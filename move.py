FILES = "abcdefgh"

class Move:
    def __init__(self, r1, c1, r2, c2):
        self.r1 = r1
        self.c1 = c1
        self.r2 = r2
        self.c2 = c2

    @staticmethod
    def parse_square(s: str):
        s = s.strip().lower()
        if len(s) != 2:
            return None
        f, rk = s[0], s[1]
        if f not in FILES or rk not in "12345678":
            return None
        c = FILES.index(f)
        r = 8 - int(rk)
        return r, c

    @staticmethod
    def parse_move_input(line: str):
        s = line.strip().lower().replace("-", " ").replace(",", " ")
        parts = [p for p in s.split() if p]

        if len(parts) == 2 and len(parts[0]) == 2 and len(parts[1]) == 2:
            return parts[0], parts[1]

        s2 = s.replace(" ", "")
        if len(s2) == 4:
            return s2[:2], s2[2:]

        return None

    @staticmethod
    def rc_to_sq(r, c):
        return FILES[c] + str(8 - r)
