# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from enum import Enum


class Color(Enum):
    WHITE = "white"
    BLACK = "black"
    BLUE = "blue"

    def next_turn(self):
        order = [Color.WHITE, Color.BLUE, Color.BLACK]
        i = order.index(self)
        return order[(i + 1) % len(order)]


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
        directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        return [HexCoordinate(self.q + dq, self.r + dr) for dq, dr in directions]


def rotate120(h: 'HexCoordinate') -> 'HexCoordinate':
    x, z = h.q, h.r
    y = -x - z
    return HexCoordinate(y, x)


def rotate240(h: 'HexCoordinate') -> 'HexCoordinate':
    return rotate120(rotate120(h))


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
    _forward = {
        Color.WHITE: (0, -1),
        Color.BLACK: (0, +1),
        Color.BLUE: (+1, 0),
    }

    _caps = {
        Color.WHITE: [(-1, 0), (+1, -1)],
        Color.BLACK: [(+1, 0), (-1, +1)],
        Color.BLUE: [(+1, -1), (0, +1)],
    }

    def get_symbol(self) -> str:
        return "P"

    def _capture_dirs(self) -> List[Tuple[int, int]]:
        return self._caps[self.color]

    def get_attack_hexes(self, board: 'HexBoard') -> List['HexCoordinate']:
        attacks: List[HexCoordinate] = []
        for dq, dr in self._capture_dirs():
            c = HexCoordinate(self.hex_coord.q + dq, self.hex_coord.r + dr)
            if board.is_valid_hex(c):
                attacks.append(c)
        return attacks

    def get_hex_moves(self, board: 'HexBoard') -> List['HexCoordinate']:
        moves: List[HexCoordinate] = []

        dq, dr = self._forward[self.color]
        one = HexCoordinate(self.hex_coord.q + dq, self.hex_coord.r + dr)
        if board.is_valid_hex(one) and board.get_piece_at_hex(one) is None:
            moves.append(one)

            if not self.has_moved:
                two = HexCoordinate(one.q + dq, one.r + dr)
                if board.is_valid_hex(two) and board.get_piece_at_hex(two) is None:
                    moves.append(two)

        for c in self.get_attack_hexes(board):
            occ = board.get_piece_at_hex(c)
            if occ is not None and occ.color != self.color:
                moves.append(c)

        return moves


class HexKnight(HexPiece):
    SYMBOLS = {Color.WHITE: '♘', Color.BLACK: '♞', Color.BLUE: '♞'}

    def get_symbol(self) -> str:
        return self.SYMBOLS.get(self.color, 'N')

    def get_hex_moves(self, board: 'HexBoard') -> List['HexCoordinate']:
        moves = []
        seen = set()
        ortho = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]

        for dq, dr in ortho:
            far = HexCoordinate(self.hex_coord.q + dq * 2, self.hex_coord.r + dr * 2)
            for sdq, sdr in self._get_perpendicular(dq, dr):
                h = HexCoordinate(far.q + sdq, far.r + sdr)
                if not board.is_valid_hex(h) or h in seen:
                    continue
                t = board.get_piece_at_hex(h)
                if t is None or t.color != self.color:
                    moves.append(h)
                    seen.add(h)
        return moves

    def _get_perpendicular(self, dq: int, dr: int) -> List[Tuple[int, int]]:
        all_dirs = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        return [d for d in all_dirs if d != (dq, dr) and d != (-dq, -dr)]


class HexBishop(HexPiece):
    SYMBOLS = {Color.WHITE: '♗', Color.BLACK: '♝', Color.BLUE: '♝'}

    def get_symbol(self) -> str:
        return self.SYMBOLS.get(self.color, 'B')

    def get_hex_moves(self, board: 'HexBoard') -> List['HexCoordinate']:
        moves = []
        for dq, dr in [(2, -1), (1, -2), (-1, -1), (-2, 1), (-1, 2), (1, 1)]:
            for dist in range(1, 13):
                h = HexCoordinate(self.hex_coord.q + dq * dist, self.hex_coord.r + dr * dist)
                if not board.is_valid_hex(h):
                    break
                t = board.get_piece_at_hex(h)
                if t is None:
                    moves.append(h)
                else:
                    if t.color != self.color:
                        moves.append(h)
                    break
        return moves


