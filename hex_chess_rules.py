# hex_chess_rules.py
from __future__ import annotations
from dataclasses import dataclass

from hex_board import HEX_DIRS, HexBoard

# Rook directions (edge-adjacent)
ROOK_DIRS = HEX_DIRS

# Bishop directions (vertex-diagonals) in axial (q, r)
# Common axial diagonals for Gliński/McCooey style movement
BISHOP_DIRS = [(1, -2), (2, -1), (1, 1), (-1, 2), (-2, 1), (-1, -1)]

# King can move 1 rook-step OR 1 bishop-step (diagonal neighbor across a vertex)
KING_DIRS = ROOK_DIRS + BISHOP_DIRS


@dataclass(frozen=True)
class HexMove:
    q1: int
    r1: int
    q2: int
    r2: int


class HexChessRulesMcCooey:
    """
    2-player McCooey hex chess:
    - R/Q/B move like in Gliński (rook: 6 edge dirs, bishop: 6 vertex-diagonal dirs)
    - King: 12 moves (6 edge + 6 vertex-diagonal)
    - Knight: 12 moves = all hex-distance-2 cells excluding 6 straight (2*rook_dir)
    - Pawn: forward 1; captures on two edge-neighbors at 60° to forward (McCooey)  :contentReference[oaicite:1]{index=1}
    """

    def is_own_piece(self, sym: str, white_turn: bool) -> bool:
        if sym == ".":
            return False
        return sym.isupper() if white_turn else sym.islower()

    def _is_enemy(self, sym: str, white: bool) -> bool:
        return sym != "." and (sym.isupper() != white)

    def _slide_moves(self, board: HexBoard, q: int, r: int, white: bool, dirs):
        res = []
        for dq, dr in dirs:
            q2, r2 = q + dq, r + dr
            while board.in_bounds(q2, r2):
                t = board.get(q2, r2)
                if t == ".":
                    res.append((q2, r2))
                else:
                    if self._is_enemy(t, white):
                        res.append((q2, r2))
                    break
                q2 += dq
                r2 += dr
        return res

    def _king_moves(self, board: HexBoard, q: int, r: int, white: bool):
        res = []
        for dq, dr in KING_DIRS:
            q2, r2 = q + dq, r + dr
            if not board.in_bounds(q2, r2):
                continue
            t = board.get(q2, r2)
            if t == "." or self._is_enemy(t, white):
                res.append((q2, r2))
        return res

    def _knight_dirs(self):
        # Generate all cells reachable by 2 king-steps (edge-neighbors),
        # then remove the 6 straight ones (2*rook_dir). This yields 12.
        two_steps = set()
        for dq1, dr1 in ROOK_DIRS:
            for dq2, dr2 in ROOK_DIRS:
                dq, dr = dq1 + dq2, dr1 + dr2
                # ignore cancelling steps (distance 0 or 1)
                if (dq, dr) == (0, 0):
                    continue
                two_steps.add((dq, dr))

        straight = {(2 * dq, 2 * dr) for dq, dr in ROOK_DIRS}
        # Keep distance-2 but not straight.
        # On axial, the 12 “L” moves are exactly these.
        return sorted(two_steps - straight)

    def _knight_moves(self, board: HexBoard, q: int, r: int, white: bool):
        res = []
        for dq, dr in self._knight_dirs():
            q2, r2 = q + dq, r + dr
            if not board.in_bounds(q2, r2):
                continue
            t = board.get(q2, r2)
            if t == "." or self._is_enemy(t, white):
                res.append((q2, r2))
        return res

    def _pawn_dirs(self, white: bool):
        # Choose "vertical" forward as (0,-1) for White (up), (0,+1) for Black (down)
        if white:
            fwd = (0, -1)
            caps = [(-1, 0), (1, -1)]   # 60° to forward, edge-neighbors
        else:
            fwd = (0, 1)
            caps = [(1, 0), (-1, 1)]
        return fwd, caps

    def _pawn_moves(self, board: HexBoard, q: int, r: int, white: bool):
        res = []
        fwd, caps = self._pawn_dirs(white)

        # forward 1
        q1, r1 = q + fwd[0], r + fwd[1]
        if board.in_bounds(q1, r1) and board.get(q1, r1) == ".":
            res.append((q1, r1))

            # optional: initial double step (McCooey allows except central pawn) :contentReference[oaicite:2]{index=2}
            # We keep it simple: allow double step only from the starting band r=3 for white, r=-3 for black,
            # and forbid for "central" file q==0 (analogue of f-file).
            start_r = 3 if white else -3
            if r == start_r and q != 0:
                q2, r2 = q + 2 * fwd[0], r + 2 * fwd[1]
                if board.in_bounds(q2, r2) and board.get(q2, r2) == ".":
                    res.append((q2, r2))

        # captures (edge-neighbors)
        for dq, dr in caps:
            qc, rc = q + dq, r + dr
            if not board.in_bounds(qc, rc):
                continue
            t = board.get(qc, rc)
            if t != "." and self._is_enemy(t, white):
                res.append((qc, rc))

        return res

    def legal_moves_from(self, board: HexBoard, q: int, r: int, white_turn: bool):
        p = board.get(q, r)
        if p == ".":
            return []

        white = p.isupper()
        if white != white_turn:
            return []

        P = p.upper()
        if P == "P":
            return self._pawn_moves(board, q, r, white)
        if P == "R":
            return self._slide_moves(board, q, r, white, ROOK_DIRS)
        if P == "B":
            return self._slide_moves(board, q, r, white, BISHOP_DIRS)
        if P == "Q":
            return self._slide_moves(board, q, r, white, ROOK_DIRS + BISHOP_DIRS)
        if P == "N":
            return self._knight_moves(board, q, r, white)
        if P == "K":
            return self._king_moves(board, q, r, white)
        return []

    def _find_king(self, board: HexBoard, white: bool):
        target = "K" if white else "k"
        for q, r in board.all_cells():
            if board.get(q, r) == target:
                return (q, r)
        return None

    def _attacks_square(self, board: HexBoard, from_q: int, from_r: int, to_q: int, to_r: int):
        p = board.get(from_q, from_r)
        if p == ".":
            return False
        white = p.isupper()
        P = p.upper()

        if P == "P":
            _, caps = self._pawn_dirs(white)
            return any((from_q + dq, from_r + dr) == (to_q, to_r) for dq, dr in caps)

        # for others we can reuse pseudo moves
        return (to_q, to_r) in self.legal_moves_from(board, from_q, from_r, white)

    def in_check(self, board: HexBoard, white: bool) -> bool:
        kpos = self._find_king(board, white)
        if not kpos:
            return True  # king missing = treated as "in check"/lost
        kq, kr = kpos

        for q, r in board.all_cells():
            s = board.get(q, r)
            if s == ".":
                continue
            if s.isupper() == white:
                continue
            if self._attacks_square(board, q, r, kq, kr):
                return True
        return False

    def validate_move(self, board: HexBoard, mv: HexMove, white_turn: bool):
        q1, r1, q2, r2 = mv.q1, mv.r1, mv.q2, mv.r2

        if not board.in_bounds(q1, r1) or not board.in_bounds(q2, r2):
            return False, "Вне поля"

        piece = board.get(q1, r1)
        if piece == ".":
            return False, "Нет фигуры"

        if not self.is_own_piece(piece, white_turn):
            return False, "Не твоя фигура"

        dest = board.get(q2, r2)
        if dest != "." and self.is_own_piece(dest, white_turn):
            return False, "Клетка занята своей фигурой"

        legal = self.legal_moves_from(board, q1, r1, white_turn)
        if (q2, r2) not in legal:
            return False, "Нелегальный ход"

        # check safety: don't leave own king in check
        snap = board.clone_grid()
        board.set(q2, r2, piece)
        board.set(q1, r1, ".")
        ok = not self.in_check(board, white_turn)
        board.cells = snap

        if not ok:
            return False, "Нельзя под шах"

        return True, "move"

    def apply_move(self, board: HexBoard, mv: HexMove, white_turn: bool, _msg: str):
        piece = board.get(mv.q1, mv.r1)
        board.set(mv.q2, mv.r2, piece)
        board.set(mv.q1, mv.r1, ".")

        # promotion (simple): if pawn reaches far edge (any cell on opposite rim)
        if piece == "P" and mv.r2 <= -4:
            board.set(mv.q2, mv.r2, "Q")
        if piece == "p" and mv.r2 >= 4:
            board.set(mv.q2, mv.r2, "q")

    def game_result(self, board: HexBoard, white_turn: bool):
        # Very simple: if side to move has no king -> loses
        if self._find_king(board, True) is None:
            return "black"
        if self._find_king(board, False) is None:
            return "white"

        # checkmate / stalemate (simplified):
        # if no legal moves for side to move -> if in check => mate else draw
        has_move = False
        for q, r in board.all_cells():
            if not self.is_own_piece(board.get(q, r), white_turn):
                continue
            for (q2, r2) in self.legal_moves_from(board, q, r, white_turn):
                mv = HexMove(q, r, q2, r2)
                ok, _ = self.validate_move(board, mv, white_turn)
                if ok:
                    has_move = True
                    break
            if has_move:
                break

        if has_move:
            return None

        if self.in_check(board, white_turn):
            return "black" if white_turn else "white"
        return "draw"