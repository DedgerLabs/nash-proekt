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