class HexRook(HexPiece):
    SYMBOLS = {Color.WHITE: '♖', Color.BLACK: '♜', Color.BLUE: '♜'}

    def get_symbol(self) -> str:
        return self.SYMBOLS.get(self.color, 'R')

    def get_hex_moves(self, board: 'HexBoard') -> List['HexCoordinate']:
        moves = []
        for dq, dr in [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]:
            for dist in range(1, 13):
                h = HexCoordinate(self.hex_coord.q + dq * dist, self.hex_coord.r + dr * dist)
                if not board.is_valid_hex(h):
                    break
                t = board.get_piece_at_hex(h)
                if t is None:
                    moves.append(h)
                else:
                    if t.color != self.color:
                        moves.append(h)
                    break
        return moves


class HexQueen(HexPiece):
    SYMBOLS = {Color.WHITE: '♕', Color.BLACK: '♛', Color.BLUE: '♛'}

    def get_symbol(self) -> str:
        return self.SYMBOLS.get(self.color, 'Q')

    def get_hex_moves(self, board: 'HexBoard') -> List['HexCoordinate']:
        moves = []
        for dq, dr in [
            (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1),
            (2, -1), (1, -2), (-1, -1), (-2, 1), (-1, 2), (1, 1)
        ]:
            for dist in range(1, 13):
                h = HexCoordinate(self.hex_coord.q + dq * dist, self.hex_coord.r + dr * dist)
                if not board.is_valid_hex(h):
                    break
                t = board.get_piece_at_hex(h)
                if t is None:
                    moves.append(h)
                else:
                    if t.color != self.color:
                        moves.append(h)
                    break
        return moves


class HexKing(HexPiece):
    _king_dirs = [
        (1, 0), (1, -1), (0, -1),
        (-1, 0), (-1, 1), (0, 1),
        (2, -1), (1, -2), (-1, -1),
        (-2, 1), (-1, 2), (1, 1),
    ]

    def get_symbol(self) -> str:
        return 'K'

    def get_hex_moves(self, board: 'HexBoard') -> List['HexCoordinate']:
        moves: List[HexCoordinate] = []
        for dq, dr in self._king_dirs:
            c = HexCoordinate(self.hex_coord.q + dq, self.hex_coord.r + dr)
            if not board.is_valid_hex(c):
                continue
            occ = board.get_piece_at_hex(c)
            if occ is None or occ.color != self.color:
                moves.append(c)
        return moves


class HexMove:
    def __init__(self, from_hex: HexCoordinate, to_hex: HexCoordinate,
                 captured_piece: Optional[HexPiece] = None, promoted: bool = False):
        self.from_hex = from_hex
        self.to_hex = to_hex
        self.captured_piece = captured_piece
        self.promoted = promoted


