from move import Move


def is_white_piece(p: str) -> bool:
    return p in ("o", "O")


def is_black_piece(p: str) -> bool:
    return p in ("x", "X")


def is_king(p: str) -> bool:
    return p in ("O", "X")


class CheckersRules:
    """
    Простые шашки (MVP):
    - ход по диагонали на 1 вперёд (дамка — в обе стороны)
    - взятие через 1 (в обе стороны)  ← как у тебя было
    - если есть взятие — оно обязательно
    - если после взятия можно бить ещё — серия ОБЯЗАТЕЛЬНА и ход не переходит
    """

    def __init__(self):
        # Если не None: сейчас продолжается серия взятий, ходить можно только этой шашкой
        self.forced_piece: tuple[int, int] | None = None  # (r, c)

    # -------------------------
    # Внутренние хелперы
    # -------------------------

    def _capture_landing_squares(self, board, r: int, c: int, white_turn: bool):
        """Куда может приземлиться шашка при взятии (только landing клетки)."""
        p = board.get(r, c)
        if p == ".":
            return []

        # Берём 4 диагонали для взятия (как у тебя)
        capture_dirs = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
        caps = []

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

            # mid должен быть врагом
            if white_turn and is_black_piece(mid):
                caps.append((r2, c2))
            elif (not white_turn) and is_white_piece(mid):
                caps.append((r2, c2))

        return caps

    def any_capture_exists(self, board, white_turn: bool) -> bool:
        """
        Проверка обязательного взятия.
        Если forced_piece активна — проверяем только её (потому что серия обязана продолжаться).
        """
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

        # Если идёт серия взятий — ходить можно только этой шашкой
        if self.forced_piece is not None and (r, c) != self.forced_piece:
            return []

        # Сначала считаем взятия
        caps = self._capture_landing_squares(board, r, c, white_turn)

        # Если где-то есть взятие (или forced_piece требует), обычные ходы запрещены
        must_capture = self.any_capture_exists(board, white_turn)
        if must_capture:
            return caps  # даже если caps пусты, это означает "этой шашкой ходов нет"

        # Иначе — обычные ходы
        if is_king(p):
            step_dirs = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
        else:
            step_dirs = [(-1, -1), (-1, +1)] if white_turn else [(+1, -1), (+1, +1)]

        moves = []
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

        # Если идёт серия — нельзя выбирать другую шашку
        if self.forced_piece is not None and (r1, c1) != self.forced_piece:
            return False, "Нужно продолжить взятие той же шашкой."

        if board.get(r2, c2) != ".":
            return False, "Клетка занята."

        is_capture = abs(r2 - r1) == 2 and abs(c2 - c1) == 2

        # обязательное взятие: если есть взятие, простой ход запрещён
        must_capture = self.any_capture_exists(board, white_turn)
        if must_capture and not is_capture:
            return False, "Есть взятие — нужно бить."

        # если forced_piece активна — ход обязан быть взятием
        if self.forced_piece is not None and not is_capture:
            return False, "Нужно продолжить взятие (обычный ход запрещён)."

        legal = self.legal_moves_from(board, r1, c1, white_turn)
        if (r2, c2) not in legal:
            return False, "Нелегальный ход."

        return True, "capture" if is_capture else "move"

    def apply_move(self, board, move: Move, white_turn: bool, move_type: str):
        r1, c1, r2, c2 = move.r1, move.c1, move.r2, move.c2
        p = board.get(r1, c1)

        board.set(r2, c2, p)
        board.set(r1, c1, ".")

        # если это взятие — снимаем побитую шашку
        if move_type == "capture":
            mid_r = (r1 + r2) // 2
            mid_c = (c1 + c2) // 2
            board.set(mid_r, mid_c, ".")

        # превращение в дамку
        if p == "o" and r2 == 7:
            board.set(r2, c2, "O")

        if p == "x" and r2 == 0:
            board.set(r2, c2, "X")

        # ЛОГИКА СЕРИИ ВЗЯТИЙ:
        if move_type == "capture":
            # проверяем, может ли эта же шашка бить дальше
            more_caps = self._capture_landing_squares(board, r2, c2, white_turn)
            if more_caps:
                # серия продолжается — ход остаётся у игрока, и ходить можно только этой шашкой
                self.forced_piece = (r2, c2)
            else:
                # серия закончилась — сбрасываем
                self.forced_piece = None
        else:
            # обычный ход — сброс
            self.forced_piece = None

    # -------------------------
    # Остальные методы (как у тебя)
    # -------------------------

    def is_own_piece(self, sym: str, white_turn: bool) -> bool:
        if sym == ".":
            return False
        if white_turn:
            return sym in ("o", "O")
        else:
            return sym in ("x", "X")

    def threatened_squares(self, board, defender_white: bool):
        """
        Клетки с фигурами стороны defender_white, которые противник может взять СЕЙЧАС.
        Возвращаем set[(r,c)] именно клеток с фигурами (жертвы).
        """
        victims = set()
        attacker_white = not defender_white

        for r in range(8):
            for c in range(8):
                p = board.get(r, c)
                if p == ".":
                    continue

                # берём только атакующую сторону
                if attacker_white and p not in ("o", "O"):
                    continue
                if (not attacker_white) and p not in ("x", "X"):
                    continue

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

        # если серия — проверяем только forced_piece
        if self.forced_piece is not None:
            r, c = self.forced_piece
            if board.get(r, c) in own:
                return len(self.legal_moves_from(board, r, c, white_turn)) > 0
            return False

        for r in range(8):
            for c in range(8):
                if board.get(r, c) in own:
                    moves = self.legal_moves_from(board, r, c, white_turn)
                    if moves:
                        return True
        return False

    def game_result(self, board, white_turn: bool):
        """
        Возвращает:
          None — игра продолжается
          "white" — выиграли белые
          "black" — выиграли чёрные
        """
        if not self.has_pieces(board, white_turn):
            return "black" if white_turn else "white"

        if not self.has_any_legal_move(board, white_turn):
            return "black" if white_turn else "white"

        return None