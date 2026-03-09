# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from enum import Enum


class Color(Enum):
    WHITE = "white"
    BLACK = "black"

    def opposite(self):
        return Color.BLACK if self == Color.WHITE else Color.WHITE


class HexCoordinate:
    def __init__(self, q: int, r: int):
        self.q = q
        self.r = r
        self.s = -q - r

    def __eq__(self, other):
        if not isinstance(other, HexCoordinate):
            return False
        return self.q == other.q and self.r == other.r

    def __hash__(self):
        return hash((self.q, self.r))

    def __repr__(self):
        return f"({self.q:+d},{self.r:+d})"

    def neighbors(self) -> List['HexCoordinate']:
        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        return [HexCoordinate(self.q + dq, self.r + dr) for dq, dr in directions]


class HexPiece(ABC):
    def __init__(self, color: Color, hex_coord: HexCoordinate):
        self.color = color
        self.hex_coord = hex_coord
        self.has_moved = False

    @abstractmethod
    def get_hex_moves(self, board: 'HexBoard') -> List['HexCoordinate']:
        pass

    @abstractmethod
    def get_symbol(self) -> str:
        pass


class HexPawn(HexPiece):
    SYMBOLS = {
        ('HexPawn', Color.WHITE): '♙',
        ('HexPawn', Color.BLACK): '♟'
    }

    def get_symbol(self) -> str:
        return self.SYMBOLS.get((self.__class__.__name__, self.color), 'P')

    def _capture_dirs(self) -> List[Tuple[int, int]]:
        return [(1, -1), (-1, 0)] if self.color == Color.WHITE else [(1, 0), (-1, 1)]

    def get_attack_hexes(self, board: 'HexBoard') -> List['HexCoordinate']:
        attacks = []
        for dq, dr in self._capture_dirs():
            c = HexCoordinate(self.hex_coord.q + dq, self.hex_coord.r + dr)
            if board.is_valid_hex(c):
                attacks.append(c)
        return attacks

    def get_hex_moves(self, board: 'HexBoard') -> List['HexCoordinate']:
        moves = []
        direction = -1 if self.color == Color.WHITE else 1

        forward_hex = HexCoordinate(self.hex_coord.q, self.hex_coord.r + direction)
        if board.is_valid_hex(forward_hex) and board.get_piece_at_hex(forward_hex) is None:
            moves.append(forward_hex)

            if not self.has_moved:
                double_hex = HexCoordinate(self.hex_coord.q, self.hex_coord.r + 2 * direction)
                if board.is_valid_hex(double_hex) and board.get_piece_at_hex(double_hex) is None:
                    moves.append(double_hex)

        for capture_hex in self.get_attack_hexes(board):
            target = board.get_piece_at_hex(capture_hex)
            if target and target.color != self.color:
                moves.append(capture_hex)

        return moves


class HexKnight(HexPiece):
    SYMBOLS = {
        ('HexKnight', Color.WHITE): '♘',
        ('HexKnight', Color.BLACK): '♞'
    }

    def get_symbol(self) -> str:
        return self.SYMBOLS.get((self.__class__.__name__, self.color), 'N')

    def get_hex_moves(self, board: 'HexBoard') -> List['HexCoordinate']:
        moves = []
        seen = set()
        ortho_dirs = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]

        for dq, dr in ortho_dirs:
            mid_hex = HexCoordinate(self.hex_coord.q + dq, self.hex_coord.r + dr)
            target_hex = HexCoordinate(mid_hex.q + dq, mid_hex.r + dr)

            for side_dq, side_dr in self._get_perpendicular(dq, dr):
                knight_hex = HexCoordinate(target_hex.q + side_dq, target_hex.r + side_dr)
                if not board.is_valid_hex(knight_hex):
                    continue
                if knight_hex in seen:
                    continue
                target_piece = board.get_piece_at_hex(knight_hex)
                if target_piece is None or target_piece.color != self.color:
                    moves.append(knight_hex)
                    seen.add(knight_hex)

        return moves

    def _get_perpendicular(self, dq: int, dr: int) -> List[Tuple[int, int]]:
        all_dirs = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        current = (dq, dr)
        opposite = (-dq, -dr)
        return [d for d in all_dirs if d != current and d != opposite]