class HexBoard:
    BOARD_SIZE = 6

    def __init__(self):
        self.hexes: dict = {}
        self.move_history: List[HexMove] = []
        self._init_valid_hexes()
        self._create_labels()
        self._setup_initial_position()
        self._assert_initial_position_ok()

    def _init_valid_hexes(self):
        self.valid_hexes = set()
        s = self.BOARD_SIZE
        for q in range(-s, s + 1):
            r1 = max(-s, -q - s)
            r2 = min(s, -q + s)
            for r in range(r1, r2 + 1):
                self.valid_hexes.add(HexCoordinate(q, r))

    def _create_labels(self):
        self.hex_labels: dict = {}
        self.label_to_hex: dict = {}
        cols = 'abcdefghijklm'
        s = self.BOARD_SIZE
        for q in range(-s, s + 1):
            col_letter = cols[q + s]
            for r in range(-s, s + 1):
                h = HexCoordinate(q, r)
                if h in self.valid_hexes:
                    row_num = (s * 2 + 1) - (r + s)
                    label = f"{col_letter}{row_num}"
                    self.hex_labels[h] = label
                    self.label_to_hex[label] = h

    def _setup_initial_position(self):
        base_back = [
            (-6, 6, HexRook),
            (-5, 6, HexKnight),
            (-4, 6, HexBishop),
            (-3, 6, HexQueen),
            (-2, 6, HexKing),
            (-1, 6, HexBishop),
            (0, 6, HexKnight),
        ]
        base_pawns = [(q, 5, HexPawn) for q in range(-6, 1)]

        def place(color: Color, rot_fn):
            for q, r, cls in base_back + base_pawns:
                h = rot_fn(HexCoordinate(q, r))
                if not self.is_valid_hex(h):
                    raise ValueError(f"Невалидная клетка {h} для {color.value}")
                if self.get_piece_at_hex(h) is not None:
                    raise ValueError(f"Перекрытие на {h} для {color.value}")
                self.set_piece_at_hex(h, cls(color, h))

        place(Color.WHITE, lambda h: h)
        place(Color.BLUE, rotate120)
        place(Color.BLACK, rotate240)

    def _assert_initial_position_ok(self):
        by_color = {Color.WHITE: [], Color.BLUE: [], Color.BLACK: []}
        for h, p in list(self.hexes.items()):
            if not self.is_valid_hex(h):
                raise AssertionError(f"Фигура на невалидной клетке: {h}")
            by_color[p.color].append(h)
        for c in Color:
            cnt = len(by_color[c])
            if cnt != 14:
                raise AssertionError(f"Ожидалось 14 для {c.value}, найдено {cnt}")
        wh = set(by_color[Color.WHITE])
        bl = set(by_color[Color.BLUE])
        bk = set(by_color[Color.BLACK])
        if {rotate120(h) for h in wh} != bl:
            raise AssertionError("WHITE→BLUE нарушена")
        if {rotate120(h) for h in bl} != bk:
            raise AssertionError("BLUE→BLACK нарушена")
        if {rotate120(h) for h in bk} != wh:
            raise AssertionError("BLACK→WHITE нарушена")

    def is_valid_hex(self, h: HexCoordinate) -> bool:
        return h in self.valid_hexes

    def get_piece_at_hex(self, h: HexCoordinate) -> Optional[HexPiece]:
        return self.hexes.get(h)

    def set_piece_at_hex(self, h: HexCoordinate, piece: Optional[HexPiece]):
        if piece is not None:
            self.hexes[h] = piece
            piece.hex_coord = h
        else:
            self.hexes.pop(h, None)

    def parse_label(self, label: str) -> Optional[HexCoordinate]:
        return self.label_to_hex.get(label.lower().strip())

    def get_all_pieces(self, color: Optional[Color] = None) -> List[HexPiece]:
        return [p for p in list(self.hexes.values()) if color is None or p.color == color]

    def find_king(self, color: Color) -> Optional[HexKing]:
        for p in self.get_all_pieces(color):
            if isinstance(p, HexKing):
                return p
        return None

    _COLOR_ANSI = {
        Color.WHITE: '\033[97m',
        Color.BLUE: '\033[94m',
        Color.BLACK: '\033[90m',
    }
    _RESET = '\033[0m'

    def _colored(self, piece: HexPiece) -> str:
        return f"{self._COLOR_ANSI[piece.color]}{piece.get_symbol()}{self._RESET}"

    def display(self):
        s = self.BOARD_SIZE
        print("\n" + "=" * 75)
        print("  HEXAGONAL CHESS — THREE-PLAYER")
        print("=" * 75)
        for r in range(-s, s + 1):
            row_hexes = [(q, HexCoordinate(q, r))
                         for q in range(-s, s + 1)
                         if HexCoordinate(q, r) in self.valid_hexes]
            if not row_hexes:
                continue
            indent = " " * (abs(r) * 2)
            cells = []
            for q, h in row_hexes:
                lbl = self.hex_labels[h]
                piece = self.get_piece_at_hex(h)
                sym = self._colored(piece) if piece else '·'
                cells.append(f"{lbl}:{sym}")
            print(indent + "  ".join(cells))
        print("=" * 75)
        print("Формат хода: g7 g8  |  Команды: show g7 | help | quit\n")

    def display_with_moves(self, hex_coord: HexCoordinate, available_hexes: List[HexCoordinate]):
        s = self.BOARD_SIZE
        print("\n" + "=" * 75)
        print(f"  Доступные ходы для: {self.hex_labels[hex_coord]}")
        print("=" * 75)
        avail_set = set(available_hexes)
        for r in range(-s, s + 1):
            row_hexes = [(q, HexCoordinate(q, r))
                         for q in range(-s, s + 1)
                         if HexCoordinate(q, r) in self.valid_hexes]
            if not row_hexes:
                continue
            indent = " " * (abs(r) * 2)
            cells = []
            for q, h in row_hexes:
                piece = self.get_piece_at_hex(h)
                if h == hex_coord:
                    cells.append(f"[{self._colored(piece)}]" if piece else "[·]")
                elif h in avail_set:
                    enemy = self.get_piece_at_hex(h)
                    cells.append(f"*{self._colored(enemy)}*" if enemy else " * ")
                else:
                    cells.append(self._colored(piece) if piece else " · ")
            print(indent + " ".join(cells))
        print("=" * 75)
        print("[X] = выбрано  |  * = ход  |  *X* = взятие\n")
        print("Доступные клетки: " +
              "  ".join(self.hex_labels.get(h, '?') for h in available_hexes) + "\n")


