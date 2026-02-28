# hex_chess_rules.py
from __future__ import annotations

from dataclasses import dataclass

# axial (q,r) rook directions (edge-adjacent)
ROOK_DIRS = [(+1, 0), (+1, -1), (0, -1), (-1, 0), (-1, +1), (0, +1)]

# diagonal directions (vertex-adjacent; stays on same colour)
# derived from cube diagonals: (2,-1,-1) etc -> axial (q=x, r=z)
BISHOP_DIRS = [(+2, -1), (+1, -2), (-1, -1), (-2, +1), (-1, +2), (+1, +1)]

# queen directions = rook + bishop
QUEEN_DIRS = ROOK_DIRS + BISHOP_DIRS


@dataclass(frozen=True)
class HexMove:
    # We store axial coordinates in fields named like Move in your project.
    r1: int  # q1
    c1: int  # r1
    r2: int  # q2
    c2: int  # r2


def is_white(sym: str) -> bool:
    return sym != "." and sym.isupper()


def is_black(sym: str) -> bool:
    return sym != "." and sym.islower()


def same_side(a: str, b: str) -> bool:
    if a == "." or b == ".":
        return False
    return (is_white(a) and is_white(b)) or (is_black(a) and is_black(b))


def slide(board, q: int, r: int, dirs, is_white_piece: bool):
    moves = []
    for dq, dr in dirs:
        q2, r2 = q + dq, r + dr
        while board.in_bounds(q2, r2):
            t = board.get(q2, r2)
            if t == ".":
                moves.append((q2, r2))
            else:
                if is_white(t) != is_white_piece:
                    moves.append((q2, r2))
                break
            q2 += dq
            r2 += dr
    return moves


def king_moves(board, q: int, r: int, is_white_piece: bool):
    moves = []
    for dq, dr in QUEEN_DIRS:
        q2, r2 = q + dq, r + dr
        if not board.in_bounds(q2, r2):
            continue
        t = board.get(q2, r2)
        if t == "." or (is_white(t) != is_white_piece):
            moves.append((q2, r2))
    return moves


def knight_moves(board, q: int, r: int, is_white_piece: bool):
    # 12 moves: 2 steps in one rook dir + 1 step in neighbor rook dir (±60°)
    vecs = []
    for i in range(6):
        vq, vr = ROOK_DIRS[i]
        wq1, wr1 = ROOK_DIRS[(i + 1) % 6]
        wq2, wr2 = ROOK_DIRS[(i - 1) % 6]
        vecs.append((2 * vq + wq1, 2 * vr + wr1))
        vecs.append((2 * vq + wq2, 2 * vr + wr2))

    moves = []
    for dq, dr in vecs:
        q2, r2 = q + dq, r + dr
        if not board.in_bounds(q2, r2):
            continue
        t = board.get(q2, r2)
        if t == "." or (is_white(t) != is_white_piece):
            moves.append((q2, r2))
    return moves


def pawn_moves_mccooey(board, q: int, r: int, is_white_piece: bool, moved_flag: bool):
    """McCooey pawns (simplified):
    - move 1 forward in the 'forward rook direction'
    - capture diagonally forward in bishop directions
    - may move 2 from initial position (except the central pawn; f-file nuance omitted here)
    Sources: https://greenchess.net/rules.php?v=mccooey
    """
    moves = []

    # Our axial orientation:
    # White goes "up" (r decreases), Black goes "down" (r increases)
    fwd = (0, -1) if is_white_piece else (0, +1)

    # 1 forward
    q1, r1 = q + fwd[0], r + fwd[1]
    if board.in_bounds(q1, r1) and board.get(q1, r1) == ".":
        moves.append((q1, r1))

        # 2 forward from start if not moved and path clear
        q2, r2 = q + 2 * fwd[0], r + 2 * fwd[1]
        if (not moved_flag) and (q != 0):  # proxy "not central pawn"
            if board.in_bounds(q2, r2) and board.get(q2, r2) == ".":
                moves.append((q2, r2))

    # captures: diagonally forward (in bishop directions)
    cap_dirs = [d for d in BISHOP_DIRS if (d[1] < 0)] if is_white_piece else [d for d in BISHOP_DIRS if (d[1] > 0)]
    cap_dirs = sorted(cap_dirs, key=lambda x: (-abs(x[1]), abs(x[0])))[:2]

    for dq, dr in cap_dirs:
        qx, rx = q + dq, r + dr
        if not board.in_bounds(qx, rx):
            continue
        t = board.get(qx, rx)
        if t != "." and (is_white(t) != is_white_piece):
            moves.append((qx, rx))

    return moves


