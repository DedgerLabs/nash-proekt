class HexRules:
    def validate_move(self, board, move, white_turn):
        r, c = move.r1, move.c1

        if not board.in_bounds(r, c):
            return False, "Вне поля"

        if board.get(r, c) != ".":
            return False, "Клетка занята"

        return True, "place"

    def apply_move(self, board, move, white_turn, _):
        r, c = move.r1, move.c1
        board.set(r, c, "W" if white_turn else "B")

    def game_result(self, board, white_turn):
        if self.has_connection(board, True):
            return "white"
        if self.has_connection(board, False):
            return "black"
        return None



    def slide_moves(self, board, q, r, is_white, dirs):
        moves = []
        for dq, dr in dirs:
            q2, r2 = q + dq, r + dr
            while board.in_bounds(q2, r2):
                t = board.get(q2, r2)
                if t == ".":
                    moves.append((q2, r2))
                else:
                    if t.isupper() != is_white:
                        moves.append((q2, r2))
                    break
                q2 += dq
                r2 += dr
        return moves

    def king_moves(self, board, q, r, is_white):
        moves = []
        for dq, dr in self.HEX_DIRS:
            q2, r2 = q + dq, r + dr
            if not board.in_bounds(q2, r2):
                continue
            t = board.get(q2, r2)
            if t == "." or (t.isupper() != is_white):
                moves.append((q2, r2))
        return moves

    def queen_moves(self, board, q, r, is_white):
        return self.slide_moves(board, q, r, is_white, self.HEX_DIRS)

    def pawn_moves(self, board, q, r, is_white):
        moves = []
        step = -1 if is_white else +1

        # ход вперёд
        if board.in_bounds(q, r + step) and board.get(q, r + step) == ".":
            moves.append((q, r + step))

        # удары (условные 2 диагонали вперёд)
        for dq in (-1, +1):
            q2, r2 = q + dq, r + step
            if not board.in_bounds(q2, r2):
                continue
            t = board.get(q2, r2)
            if t != "." and (t.isupper() != is_white):
                moves.append((q2, r2))

        return moves

    def legal_moves_for(self, board, q, r, white_turn):
        p = board.get(q, r)
        if p == ".":
            return []

        is_white = p.isupper()
        if is_white != white_turn:
            return []

        P = p.upper()

        if P == "K":
            return self.king_moves(board, q, r, is_white)
        if P == "Q":
            return self.queen_moves(board, q, r, is_white)
        if P == "P":
            return self.pawn_moves(board, q, r, is_white)

        return []