class HexBishop(HexPiece):
    SYMBOLS = {
        ('HexBishop', Color.WHITE): '♗',
        ('HexBishop', Color.BLACK): '♝'
    }

    def get_symbol(self) -> str:
        return self.SYMBOLS.get((self.__class__.__name__, self.color), 'B')

    def get_hex_moves(self, board: 'HexBoard') -> List['HexCoordinate']:
        moves = []
        diag_dirs = [(2, -1), (1, -2), (-1, -1), (-2, 1), (-1, 2), (1, 1)]

        for dq, dr in diag_dirs:
            for distance in range(1, 11):
                target_hex = HexCoordinate(
                    self.hex_coord.q + dq * distance,
                    self.hex_coord.r + dr * distance
                )

                if not board.is_valid_hex(target_hex):
                    break

                target_piece = board.get_piece_at_hex(target_hex)

                if target_piece is None:
                    moves.append(target_hex)
                else:
                    if target_piece.color != self.color:
                        moves.append(target_hex)
                    break

        return moves


class HexRook(HexPiece):
    SYMBOLS = {
        ('HexRook', Color.WHITE): '♖',
        ('HexRook', Color.BLACK): '♜'
    }

    def get_symbol(self) -> str:
        return self.SYMBOLS.get((self.__class__.__name__, self.color), 'R')

    def get_hex_moves(self, board: 'HexBoard') -> List['HexCoordinate']:
        moves = []
        ortho_dirs = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]

        for dq, dr in ortho_dirs:
            for distance in range(1, 11):
                target_hex = HexCoordinate(
                    self.hex_coord.q + dq * distance,
                    self.hex_coord.r + dr * distance
                )

                if not board.is_valid_hex(target_hex):
                    break

                target_piece = board.get_piece_at_hex(target_hex)

                if target_piece is None:
                    moves.append(target_hex)
                else:
                    if target_piece.color != self.color:
                        moves.append(target_hex)
                    break

        return moves


class HexQueen(HexPiece):
    SYMBOLS = {
        ('HexQueen', Color.WHITE): '♕',
        ('HexQueen', Color.BLACK): '♛'
    }

    def get_symbol(self) -> str:
        return self.SYMBOLS.get((self.__class__.__name__, self.color), 'Q')

    def get_hex_moves(self, board: 'HexBoard') -> List['HexCoordinate']:
        moves = []
        all_dirs = [
            (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1),
            (2, -1), (1, -2), (-1, -1), (-2, 1), (-1, 2), (1, 1)
        ]

        for dq, dr in all_dirs:
            for distance in range(1, 11):
                target_hex = HexCoordinate(
                    self.hex_coord.q + dq * distance,
                    self.hex_coord.r + dr * distance
                )

                if not board.is_valid_hex(target_hex):
                    break

                target_piece = board.get_piece_at_hex(target_hex)

                if target_piece is None:
                    moves.append(target_hex)
                else:
                    if target_piece.color != self.color:
                        moves.append(target_hex)
                    break

        return moves


class HexKing(HexPiece):
    SYMBOLS = {
        ('HexKing', Color.WHITE): '♔',
        ('HexKing', Color.BLACK): '♚'
    }

    _KING_DIRS = [
        (1, 0), (1, -1), (0, -1),
        (-1, 0), (-1, 1), (0, 1),
        (2, -1), (1, -2), (-1, -1),
        (-2, 1), (-1, 2), (1, 1)
    ]

    def get_symbol(self) -> str:
        return self.SYMBOLS.get((self.__class__.__name__, self.color), 'K')

    def get_hex_moves(self, board: 'HexBoard') -> List['HexCoordinate']:
        moves = []
        for dq, dr in self._KING_DIRS:
            target_hex = HexCoordinate(self.hex_coord.q + dq, self.hex_coord.r + dr)
            if board.is_valid_hex(target_hex):
                target_piece = board.get_piece_at_hex(target_hex)
                if target_piece is None or target_piece.color != self.color:
                    moves.append(target_hex)
        return moves


