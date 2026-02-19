class SquareBoard:
    def __init__(self):
        self.grid = self.make_start_board()

    @staticmethod
    def make_start_board():
        return [
            ["л","н","с","ф","к","с","н","л"],
            ["п","п","п","п","п","п","п","п"],
            [".",".",".",".",".",".",".","."],
            [".",".",".",".",".",".",".","."],
            [".",".",".",".",".",".",".","."],
            [".",".",".",".",".",".",".","."],
            ["П","П","П","П","П","П","П","П"],
            ["Л","К","С","Ф","K","С","К","Л"],
        ]

    def clone_grid(self):
        return [row[:] for row in self.grid]

    @staticmethod
    def in_bounds(r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def get(self, r, c):
        return self.grid[r][c]

    def set(self, r, c, v):
        self.grid[r][c] = v

    def print_board(self):
        print()
        print("      A   B   C   D   E   F   G   H")
        print("    +---+---+---+---+---+---+---+---+")
        for r in range(8):
            print(f" {8 - r}  |", end="")
            for c in range(8):
                print(f" {self.grid[r][c]} |", end="")
            print(f"  {8 - r}")
            print("    +---+---+---+---+---+---+---+---+")
        print("      A   B   C   D   E   F   G   H")
        print()
#123 12313123123123132123132131231