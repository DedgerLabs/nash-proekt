class HexBoard:
    def __init__(self, size=6):
        self.size = size
        self.grid = [["." for _ in range(size)] for _ in range(size)]

    def get(self, r, c):
        return self.grid[r][c]

    def set(self, r, c, val):
        self.grid[r][c] = val

    def in_bounds(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size