class HexChessRulesMcCooey:
    """McCooey's Hexagonal Chess (MVP engine).

    - piece movement per hex-board rules (rook 6 dirs, bishop 6 diagonals, queen 12, king 12/1, knight 12)
      https://greenchess.net/rules.php?type=hex-board
    - pawn movement per McCooey (forward rook dir; capture bishop-forward; double-step exceptions simplified)
      https://greenchess.net/rules.php?v=mccooey
    - no castling (per McCooey)
    - basic check/checkmate detection
    """

    def __init__(self):
        self.pawn_moved = set()  # set[(q,r)] for pawns that have moved

    def is_own_piece(self, sym: str, white_turn: bool) -> bool:
        if sym == ".":
            return False
        return is_white(sym) if white_turn else is_black(sym)

    def find_king(self, board, white: bool):
        target = "K" if white else "k"
        for (q, r) in board.all_cells():
            if board.get(q, r) == target:
                return (q, r)
        return None

    def attacks(self, board, q: int, r: int):
        p = board.get(q, r)
        if p == ".":
            return []
        w = is_white(p)
        P = p.upper()

        if P == "R":
            return slide(board, q, r, ROOK_DIRS, w)
        if P == "B":
            return slide(board, q, r, BISHOP_DIRS, w)
        if P == "Q":
            return slide(board, q, r, QUEEN_DIRS, w)
        if P == "K":
            return king_moves(board, q, r, w)
        if P == "N":
            return knight_moves(board, q, r, w)
        if P == "P":
            moved = (q, r) in self.pawn_moved
            return [sq for sq in pawn_moves_mccooey(board, q, r, w, moved) if board.get(*sq) != "."]
        return []

    def square_attacked_by(self, board, attacker_white: bool, tq: int, tr: int) -> bool:
        for (q, r) in board.all_cells():
            p = board.get(q, r)
            if p == ".":
                continue
            if attacker_white and not is_white(p):
                continue
            if (not attacker_white) and not is_black(p):
                continue
            if (tq, tr) in self.attacks(board, q, r):
                return True
        return False

    def is_in_check(self, board, white_turn: bool) -> bool:
        kp = self.find_king(board, white_turn)
        if kp is None:
            return False
        kq, kr = kp
        return self.square_attacked_by(board, not white_turn, kq, kr)

    def pseudo_moves_from(self, board, q: int, r: int, white_turn: bool):
        p = board.get(q, r)
        if p == ".":
            return []
        if (is_white(p) != white_turn):
            return []

        w = is_white(p)
        P = p.upper()

        if P == "R":
            return slide(board, q, r, ROOK_DIRS, w)
        if P == "B":
            return slide(board, q, r, BISHOP_DIRS, w)
        if P == "Q":
            return slide(board, q, r, QUEEN_DIRS, w)
        if P == "K":
            return king_moves(board, q, r, w)
        if P == "N":
            return knight_moves(board, q, r, w)
        if P == "P":
            moved = (q, r) in self.pawn_moved
            return pawn_moves_mccooey(board, q, r, w, moved)
        return []

    def simulate(self, board, mv: HexMove):
        tmp = board.clone_grid()
        p = tmp[(mv.r1, mv.c1)]
        tmp[(mv.r2, mv.c2)] = p
        tmp[(mv.r1, mv.c1)] = "."
        return tmp

    def validate_move(self, board, move: HexMove, white_turn: bool):
        q1, r1, q2, r2 = move.r1, move.c1, move.r2, move.c2
        if not board.in_bounds(q1, r1) or not board.in_bounds(q2, r2):
            return False, "Вне поля"
        p = board.get(q1, r1)
        if p == ".":
            return False, "Пустая клетка"
        if is_white(p) != white_turn:
            return False, "Не ваша фигура"
        t = board.get(q2, r2)
        if same_side(p, t):
            return False, "Нельзя на свою фигуру"

        legal = self.pseudo_moves_from(board, q1, r1, white_turn)
        if (q2, r2) not in legal:
            return False, "Нелегальный ход"

        # self-check
        tmp_cells = self.simulate(board, move)
        from hex_board import HexBoard
        tmp_board = HexBoard(radius=board.radius)
        tmp_board.cells = dict(tmp_cells)
        if self.is_in_check(tmp_board, white_turn):
            return False, "Нельзя: король под шахом"

        return True, "ok"

    def apply_move(self, board, move: HexMove, white_turn: bool, _info: str):
        q1, r1, q2, r2 = move.r1, move.c1, move.r2, move.c2
        p = board.get(q1, r1)
        board.set(q2, r2, p)
        board.set(q1, r1, ".")

        if p.upper() == "P":
            self.pawn_moved.discard((q1, r1))
            self.pawn_moved.add((q2, r2))

        # promotion: simplified (edge reached)
        if p == "P" and (not board.in_bounds(q2, r2 - 1)):
            board.set(q2, r2, "Q")
        if p == "p" and (not board.in_bounds(q2, r2 + 1)):
            board.set(q2, r2, "q")

    def legal_moves_from(self, board, q: int, r: int, white_turn: bool):
        candidates = self.pseudo_moves_from(board, q, r, white_turn)
        legal = []
        for (q2, r2) in candidates:
            mv = HexMove(q, r, q2, r2)
            ok, _ = self.validate_move(board, mv, white_turn)
            if ok:
                legal.append((q2, r2))
        return legal

    def has_any_legal_move(self, board, white_turn: bool) -> bool:
        for (q, r) in board.all_cells():
            if self.is_own_piece(board.get(q, r), white_turn):
                if self.legal_moves_from(board, q, r, white_turn):
                    return True
        return False

    def game_result(self, board, white_turn: bool):
        if not self.has_any_legal_move(board, white_turn):
            if self.is_in_check(board, white_turn):
                return "black" if white_turn else "white"
            return "draw"
        return None
