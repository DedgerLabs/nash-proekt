# hex_board.py

from __future__ import annotations

HEX_DIRS = [(+1, 0), (+1, -1), (0, -1), (-1, 0), (-1, +1), (0, +1)]


class HexBoard:
    def __init__(self, radius=5):
        self.radius = radius
        self.cells = {}
        self.make_board()

    def make_board(self):
        R = self.radius
        for x in range(-R, R + 1):
            for y in range(-R, R + 1):
                z = -x - y
                if max(abs(x), abs(y), abs(z)) <= R:
                    q = x
                    r = z
                    self.cells[(q, r)] = "."

    def clone_grid(self):
        return dict(self.cells)

    def in_bounds(self, q, r):
        return (q, r) in self.cells

    def get(self, q, r):
        return self.cells.get((q, r), ".")

    def set(self, q, r, v):
        if (q, r) in self.cells:
            self.cells[(q, r)] = v

    def all_cells(self):
        return list(self.cells.keys())

    def neighbors(self, q, r):
        res = []
        for dq, dr in HEX_DIRS:
            q2, r2 = q + dq, r + dr
            if self.in_bounds(q2, r2):
                res.append((q2, r2))
        return res


def make_start_hex_test(board: "HexBoard"):
    # просто тест: чтоб увидеть фигуры на поле
    board.set(0, 0, "K")    # белый король
    board.set(1, -1, "Q")   # белый ферзь
    board.set(-1, 1, "k")   # чёрный король