class HexChessGame:
    _TURN_ORDER = [Color.WHITE, Color.BLUE, Color.BLACK]

    def __init__(self):
        self.board = HexBoard()
        self.current_turn = Color.WHITE
        self.game_over = False
        self.eliminated: List[Color] = []

    def parse_input(self, notation: str) -> Optional[HexCoordinate]:
        return self.board.parse_label(notation)

    def get_legal_hex_moves(self, piece: HexPiece) -> List[HexCoordinate]:
        possible = piece.get_hex_moves(self.board)
        legal = []
        seen = set()
        orig_hex = piece.hex_coord

        for target in possible:
            if target in seen:
                continue
            captured = self.board.get_piece_at_hex(target)
            self.board.set_piece_at_hex(target, piece)
            self.board.set_piece_at_hex(orig_hex, None)

            king = self.board.find_king(piece.color)
            safe = True
            if king:
                for c in Color:
                    if c == piece.color or c in self.eliminated:
                        continue
                    if self._hex_attacked_by(king.hex_coord, c):
                        safe = False
                        break

            self.board.set_piece_at_hex(orig_hex, piece)
            self.board.set_piece_at_hex(target, captured)

            if safe:
                legal.append(target)
                seen.add(target)
        return legal

    def _hex_attacked_by(self, h: HexCoordinate, by_color: Color) -> bool:
        for p in self.board.get_all_pieces(by_color):
            if isinstance(p, HexPawn):
                if h in p.get_attack_hexes(self.board):
                    return True
            else:
                if h in p.get_hex_moves(self.board):
                    return True
        return False

    def is_check(self, color: Color) -> bool:
        king = self.board.find_king(color)
        if not king:
            return False
        for c in Color:
            if c == color or c in self.eliminated:
                continue
            if self._hex_attacked_by(king.hex_coord, c):
                return True
        return False

    def is_checkmate(self, color: Color) -> bool:
        if not self.is_check(color):
            return False
        return all(not self.get_legal_hex_moves(p) for p in self.board.get_all_pieces(color))

    def is_stalemate(self, color: Color) -> bool:
        if self.is_check(color):
            return False
        return all(not self.get_legal_hex_moves(p) for p in self.board.get_all_pieces(color))

    def _promotion_rank(self, color: Color) -> set:
        s = self.board.BOARD_SIZE
        if color == Color.WHITE:
            return {h for h in self.board.valid_hexes if h.r == -s}
        if color == Color.BLACK:
            return {h for h in self.board.valid_hexes if h.r == s}
        return {h for h in self.board.valid_hexes if h.q == s}

    def _try_promote(self, piece: HexPiece) -> bool:
        if not isinstance(piece, HexPawn):
            return False
        if piece.hex_coord not in self._promotion_rank(piece.color):
            return False
        print(f"\nПревращение пешки на {self.board.hex_labels[piece.hex_coord]}!")
        print("Выберите фигуру: Q=ферзь  R=ладья  B=слон  N=конь")
        choice_map = {'q': HexQueen, 'r': HexRook, 'b': HexBishop, 'n': HexKnight}
        while True:
            raw = input("Ваш выбор: ").strip().lower()
            cls = choice_map.get(raw)
            if cls:
                h, col = piece.hex_coord, piece.color
                self.board.set_piece_at_hex(h, cls(col, h))
                print(f"Пешка превращена в {cls.__name__}")
                return True
            print("Неверный выбор. Введите Q, R, B или N.")

    def _next_active(self, color: Color) -> Color:
        order = self._TURN_ORDER
        i = order.index(color)
        for step in range(1, len(order) + 1):
            nxt = order[(i + step) % len(order)]
            if nxt not in self.eliminated:
                return nxt
        return color

    def _prev_active(self, color: Color) -> Color:
        order = self._TURN_ORDER
        i = order.index(color)
        for step in range(1, len(order) + 1):
            prv = order[(i - step) % len(order)]
            if prv not in self.eliminated:
                return prv
        return color

    def _eliminate(self, color: Color):
        self.eliminated.append(color)
        for h in [h for h, p in list(self.board.hexes.items()) if p.color == color]:
            self.board.set_piece_at_hex(h, None)

        active = [c for c in self._TURN_ORDER if c not in self.eliminated]
        if len(active) == 1:
            print(f"\n🏆  ПОБЕДА! {active[0].value.upper()} выигрывает партию!")
            self.game_over = True
        elif len(active) == 0:
            print("\nНичья!")
            self.game_over = True
        else:
            if self.current_turn == color:
                self.current_turn = self._next_active(color)

    def make_hex_move(self, from_notation: str, to_notation: str) -> bool:
        f = self.parse_input(from_notation)
        t = self.parse_input(to_notation)

        if f is None:
            print(f"ОШИБКА: Неверная нотация '{from_notation}'")
            return False
        if t is None:
            print(f"ОШИБКА: Неверная нотация '{to_notation}'")
            return False

        piece = self.board.get_piece_at_hex(f)
        if piece is None:
            print(f"ОШИБКА: На клетке {from_notation} нет фигуры")
            return False
        if piece.color != self.current_turn:
            print("ОШИБКА: Чужая фигура")
            return False

        legal = self.get_legal_hex_moves(piece)
        if t not in legal:
            print("ОШИБКА: Недопустимый ход")
            print(f"Подсказка: 'show {from_notation}' для просмотра ходов")
            return False

        captured = self.board.get_piece_at_hex(t)
        self.board.set_piece_at_hex(t, piece)
        self.board.set_piece_at_hex(f, None)
        piece.has_moved = True
        self.board.move_history.append(HexMove(f, t, captured))

        print(f"\nХод: {from_notation} → {to_notation}")
        if captured:
            print(f"  ⚔️  Взята фигура: {captured.__class__.__name__} ({captured.color.value})")

        moved_piece = self.board.get_piece_at_hex(t)
        if moved_piece:
            self._try_promote(moved_piece)

        self.current_turn = self._next_active(self.current_turn)
        cur = self.current_turn

        if self.is_checkmate(cur):
            prev = self._prev_active(cur)
            print(f"\n♟  МАТ! {prev.value.upper()} ставит мат {cur.value.upper()}!")
            self._eliminate(cur)
        elif self.is_stalemate(cur):
            print(f"\nПАТ для {cur.value.upper()}! Игрок выбывает.")
            self._eliminate(cur)
        elif self.is_check(cur):
            print(f"\n⚠️  ШАХ {cur.value.upper()}!")

        return True

    def show_available_moves(self, notation: str):
        h = self.parse_input(notation)
        if h is None:
            print("ОШИБКА: Неверная нотация")
            return
        piece = self.board.get_piece_at_hex(h)
        if piece is None:
            print(f"ОШИБКА: На клетке {notation} нет фигуры")
            return
        if piece.color != self.current_turn:
            print("ОШИБКА: Не ваша фигура")
            return
        legal = self.get_legal_hex_moves(piece)
        if not legal:
            print("ОШИБКА: Нет доступных ходов")
            return
        self.board.display_with_moves(h, legal)

    def play(self):
        print("\n" + "=" * 75)
        print("  HEXAGONAL CHESS — ТРЁХСТОРОННИЙ ВАРИАНТ")
        print("=" * 75)
        print("\nПравила:")
        print("  Клетки: столбец(a-m) + строка(1-13), пример: g7")
        print("  Ход: g7 g8  |  show g7 — ходы фигуры  |  quit — выход\n")
        while not self.game_over:
            self.board.display()
            active = [c.value.upper() for c in self._TURN_ORDER if c not in self.eliminated]
            print(f"Активные игроки: {' | '.join(active)}")
            print(f"Ход: {self.current_turn.value.upper()}\n")
            raw = input("Введите ход: ").strip().lower()
            print()

            if raw in ('quit', 'q', 'exit'):
                print("Игра завершена")
                break
            if raw in ('help', 'h'):
                print("  show <клетка> — показать ходы\n"
                      "  <от> <куда>   — сделать ход\n"
                      "  quit          — выйти\n")
                continue
            if raw.startswith(('show ', 's ')):
                self.show_available_moves(raw.split(maxsplit=1)[1])
                continue

            parts = raw.split()
            if len(parts) != 2:
                print("ОШИБКА: Используйте формат 'g7 g8' или 'show g7'\n")
                continue

            self.make_hex_move(parts[0], parts[1])

        self.board.display()
        print("\n" + "=" * 75 + "\n  КОНЕЦ ИГРЫ\n" + "=" * 75 + "\n")


if __name__ == "__main__":
    game = HexChessGame()
    game.play()