class HexMove:
    def __init__(self, from_hex: HexCoordinate, to_hex: HexCoordinate,
                 captured_piece: Optional[HexPiece] = None, promoted: bool = False):
        self.from_hex = from_hex
        self.to_hex = to_hex
        self.captured_piece = captured_piece
        self.promoted = promoted


class HexBoard:
    BOARD_SIZE = 5

    def __init__(self):
        self.hexes = {}
        self.move_history = []
        self._init_valid_hexes()
        self._create_labels()
        self._setup_initial_position()

    def _init_valid_hexes(self):
        self.valid_hexes = set()
        for q in range(-self.BOARD_SIZE, self.BOARD_SIZE + 1):
            r1 = max(-self.BOARD_SIZE, -q - self.BOARD_SIZE)
            r2 = min(self.BOARD_SIZE, -q + self.BOARD_SIZE)
            for r in range(r1, r2 + 1):
                self.valid_hexes.add(HexCoordinate(q, r))

    def _create_labels(self):
        self.hex_labels = {}
        self.label_to_hex = {}
        cols = 'abcdefghijk'
        for q in range(-5, 6):
            col_letter = cols[q + 5]
            for r in range(-5, 6):
                hex_coord = HexCoordinate(q, r)
                if hex_coord in self.valid_hexes:
                    row_num = 11 - (r + 5)
                    label = f"{col_letter}{row_num}"
                    self.hex_labels[hex_coord] = label
                    self.label_to_hex[label] = hex_coord

    def is_valid_hex(self, hex_coord: HexCoordinate) -> bool:
        return hex_coord in self.valid_hexes

    def get_piece_at_hex(self, hex_coord: HexCoordinate) -> Optional[HexPiece]:
        return self.hexes.get(hex_coord)

    def set_piece_at_hex(self, hex_coord: HexCoordinate, piece: Optional[HexPiece]):
        if piece:
            self.hexes[hex_coord] = piece
            piece.hex_coord = hex_coord
        elif hex_coord in self.hexes:
            del self.hexes[hex_coord]

    def _setup_initial_position(self):
        self.set_piece_at_hex(HexCoordinate(-5, 5), HexRook(Color.WHITE, HexCoordinate(-5, 5)))
        self.set_piece_at_hex(HexCoordinate(-4, 5), HexKnight(Color.WHITE, HexCoordinate(-4, 5)))
        self.set_piece_at_hex(HexCoordinate(-3, 5), HexBishop(Color.WHITE, HexCoordinate(-3, 5)))
        self.set_piece_at_hex(HexCoordinate(-2, 5), HexQueen(Color.WHITE, HexCoordinate(-2, 5)))
        self.set_piece_at_hex(HexCoordinate(-1, 5), HexKing(Color.WHITE, HexCoordinate(-1, 5)))
        self.set_piece_at_hex(HexCoordinate(0, 5), HexBishop(Color.WHITE, HexCoordinate(0, 5)))
        self.set_piece_at_hex(HexCoordinate(1, 4), HexBishop(Color.WHITE, HexCoordinate(1, 4)))
        self.set_piece_at_hex(HexCoordinate(2, 3), HexKnight(Color.WHITE, HexCoordinate(2, 3)))
        self.set_piece_at_hex(HexCoordinate(3, 2), HexRook(Color.WHITE, HexCoordinate(3, 2)))

        pawn_positions = [
            HexCoordinate(-4, 4), HexCoordinate(-3, 4), HexCoordinate(-2, 4),
            HexCoordinate(-1, 4), HexCoordinate(0, 4), HexCoordinate(1, 3),
            HexCoordinate(2, 2), HexCoordinate(3, 1), HexCoordinate(4, 0)
        ]
        for pos in pawn_positions:
            self.set_piece_at_hex(pos, HexPawn(Color.WHITE, pos))

        self.set_piece_at_hex(HexCoordinate(5, -5), HexRook(Color.BLACK, HexCoordinate(5, -5)))
        self.set_piece_at_hex(HexCoordinate(4, -5), HexKnight(Color.BLACK, HexCoordinate(4, -5)))
        self.set_piece_at_hex(HexCoordinate(3, -5), HexBishop(Color.BLACK, HexCoordinate(3, -5)))
        self.set_piece_at_hex(HexCoordinate(2, -5), HexQueen(Color.BLACK, HexCoordinate(2, -5)))
        self.set_piece_at_hex(HexCoordinate(1, -5), HexKing(Color.BLACK, HexCoordinate(1, -5)))
        self.set_piece_at_hex(HexCoordinate(0, -5), HexBishop(Color.BLACK, HexCoordinate(0, -5)))
        self.set_piece_at_hex(HexCoordinate(-1, -4), HexBishop(Color.BLACK, HexCoordinate(-1, -4)))
        self.set_piece_at_hex(HexCoordinate(-2, -3), HexKnight(Color.BLACK, HexCoordinate(-2, -3)))
        self.set_piece_at_hex(HexCoordinate(-3, -2), HexRook(Color.BLACK, HexCoordinate(-3, -2)))

        black_pawn_positions = [
            HexCoordinate(4, -4), HexCoordinate(3, -4), HexCoordinate(2, -4),
            HexCoordinate(1, -4), HexCoordinate(0, -4), HexCoordinate(-1, -3),
            HexCoordinate(-2, -2), HexCoordinate(-3, -1), HexCoordinate(-4, 0)
        ]
        for pos in black_pawn_positions:
            self.set_piece_at_hex(pos, HexPawn(Color.BLACK, pos))

    def display(self):
        print("\n" + "=" * 75)
        print("             ГЕКСАГОНАЛЬНЫЕ ШАХМАТЫ — 2 ИГРОКА")
        print("=" * 75)
        rows_data = []
        for r in range(-5, 6):
            row_hexes = []
            for q in range(-5, 6):
                hex_coord = HexCoordinate(q, r)
                if self.is_valid_hex(hex_coord):
                    row_hexes.append((q, hex_coord))
            if row_hexes:
                rows_data.append((r, row_hexes))

        for r, row_hexes in rows_data:
            indent = abs(r) * 2
            label_line = " " * indent
            piece_line = " " * indent
            for q, hex_coord in row_hexes:
                label = self.hex_labels[hex_coord]
                piece = self.get_piece_at_hex(hex_coord)
                label_line += f" {label:3s}"
                piece_line += f"  {piece.get_symbol()} " if piece else "  · "
            print(label_line)
            print(piece_line)

        print("=" * 75)
        print("Format: column(a-k) + row(1-11), example: f6 f7")
        print("Commands: 'show f6' | 'help' | 'quit'\n")

    def display_with_moves(self, hex_coord: HexCoordinate, available_hexes: List[HexCoordinate]):
        print("\n" + "=" * 75)
        print(f"  AVAILABLE MOVES FOR: {self.hex_labels[hex_coord]}")
        print("=" * 75)
        rows_data = []
        for r in range(-5, 6):
            row_hexes = []
            for q in range(-5, 6):
                hc = HexCoordinate(q, r)
                if self.is_valid_hex(hc):
                    row_hexes.append((q, hc))
            if row_hexes:
                rows_data.append((r, row_hexes))

        for r, row_hexes in rows_data:
            indent = abs(r) * 2
            piece_line = " " * indent
            for q, hc in row_hexes:
                piece = self.get_piece_at_hex(hc)
                if hc == hex_coord:
                    piece_line += f" [{piece.get_symbol()}]"
                elif hc in available_hexes:
                    piece_line += "  * "
                elif piece:
                    piece_line += f"  {piece.get_symbol()} "
                else:
                    piece_line += "  · "
            print(piece_line)

        print("=" * 75)
        print("[X] = selected | * = available move\n")
        print("Available destinations:")
        for i, h in enumerate(available_hexes, 1):
            label = self.hex_labels.get(h, "?")
            print(f"  {label}", end="  ")
            if i % 8 == 0:
                print()
        print("\n")

    def parse_label(self, label: str) -> Optional[HexCoordinate]:
        return self.label_to_hex.get(label.lower().strip())

    def get_all_pieces(self, color: Optional[Color] = None) -> List[HexPiece]:
        return [piece for piece in self.hexes.values() if color is None or piece.color == color]

    def find_king(self, color: Color) -> Optional[HexKing]:
        for piece in self.get_all_pieces(color):
            if isinstance(piece, HexKing):
                return piece
        return None


