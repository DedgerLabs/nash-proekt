from move import Move

def is_white_piece(p: str) -> bool:
    return p in ("o", "O")

def is_black_piece(p: str) -> bool:
    return p in ("x", "X")

def is_king(p: str) -> bool:
    return p in ("O", "X")

class CheckersRules:
    """
    Простые шашки:
    - ход по диагонали на 1 вперёд (дамка — в обе стороны)
    - взятие через 1 (в обе стороны)
    - если есть взятие — оно обязательно
    """

    def legal_moves_from(self, board, r, c, white_turn: bool):
        p = board.get(r, c)
        if p == ".":
            return []

        if white_turn and not is_white_piece(p):
            return []
        if (not white_turn) and not is_black_piece(p):
            return []

        # направления ходов
        if is_king(p):
            step_dirs = [(-1,-1), (-1,+1), (+1,-1), (+1,+1)]
        else:
            step_dirs = [(-1,-1), (-1,+1)] if white_turn else [(+1,-1), (+1,+1)]

        moves = []

        # обычные ходы на 1
        for dr, dc in step_dirs:
            r2, c2 = r + dr, c + dc
            if board.in_bounds(r2, c2) and board.get(r2, c2) == ".":
                moves.append((r2, c2))

        # взятия (в обе стороны даже у обычной шашки — проще и распространено)
        capture_dirs = [(-1,-1), (-1,+1), (+1,-1), (+1,+1)]
        caps = []
        for dr, dc in capture_dirs:
            mid_r, mid_c = r + dr, c + dc
            r2, c2 = r + 2*dr, c + 2*dc
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
            if (not white_turn) and is_white_piece(mid):
                caps.append((r2, c2))

        # если есть взятия — показываем только их (обязательное взятие)
        return caps if caps else moves

    def any_capture_exists(self, board, white_turn: bool) -> bool:
        for r in range(8):
            for c in range(8):
                p = board.get(r, c)
                if p == ".":
                    continue
                if white_turn and not is_white_piece(p):
                    continue
                if (not white_turn) and not is_black_piece(p):
                    continue
                # проверим есть ли взятия
                caps = self.legal_moves_from(board, r, c, white_turn)
                # но legal_moves_from уже может вернуть обычные ходы, поэтому проверим именно взятия:
                for (r2, c2) in caps:
                    if abs(r2 - r) == 2:
                        return True
        return False

    def validate_move(self, board, move: Move, white_turn: bool):
        r1, c1, r2, c2 = move.r1, move.c1, move.r2, move.c2
        p = board.get(r1, c1)
        if p == ".":
            return False, "На выбранной клетке нет шашки."

        if white_turn and not is_white_piece(p):
            return False, "Сейчас ход белых."
        if (not white_turn) and not is_black_piece(p):
            return False, "Сейчас ход чёрных."

        if board.get(r2, c2) != ".":
            return False, "Клетка занята."

        legal = self.legal_moves_from(board, r1, c1, white_turn)

        # обязательное взятие: если где-то на доске есть взятие, то простой ход запрещён
        must_capture = self.any_capture_exists(board, white_turn)
        is_capture = abs(r2 - r1) == 2 and abs(c2 - c1) == 2

        if must_capture and not is_capture:
            return False, "Есть взятие — нужно бить."

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
        if p == "o" and r2 == 0:
            board.set(r2, c2, "O")
        if p == "x" and r2 == 7:
            board.set(r2, c2, "X")

    def is_own_piece(self, sym: str, white_turn: bool) -> bool:
        if sym == ".":
            return False
        if white_turn:
            return sym in ("o", "O")
        else:
            return sym in ("x", "X")