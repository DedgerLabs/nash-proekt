from move import Move


def is_white_piece(p: str) -> bool:
    return p in ("o", "O")


def is_black_piece(p: str) -> bool:
    return p in ("x", "X")


def is_king(p: str) -> bool:
    return p in ("O", "X")


class CheckersRules:
    """
    Шашки:
    - обычная шашка ходит на 1 по диагонали вперёд
    - обычная шашка бьёт через 1 клетку
    - дамка ходит по диагонали на любое расстояние
    - дамка бьёт по диагонали: через РОВНО одну вражескую шашку,
      приземлиться можно на любую пустую клетку дальше по этой диагонали
    - если есть взятие — оно обязательно
    - если после взятия можно бить ещё — серия обязательна
    """

    def __init__(self):
        self.forced_piece: tuple[int, int] | None = None

    # -------------------------
    # Внутренние хелперы
    # -------------------------

    def _landing_and_victim_for_king_capture(self, board, r1: int, c1: int, r2: int, c2: int, white_turn: bool):
        """
        Проверка дальнего взятия дамкой.
        Если ход (r1,c1)->(r2,c2) является корректным взятием дамкой,
        возвращает координаты побитой шашки (vr, vc).
        Иначе возвращает None.
        """
        if abs(r2 - r1) != abs(c2 - c1):
            return None

        dr = 1 if r2 > r1 else -1
        dc = 1 if c2 > c1 else -1

        cr, cc = r1 + dr, c1 + dc
        victim = None

        while cr != r2 and cc != c2:
            cell = board.get(cr, cc)

            if cell != ".":
                # своя фигура на пути — нельзя
                if white_turn and is_white_piece(cell):
                    return None
                if (not white_turn) and is_black_piece(cell):
                    return None

                # вторая чужая фигура на пути — нельзя
                if victim is not None:
                    return None

                victim = (cr, cc)

            cr += dr
            cc += dc

        # у дамки для взятия на пути должна быть ровно одна вражеская шашка
        return victim

    def _capture_landing_squares(self, board, r: int, c: int, white_turn: bool):
        """
        Куда может приземлиться фигура при взятии.
        Для обычной шашки: через 1.
        Для дамки: на любую пустую клетку за одной вражеской фигурой по диагонали.
        """
        p = board.get(r, c)
        if p == ".":
            return []

        caps = []

        if is_king(p):
            for dr, dc in [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]:
                seen_enemy = False
                cr, cc = r + dr, c + dc

                while board.in_bounds(cr, cc):
                    cell = board.get(cr, cc)

                    if cell == ".":
                        if seen_enemy:
                            caps.append((cr, cc))
                        cr += dr
                        cc += dc
                        continue

                    # своя фигура блокирует луч
                    if white_turn and is_white_piece(cell):
                        break
                    if (not white_turn) and is_black_piece(cell):
                        break

                    # чужая фигура
                    if not seen_enemy:
                        seen_enemy = True
                        cr += dr
                        cc += dc
                        continue
                    else:
                        # вторая фигура подряд — дальше бить нельзя
                        break

            return caps

        # обычная шашка
        capture_dirs = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]

        for dr, dc in capture_dirs:
            mid_r, mid_c = r + dr, c + dc
            r2, c2 = r + 2 * dr, c + 2 * dc

            if not board.in_bounds(r2, c2):
                continue
            if board.get(r2, c2) != ".":
                continue

            mid = board.get(mid_r, mid_c)
            if mid == ".":
                continue

            if white_turn and is_black_piece(mid):
                caps.append((r2, c2))
            elif (not white_turn) and is_white_piece(mid):
                caps.append((r2, c2))

        return caps

    def any_capture_exists(self, board, white_turn: bool) -> bool:
        if self.forced_piece is not None:
            r, c = self.forced_piece
            return len(self._capture_landing_squares(board, r, c, white_turn)) > 0

        for r in range(8):
            for c in range(8):
                p = board.get(r, c)
                if p == ".":
                    continue
                if white_turn and not is_white_piece(p):
                    continue
                if (not white_turn) and not is_black_piece(p):
                    continue

                if self._capture_landing_squares(board, r, c, white_turn):
                    return True

        return False

    # -------------------------
    # Основные методы правил
    # -------------------------

    def legal_moves_from(self, board, r, c, white_turn: bool):
        p = board.get(r, c)
        if p == ".":
            return []

        if white_turn and not is_white_piece(p):
            return []
        if (not white_turn) and not is_black_piece(p):
            return []

        if self.forced_piece is not None and (r, c) != self.forced_piece:
            return []

        # Сначала взятия
        caps = self._capture_landing_squares(board, r, c, white_turn)
        must_capture = self.any_capture_exists(board, white_turn)
        if must_capture:
            return caps

        moves = []

        if is_king(p):
            # дальнобойная дамка: любые пустые клетки по диагонали
            for dr, dc in [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]:
                r2, c2 = r + dr, c + dc
                while board.in_bounds(r2, c2) and board.get(r2, c2) == ".":
                    moves.append((r2, c2))
                    r2 += dr
                    c2 += dc
        else:
            step_dirs = [(-1, -1), (-1, +1)] if white_turn else [(+1, -1), (+1, +1)]
            for dr, dc in step_dirs:
                r2, c2 = r + dr, c + dc
                if board.in_bounds(r2, c2) and board.get(r2, c2) == ".":
                    moves.append((r2, c2))

        return moves

    def validate_move(self, board, move: Move, white_turn: bool):
        r1, c1, r2, c2 = move.r1, move.c1, move.r2, move.c2
        p = board.get(r1, c1)

        if p == ".":
            return False, "На выбранной клетке нет шашки."

        if white_turn and not is_white_piece(p):
            return False, "Сейчас ход белых."
        if (not white_turn) and not is_black_piece(p):
            return False, "Сейчас ход чёрных."

        if self.forced_piece is not None and (r1, c1) != self.forced_piece:
            return False, "Нужно продолжить взятие той же шашкой."

        if not board.in_bounds(r2, c2):
            return False, "Клетка вне доски."

        if board.get(r2, c2) != ".":
            return False, "Клетка занята."

        legal = self.legal_moves_from(board, r1, c1, white_turn)
        if (r2, c2) not in legal:
            return False, "Нелегальный ход."

        # Определяем тип хода
        move_type = "move"

        if is_king(p):
            victim = self._landing_and_victim_for_king_capture(board, r1, c1, r2, c2, white_turn)
            if victim is not None:
                move_type = "capture"
        else:
            if abs(r2 - r1) == 2 and abs(c2 - c1) == 2:
                move_type = "capture"

        must_capture = self.any_capture_exists(board, white_turn)
        if must_capture and move_type != "capture":
            return False, "Есть взятие — нужно бить."

        if self.forced_piece is not None and move_type != "capture":
            return False, "Нужно продолжить взятие (обычный ход запрещён)."

        return True, move_type

    def apply_move(self, board, move: Move, white_turn: bool, move_type: str):
        r1, c1, r2, c2 = move.r1, move.c1, move.r2, move.c2
        p = board.get(r1, c1)

        board.set(r2, c2, p)
        board.set(r1, c1, ".")

        if move_type == "capture":
            if is_king(p):
                victim = self._landing_and_victim_for_king_capture(board, r1, c1, r2, c2, white_turn)
                if victim is not None:
                    vr, vc = victim
                    board.set(vr, vc, ".")
            else:
                mid_r = (r1 + r2) // 2
                mid_c = (c1 + c2) // 2
                board.set(mid_r, mid_c, ".")

        # превращение в дамку
        if p == "o" and r2 == 0:
            board.set(r2, c2, "O")

        if p == "x" and r2 == 7:
            board.set(r2, c2, "X")

        if move_type == "capture":
            more_caps = self._capture_landing_squares(board, r2, c2, white_turn)
            if more_caps:
                self.forced_piece = (r2, c2)
            else:
                self.forced_piece = None
        else:
            self.forced_piece = None

    # -------------------------
    # Остальные методы
    # -------------------------

    def is_own_piece(self, sym: str, white_turn: bool) -> bool:
        if sym == ".":
            return False
        if white_turn:
            return sym in ("o", "O")
        return sym in ("x", "X")

    def threatened_squares(self, board, defender_white: bool):
        """
        Клетки с фигурами стороны defender_white, которые противник может взять сейчас.
        """
        victims = set()
        attacker_white = not defender_white

        for r in range(8):
            for c in range(8):
                p = board.get(r, c)
                if p == ".":
                    continue

                if attacker_white and p not in ("o", "O"):
                    continue
                if (not attacker_white) and p not in ("x", "X"):
                    continue

                if is_king(p):
                    for dr, dc in [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]:
                        seen_enemy = None
                        cr, cc = r + dr, c + dc

                        while board.in_bounds(cr, cc):
                            cell = board.get(cr, cc)

                            if cell == ".":
                                if seen_enemy is not None:
                                    victims.add(seen_enemy)
                                cr += dr
                                cc += dc
                                continue

                            if attacker_white and cell in ("o", "O"):
                                break
                            if (not attacker_white) and cell in ("x", "X"):
                                break

                            if seen_enemy is None:
                                seen_enemy = (cr, cc)
                                cr += dr
                                cc += dc
                            else:
                                break
                else:
                    for dr, dc in [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]:
                        mid_r, mid_c = r + dr, c + dc
                        r2, c2 = r + 2 * dr, c + 2 * dc

                        if not board.in_bounds(r2, c2):
                            continue
                        if board.get(r2, c2) != ".":
                            continue

                        mid = board.get(mid_r, mid_c)
                        if mid == ".":
                            continue

                        if defender_white and mid in ("o", "O"):
                            victims.add((mid_r, mid_c))
                        if (not defender_white) and mid in ("x", "X"):
                            victims.add((mid_r, mid_c))

        return victims

    def has_pieces(self, board, white: bool) -> bool:
        targets = ("o", "O") if white else ("x", "X")
        for r in range(8):
            for c in range(8):
                if board.get(r, c) in targets:
                    return True
        return False

    def has_any_legal_move(self, board, white_turn: bool) -> bool:
        own = ("o", "O") if white_turn else ("x", "X")

        if self.forced_piece is not None:
            r, c = self.forced_piece
            if board.get(r, c) in own:
                return len(self.legal_moves_from(board, r, c, white_turn)) > 0
            return False

        for r in range(8):
            for c in range(8):
                if board.get(r, c) in own:
                    if self.legal_moves_from(board, r, c, white_turn):
                        return True
        return False

    def game_result(self, board, white_turn: bool):
        if not self.has_pieces(board, white_turn):
            return "black" if white_turn else "white"

        if not self.has_any_legal_move(board, white_turn):
            return "black" if white_turn else "white"

        return None