class HexChessGame:
    def __init__(self):
        self.board = HexBoard()
        self.current_turn = Color.WHITE
        self.game_over = False

    def parse_input(self, notation: str) -> Optional[HexCoordinate]:
        return self.board.parse_label(notation.strip().lower())

    def show_available_moves(self, notation: str):
        hex_coord = self.parse_input(notation)
        if hex_coord is None:
            print("ERROR: Invalid cell notation")
            return
        piece = self.board.get_piece_at_hex(hex_coord)
        if piece is None:
            print(f"ERROR: No piece at {notation}")
            return
        if piece.color != self.current_turn:
            print("ERROR: Not your piece")
            return
        legal_hexes = self.get_legal_hex_moves(piece)
        if not legal_hexes:
            print("ERROR: No available moves")
            return
        self.board.display_with_moves(hex_coord, legal_hexes)

    def get_legal_hex_moves(self, piece: HexPiece) -> List[HexCoordinate]:
        possible_hexes = piece.get_hex_moves(self.board)
        legal_hexes = []
        seen = set()

        for target_hex in possible_hexes:
            if target_hex in seen:
                continue
            original_piece = self.board.get_piece_at_hex(target_hex)
            original_hex = piece.hex_coord
            self.board.set_piece_at_hex(target_hex, piece)
            self.board.set_piece_at_hex(original_hex, None)

            king = self.board.find_king(piece.color)
            safe = True
            if king and self.is_hex_under_attack(king.hex_coord, piece.color.opposite()):
                safe = False

            self.board.set_piece_at_hex(original_hex, piece)
            self.board.set_piece_at_hex(target_hex, original_piece)

            if safe:
                legal_hexes.append(target_hex)
                seen.add(target_hex)

        return legal_hexes

    def is_hex_under_attack(self, hex_coord: HexCoordinate, by_color: Color) -> bool:
        for piece in self.board.get_all_pieces(by_color):
            if isinstance(piece, HexPawn):
                if hex_coord in piece.get_attack_hexes(self.board):
                    return True
            else:
                if hex_coord in piece.get_hex_moves(self.board):
                    return True
        return False

    def is_check(self, color: Color) -> bool:
        king = self.board.find_king(color)
        return self.is_hex_under_attack(king.hex_coord, color.opposite()) if king else False

    def is_checkmate(self, color: Color) -> bool:
        if not self.is_check(color):
            return False
        return all(not self.get_legal_hex_moves(piece) for piece in self.board.get_all_pieces(color))

    def is_stalemate(self, color: Color) -> bool:
        if self.is_check(color):
            return False
        return all(not self.get_legal_hex_moves(piece) for piece in self.board.get_all_pieces(color))

    def _promotion_rank(self, color: Color) -> set:
        if color == Color.WHITE:
            return {h for h in self.board.valid_hexes if h.r == -self.board.BOARD_SIZE}
        return {h for h in self.board.valid_hexes if h.r == self.board.BOARD_SIZE}

    def _try_promote(self, piece: HexPiece) -> bool:
        if not isinstance(piece, HexPawn):
            return False
        if piece.hex_coord not in self._promotion_rank(piece.color):
            return False

        print(f"\nPromotion on {self.board.hex_labels[piece.hex_coord]}!")
        print("Choose piece: Q=Queen  R=Rook  B=Bishop  N=Knight")
        choice_map = {'q': HexQueen, 'r': HexRook, 'b': HexBishop, 'n': HexKnight}
        while True:
            raw = input("Your choice: ").strip().lower()
            cls = choice_map.get(raw)
            if cls:
                h, col = piece.hex_coord, piece.color
                self.board.set_piece_at_hex(h, cls(col, h))
                print(f"Pawn promoted to {cls.__name__}")
                return True
            print("Invalid choice. Enter Q, R, B or N.")

    def make_hex_move(self, from_notation: str, to_notation: str) -> bool:
        from_hex = self.parse_input(from_notation)
        to_hex = self.parse_input(to_notation)

        if from_hex is None:
            print(f"ERROR: Invalid notation '{from_notation}'")
            return False
        if to_hex is None:
            print(f"ERROR: Invalid notation '{to_notation}'")
            return False

        piece = self.board.get_piece_at_hex(from_hex)
        if piece is None:
            print(f"ERROR: No piece at {from_notation}")
            return False
        if piece.color != self.current_turn:
            print("ERROR: Not your piece")
            return False

        legal_hexes = self.get_legal_hex_moves(piece)
        if to_hex not in legal_hexes:
            print("ERROR: Illegal move")
            print(f"Hint: 'show {from_notation}' to see valid moves")
            return False

        captured = self.board.get_piece_at_hex(to_hex)
        self.board.set_piece_at_hex(to_hex, piece)
        self.board.set_piece_at_hex(from_hex, None)
        piece.has_moved = True

        move = HexMove(from_hex, to_hex, captured)
        self.board.move_history.append(move)

        print(f"\nMove: {from_notation} -> {to_notation}")
        if captured:
            print(f"Captured: {captured.__class__.__name__}")

        moved_piece = self.board.get_piece_at_hex(to_hex)
        if moved_piece:
            self._try_promote(moved_piece)

        self.current_turn = self.current_turn.opposite()

        if self.is_checkmate(self.current_turn):
            print(f"\nCHECKMATE! {self.current_turn.opposite().value.upper()} WINS!")
            self.game_over = True
        elif self.is_stalemate(self.current_turn):
            print("\nSTALEMATE! Draw!")
            self.game_over = True
        elif self.is_check(self.current_turn):
            print("\nCHECK!")

        return True

    def play(self):
        print("\n" + "=" * 75)
        print("           HEXAGONAL CHESS — TWO-PLAYER VARIANT")
        print("=" * 75)
        print("\nКак играть:")
        print("  - формат клетки: столбец(a-k) + строка(1-11)")
        print("  - формат хода: f6 f7")
        print("  - команды: 'show f6', 'help', 'quit'")
        print("=" * 75 + "\n")

        while not self.game_over:
            self.board.display()
            print(f"Turn: {self.current_turn.value.upper()}\n")
            user_input = input("Enter move: ").strip().lower()
            print()

            if user_input in ['quit', 'q', 'exit']:
                print("Game terminated")
                break

            if user_input in ['help', 'h']:
                print("Commands:")
                print("  show <cell>  - show available moves (e.g., 'show f6')")
                print("  <from> <to>  - make a move (e.g., 'f6 f7')")
                print("  quit         - exit game\n")
                continue

            if user_input.startswith('show ') or user_input.startswith('s '):
                notation = user_input.split(maxsplit=1)[1]
                self.show_available_moves(notation)
                continue

            parts = user_input.split()
            if len(parts) != 2:
                print("ERROR: Use format 'f6 f7' or 'show f6'\n")
                continue

            self.make_hex_move(parts[0], parts[1])

        self.board.display()
        print("\n" + "=" * 75)
        print("           GAME OVER")
        print("=" * 75 + "\n")


if __name__ == "__main__":
    game = HexChessGame()
    game.play()
