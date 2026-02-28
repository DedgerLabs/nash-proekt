import pygame
from abc import ABC, abstractmethod

pygame.init()

WIDTH, HEIGHT = 800, 800
SQUARE_SIZE = WIDTH // 8

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
HIGHLIGHT = (255, 255, 0, 150)
VALID_MOVE = (0, 255, 0, 150)
CAPTURE_MOVE = (255, 100, 100, 150)
LAST_MOVE = (173, 216, 230, 150)
THREATENED_COLOR = (255, 100, 0, 180)
CHECK_COLOR = (255, 50, 50, 200)

# Константы для цветов фигур
WHITE_PIECE = 0
BLACK_PIECE = 1

# Константы для типов фигур (для превращения)
QUEEN = 'q'
ROOK = 'r'
BISHOP = 'b'
KNIGHT = 'n'


# ==================== ИЕРАРХИЯ КЛАССОВ ФИГУР ====================
class Piece(ABC):
    """Абстрактный базовый класс для всех шахматных фигур"""

    def __init__(self, color, pos):
        self.color = color  # WHITE_PIECE или BLACK_PIECE
        self.pos = pos  # позиция в формате (row, col) где row 0-7, col 0-7
        self.has_moved = False
        self.symbol = self.get_symbol()  # символ для отображения

    @abstractmethod
    def get_possible_moves(self, board):
        """Возвращает все возможные ходы без учета шахов"""
        pass

    @abstractmethod
    def get_symbol(self):
        """Возвращает символ фигуры для отображения"""
        pass

    def get_valid_moves(self, board):
        """Возвращает легальные ходы с учетом защиты короля"""
        possible_moves = self.get_possible_moves(board)
        valid_moves = []

        for move in possible_moves:
            if board.is_move_legal(self.pos, move, self.color):
                valid_moves.append(move)

        return valid_moves

    def move_to(self, new_pos):
        """Перемещает фигуру на новую позицию"""
        self.pos = new_pos
        self.has_moved = True


class Pawn(Piece):
    """Класс пешки"""

    def get_symbol(self):
        return 'Р' if self.color == WHITE_PIECE else 'р'

    def get_possible_moves(self, board):
        moves = []
        row, col = self.pos
        direction = -1 if self.color == WHITE_PIECE else 1  # белые вверх (row уменьшается)

        # Движение вперед на 1 клетку
        new_row = row + direction
        if 0 <= new_row < 8 and board.get_piece_at((new_row, col)) is None:
            moves.append((new_row, col))

            # Движение вперед на 2 клетки с начальной позиции
            if not self.has_moved:
                new_row2 = row + 2 * direction
                if 0 <= new_row2 < 8 and board.get_piece_at((new_row2, col)) is None:
                    moves.append((new_row2, col))

        # Взятие фигур по диагонали
        for dcol in [-1, 1]:
            new_col = col + dcol
            new_row = row + direction
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board.get_piece_at((new_row, new_col))
                if target and target.color != self.color:
                    moves.append((new_row, new_col))

        return moves


class Knight(Piece):
    """Класс коня"""

    def get_symbol(self):
        return 'Л' if self.color == WHITE_PIECE else 'л'

    def get_possible_moves(self, board):
        moves = []
        row, col = self.pos

        # Все возможные ходы коня (8 направлений)
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board.get_piece_at((new_row, new_col))
                if target is None or target.color != self.color:
                    moves.append((new_row, new_col))

        return moves


class Bishop(Piece):
    """Класс слона"""

    def get_symbol(self):
        return 'С' if self.color == WHITE_PIECE else 'с'

    def get_possible_moves(self, board):
        moves = []
        row, col = self.pos

        # Четыре диагональных направления
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:
            for step in range(1, 8):
                new_row, new_col = row + step * dr, col + step * dc
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break

                target = board.get_piece_at((new_row, new_col))
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != self.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break

        return moves


class Rook(Piece):
    """Класс ладьи"""

    def get_symbol(self):
        return 'Л' if self.color == WHITE_PIECE else 'л'

    def get_possible_moves(self, board):
        moves = []
        row, col = self.pos

        # Четыре ортогональных направления
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            for step in range(1, 8):
                new_row, new_col = row + step * dr, col + step * dc
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break

                target = board.get_piece_at((new_row, new_col))
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != self.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break

        return moves


class Queen(Piece):
    """Класс ферзя (комбинация слона и ладьи)"""

    def get_symbol(self):
        return 'Q' if self.color == WHITE_PIECE else 'q'

    def get_possible_moves(self, board):
        moves = []
        row, col = self.pos

        # Все 8 направлений
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for dr, dc in directions:
            for step in range(1, 8):
                new_row, new_col = row + step * dr, col + step * dc
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break

                target = board.get_piece_at((new_row, new_col))
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != self.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break

        return moves


class King(Piece):
    """Класс короля"""

    def get_symbol(self):
        return 'K' if self.color == WHITE_PIECE else 'k'

    def get_possible_moves(self, board):
        moves = []
        row, col = self.pos

        # Все соседние клетки
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue

                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = board.get_piece_at((new_row, new_col))
                    if target is None or target.color != self.color:
                        moves.append((new_row, new_col))

        # Рокировка
        if not self.has_moved and not board.is_in_check(self.color):
            # Короткая рокировка
            if board.can_castle_kingside(self.color):
                moves.append((row, col + 2))
            # Длинная рокировка
            if board.can_castle_queenside(self.color):
                moves.append((row, col - 2))

        return moves


# ==================== ДОПОЛНИТЕЛЬНЫЕ ФИГУРЫ (модификация) ====================
class Archbishop(Piece):
    """
    Архиепископ: ходит как СЛОН + КОНЬ (объединение ходов).
    """

    def get_symbol(self):
        return 'A' if self.color == WHITE_PIECE else 'a'

    def get_possible_moves(self, board):
        moves = set()

        # как слон
        row, col = self.pos
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            for step in range(1, 8):
                new_row, new_col = row + step * dr, col + step * dc
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                target = board.get_piece_at((new_row, new_col))
                if target is None:
                    moves.add((new_row, new_col))
                elif target.color != self.color:
                    moves.add((new_row, new_col))
                    break
                else:
                    break

        # как конь
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board.get_piece_at((new_row, new_col))
                if target is None or target.color != self.color:
                    moves.add((new_row, new_col))

        return list(moves)


class Chancellor(Piece):
    """
    Канцлер: ходит как ЛАДЬЯ + КОНЬ (объединение ходов).
    """

    def get_symbol(self):
        return 'C' if self.color == WHITE_PIECE else 'c'

    def get_possible_moves(self, board):
        moves = set()
        row, col = self.pos

        # как ладья
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            for step in range(1, 8):
                new_row, new_col = row + step * dr, col + step * dc
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                target = board.get_piece_at((new_row, new_col))
                if target is None:
                    moves.add((new_row, new_col))
                elif target.color != self.color:
                    moves.add((new_row, new_col))
                    break
                else:
                    break

        # как конь
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board.get_piece_at((new_row, new_col))
                if target is None or target.color != self.color:
                    moves.add((new_row, new_col))

        return list(moves)


class Camel(Piece):
    """
    Верблюд: "длинный конь" (3+1).
    Ходы: (±3,±1) и (±1,±3)
    """

    def get_symbol(self):
        return 'M' if self.color == WHITE_PIECE else 'm'

    def get_possible_moves(self, board):
        moves = []
        row, col = self.pos

        camel_moves = [
            (-3, -1), (-3, 1), (3, -1), (3, 1),
            (-1, -3), (-1, 3), (1, -3), (1, 3),
        ]

        for dr, dc in camel_moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board.get_piece_at((new_row, new_col))
                if target is None or target.color != self.color:
                    moves.append((new_row, new_col))

        return moves


# ==================== КЛАСС ХОДА ====================

class Move:
    """Класс, представляющий ход"""

    def __init__(self, from_pos, to_pos, piece, captured_piece=None,
                 is_castling=False, is_en_passant=False, promotion=None):
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.piece = piece
        self.captured_piece = captured_piece
        self.is_castling = is_castling
        self.is_en_passant = is_en_passant
        self.promotion = promotion  # тип фигуры для превращения
        self.notation = self.generate_notation()

    def generate_notation(self):
        """Генерирует строковую нотацию хода"""
        cols = 'abcdefgh'
        rows = '87654321'

        from_str = cols[self.from_pos[1]] + rows[self.from_pos[0]]
        to_str = cols[self.to_pos[1]] + rows[self.to_pos[0]]

        if self.promotion:
            return f"{from_str}{to_str}{self.promotion}"
        return f"{from_str}{to_str}"

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return (self.from_pos == other.from_pos and
                self.to_pos == other.to_pos and
                self.promotion == other.promotion)


# ==================== КЛАСС ДОСКИ ====================

class Board:
    """Класс шахматной доски"""

    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.current_turn = WHITE_PIECE
        self.move_history = []
        self.setup_board()

    def setup_board(self):
        """Расставляет фигуры в начальную позицию"""
        # Пешки
        for col in range(8):
            self.grid[1][col] = Pawn(BLACK_PIECE, (1, col))
            self.grid[6][col] = Pawn(WHITE_PIECE, (6, col))

        # Ладьи
        self.grid[0][0] = Rook(BLACK_PIECE, (0, 0))
        self.grid[0][7] = Rook(BLACK_PIECE, (0, 7))
        self.grid[7][0] = Rook(WHITE_PIECE, (7, 0))
        self.grid[7][7] = Rook(WHITE_PIECE, (7, 7))

        # Кони
        self.grid[0][1] = Chancellor(BLACK_PIECE, (0, 1))
        self.grid[0][6] = Archbishop(BLACK_PIECE, (0, 6))
        self.grid[7][1] = Chancellor(WHITE_PIECE, (7, 1))
        self.grid[7][6] = Archbishop(WHITE_PIECE, (7, 6))

        # Слоны
        self.grid[0][2] = Camel(BLACK_PIECE, (0, 2))
        self.grid[0][5] = Bishop(BLACK_PIECE, (0, 5))
        self.grid[7][2] = Camel(WHITE_PIECE, (7, 2))
        self.grid[7][5] = Bishop(WHITE_PIECE, (7, 5))

        # Ферзи
        self.grid[0][3] = Queen(BLACK_PIECE, (0, 3))
        self.grid[7][3] = Queen(WHITE_PIECE, (7, 3))

        # Короли
        self.grid[0][4] = King(BLACK_PIECE, (0, 4))
        self.grid[7][4] = King(WHITE_PIECE, (7, 4))

    def get_piece_at(self, pos):
        """Возвращает фигуру в указанной позиции"""
        row, col = pos
        if 0 <= row < 8 and 0 <= col < 8:
            return self.grid[row][col]
        return None

    def get_king_position(self, color):
        """Возвращает позицию короля указанного цвета"""
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and isinstance(piece, King) and piece.color == color:
                    return (row, col)
        return None

    def is_square_attacked(self, pos, attacking_color):
        """Проверяет, атакована ли клетка фигурами указанного цвета"""
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and piece.color == attacking_color:
                    # Временно убираем короля из рассмотрения, если это он
                    if isinstance(piece, King):
                        continue

                    possible_moves = piece.get_possible_moves(self)
                    if pos in possible_moves:
                        return True

        # Проверяем атаки короля отдельно
        king_pos = self.get_king_position(attacking_color)
        if king_pos:
            king = self.grid[king_pos[0]][king_pos[1]]
            if king:
                kr, kc = king_pos
                pr, pc = pos
                if abs(kr - pr) <= 1 and abs(kc - pc) <= 1:
                    return True

        return False

    def is_in_check(self, color):
        """Проверяет, находится ли король указанного цвета под шахом"""
        king_pos = self.get_king_position(color)
        if not king_pos:
            return False

        opponent_color = BLACK_PIECE if color == WHITE_PIECE else WHITE_PIECE
        return self.is_square_attacked(king_pos, opponent_color)

    def is_move_legal(self, from_pos, to_pos, color):
        """Проверяет, не оставляет ли ход короля под шахом"""
        # Создаем копию доски и делаем ход
        temp_board = self.copy()
        temp_board.make_move(from_pos, to_pos, check_legal=False)

        # Проверяем, не под шахом ли король после хода
        return not temp_board.is_in_check(color)

    def make_move(self, from_pos, to_pos, promotion=None, check_legal=True):
        """Выполняет ход"""
        piece = self.get_piece_at(from_pos)
        if not piece:
            return None

        target = self.get_piece_at(to_pos)

        # Проверка легальности хода
        if check_legal:
            if piece.color != self.current_turn:
                return None

            possible_moves = piece.get_possible_moves(self)
            if to_pos not in possible_moves:
                return None

            if not self.is_move_legal(from_pos, to_pos, piece.color):
                return None

        # Создаем объект хода
        move = Move(from_pos, to_pos, piece, target)

        # Обработка превращения пешки
        if isinstance(piece, Pawn):
            if (piece.color == WHITE_PIECE and to_pos[0] == 0) or \
                    (piece.color == BLACK_PIECE and to_pos[0] == 7):
                if promotion:
                    # Создаем новую фигуру согласно выбору
                    new_piece_class = {
                        QUEEN: Queen,
                        ROOK: Rook,
                        BISHOP: Bishop,
                        KNIGHT: Knight
                    }.get(promotion)

                    if new_piece_class:
                        self.grid[from_pos[0]][from_pos[1]] = None
                        self.grid[to_pos[0]][to_pos[1]] = new_piece_class(piece.color, to_pos)
                        move.promotion = promotion

        if not move.promotion:
            # Обычный ход
            self.grid[from_pos[0]][from_pos[1]] = None
            self.grid[to_pos[0]][to_pos[1]] = piece
            piece.move_to(to_pos)

        # Обработка рокировки
        if isinstance(piece, King) and abs(to_pos[1] - from_pos[1]) == 2:
            move.is_castling = True
            # Перемещаем ладью
            if to_pos[1] > from_pos[1]:  # Короткая рокировка
                rook = self.grid[from_pos[0]][7]
                self.grid[from_pos[0]][7] = None
                self.grid[from_pos[0]][5] = rook
                rook.move_to((from_pos[0], 5))
            else:  # Длинная рокировка
                rook = self.grid[from_pos[0]][0]
                self.grid[from_pos[0]][0] = None
                self.grid[from_pos[0]][3] = rook
                rook.move_to((from_pos[0], 3))

        # Меняем очередь хода
        self.current_turn = BLACK_PIECE if self.current_turn == WHITE_PIECE else WHITE_PIECE
        self.move_history.append(move)

        return move

    def can_castle_kingside(self, color):
        """Проверяет возможность короткой рокировки"""
        row = 7 if color == WHITE_PIECE else 0

        # Проверяем короля
        king = self.grid[row][4]
        if not king or not isinstance(king, King) or king.has_moved:
            return False

        # Проверяем ладью
        rook = self.grid[row][7]
        if not rook or not isinstance(rook, Rook) or rook.has_moved:
            return False

        # Проверяем, что клетки между ними пусты
        if self.grid[row][5] is not None or self.grid[row][6] is not None:
            return False

        # Проверяем, что король не проходит через битые клетки
        opponent = BLACK_PIECE if color == WHITE_PIECE else WHITE_PIECE
        for col in [4, 5, 6]:
            if self.is_square_attacked((row, col), opponent):
                return False

        return True

    def can_castle_queenside(self, color):
        """Проверяет возможность длинной рокировки"""
        row = 7 if color == WHITE_PIECE else 0

        # Проверяем короля
        king = self.grid[row][4]
        if not king or not isinstance(king, King) or king.has_moved:
            return False

        # Проверяем ладью
        rook = self.grid[row][0]
        if not rook or not isinstance(rook, Rook) or rook.has_moved:
            return False

        # Проверяем, что клетки между ними пусты
        if (self.grid[row][1] is not None or
                self.grid[row][2] is not None or
                self.grid[row][3] is not None):
            return False

        # Проверяем, что король не проходит через битые клетки
        opponent = BLACK_PIECE if color == WHITE_PIECE else WHITE_PIECE
        for col in [2, 3, 4]:
            if self.is_square_attacked((row, col), opponent):
                return False

        return True

    def copy(self):
        """Создает глубокую копию доски"""
        new_board = Board.__new__(Board)
        new_board.grid = [[None for _ in range(8)] for _ in range(8)]

        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece:
                    # Создаем копию фигуры
                    piece_class = piece.__class__
                    new_piece = piece_class(piece.color, (row, col))
                    new_piece.has_moved = piece.has_moved
                    new_board.grid[row][col] = new_piece

        new_board.current_turn = self.current_turn
        new_board.move_history = self.move_history.copy()

        return new_board

    def is_checkmate(self):
        """Проверяет, есть ли мат"""
        if not self.is_in_check(self.current_turn):
            return False

        # Проверяем, есть ли хоть один легальный ход
        return not self.has_any_legal_move(self.current_turn)

    def is_stalemate(self):
        """Проверяет, есть ли пат"""
        if self.is_in_check(self.current_turn):
            return False

        # Проверяем, есть ли хоть один легальный ход
        return not self.has_any_legal_move(self.current_turn)

    def has_any_legal_move(self, color):
        """Проверяет, есть ли у цвета хоть один легальный ход"""
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and piece.color == color:
                    moves = piece.get_possible_moves(self)
                    for move in moves:
                        if self.is_move_legal((row, col), move, color):
                            return True
        return False


# ==================== ОСНОВНОЙ КЛАСС ИГРЫ ====================

class ChessGame:
    def __init__(self, screen):
        self.screen = screen
        self.board = Board()

        self.selected_square = None
        self.valid_moves = []
        self.last_move = None

        self.promotion_menu_active = False
        self.pending_promotion_move = None
        self.pending_promotion_from = None
        self.pending_promotion_to = None

        self.show_threats = False
        self.threatened_squares = set()

        # Загружаем изображения фигур
        self.pieces = {}
        self.load_pieces()

    def load_pieces(self):
        """Создает поверхности с символами фигур"""
        piece_size = SQUARE_SIZE - 40

        try:
            font = pygame.font.SysFont('arial', 64, bold=True)
        except:
            font = pygame.font.SysFont('arial', 64, bold=True)

        # Создаем поверхности для всех фигур
        for row in range(8):
            for col in range(8):
                piece = self.board.grid[row][col]
                if piece:
                    surf = pygame.Surface((piece_size, piece_size), pygame.SRCALPHA)
                    text_color = BLACK if piece.color == WHITE_PIECE else WHITE

                    text = font.render(piece.symbol, True, text_color)
                    text_rect = text.get_rect(center=(piece_size // 2, piece_size // 2))
                    surf.blit(text, text_rect)

                    piece_key = f"{'w' if piece.color == WHITE_PIECE else 'b'}{piece.__class__.__name__}"
                    self.pieces[piece_key] = surf

    def calculate_threats(self):
        """Вычисляет фигуры под угрозой"""
        self.threatened_squares.clear()

        if not self.show_threats:
            return

        current_color = self.board.current_turn
        opponent_color = BLACK_PIECE if current_color == WHITE_PIECE else WHITE_PIECE

        # Находим все клетки, атакованные противником
        attacked_squares = set()
        for row in range(8):
            for col in range(8):
                piece = self.board.grid[row][col]
                if piece and piece.color == opponent_color:
                    # Для короля используем отдельную логику
                    if isinstance(piece, King):
                        for dr in [-1, 0, 1]:
                            for dc in [-1, 0, 1]:
                                if dr == 0 and dc == 0:
                                    continue
                                nr, nc = row + dr, col + dc
                                if 0 <= nr < 8 and 0 <= nc < 8:
                                    attacked_squares.add((nr, nc))
                    else:
                        for move in piece.get_possible_moves(self.board):
                            attacked_squares.add(move)

        # Помечаем фигуры текущего цвета, стоящие на атакованных клетках
        for row in range(8):
            for col in range(8):
                piece = self.board.grid[row][col]
                if piece and piece.color == current_color and (row, col) in attacked_squares:
                    self.threatened_squares.add((row, col))

    def draw_board(self):
        """Рисует шахматную доску"""
        for row in range(8):
            for col in range(8):
                color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
                pygame.draw.rect(self.screen, color,
                                 (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

        # Подсветка последнего хода
        if self.last_move:
            for pos in [self.last_move.from_pos, self.last_move.to_pos]:
                row, col = pos
                highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                highlight.fill(LAST_MOVE)
                self.screen.blit(highlight, (col * SQUARE_SIZE, row * SQUARE_SIZE))

        # Подсветка выбранной фигуры и возможных ходов
        if self.selected_square and not self.promotion_menu_active:
            row, col = self.selected_square
            highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            highlight.fill(HIGHLIGHT)
            self.screen.blit(highlight, (col * SQUARE_SIZE, row * SQUARE_SIZE))

            piece = self.board.grid[row][col]
            if piece:
                for move in piece.get_valid_moves(self.board):
                    m_row, m_col = move
                    if self.board.grid[m_row][m_col]:  # Клетка с фигурой (взятие)
                        highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                        highlight.fill(CAPTURE_MOVE)
                        self.screen.blit(highlight, (m_col * SQUARE_SIZE, m_row * SQUARE_SIZE))
                    else:  # Пустая клетка
                        center = (m_col * SQUARE_SIZE + SQUARE_SIZE // 2,
                                  m_row * SQUARE_SIZE + SQUARE_SIZE // 2)
                        pygame.draw.circle(self.screen, VALID_MOVE[:3], center, SQUARE_SIZE // 8)

        # Подсветка угроз
        if self.show_threats:
            self.calculate_threats()
            for row, col in self.threatened_squares:
                highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                highlight.fill(THREATENED_COLOR)
                self.screen.blit(highlight, (col * SQUARE_SIZE, row * SQUARE_SIZE))

            if self.board.is_in_check(self.board.current_turn):
                king_pos = self.board.get_king_position(self.board.current_turn)
                if king_pos:
                    row, col = king_pos
                    highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    highlight.fill(CHECK_COLOR)
                    self.screen.blit(highlight, (col * SQUARE_SIZE, row * SQUARE_SIZE))

    def draw_pieces(self):
        """Рисует фигуры на доске"""
        piece_size = SQUARE_SIZE - 40
        offset = 20

        for row in range(8):
            for col in range(8):
                piece = self.board.grid[row][col]
                if piece:
                    piece_key = f"{'w' if piece.color == WHITE_PIECE else 'b'}{piece.__class__.__name__}"

                    if piece_key in self.pieces:
                        x = col * SQUARE_SIZE + offset
                        y = row * SQUARE_SIZE + offset

                        # Немного затемняем фигуры под угрозой
                        if self.show_threats and (row, col) in self.threatened_squares:
                            darkened = self.pieces[piece_key].copy()
                            dark_surf = pygame.Surface((piece_size, piece_size), pygame.SRCALPHA)
                            dark_surf.fill((255, 100, 100, 100))
                            darkened.blit(dark_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                            self.screen.blit(darkened, (x, y))
                        else:
                            self.screen.blit(self.pieces[piece_key], (x, y))

    def draw_promotion_menu(self):
        """Рисует меню выбора фигуры при превращении пешки"""
        if not self.promotion_menu_active or not self.pending_promotion_to:
            return

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        menu_width = SQUARE_SIZE * 3
        menu_height = SQUARE_SIZE * 4 + 60
        menu_x = WIDTH // 2 - menu_width // 2
        menu_y = HEIGHT // 2 - menu_height // 2

        pygame.draw.rect(self.screen, (40, 40, 50), (menu_x, menu_y, menu_width, menu_height), border_radius=10)
        pygame.draw.rect(self.screen, WHITE, (menu_x, menu_y, menu_width, menu_height), 3, border_radius=10)

        font = pygame.font.SysFont('arial', 28, bold=True)
        title = font.render("Выберите фигуру:", True, WHITE)
        self.screen.blit(title, (menu_x + menu_width // 2 - title.get_width() // 2, menu_y + 10))

        options = [
            (Queen, '♕', 'Ферзь'),
            (Rook, '♖', 'Ладья'),
            (Bishop, '♗', 'Слон'),
            (Knight, '♘', 'Конь')
        ]

        mouse_pos = pygame.mouse.get_pos()
        color = self.board.current_turn
        color_char = 'w' if color == WHITE_PIECE else 'b'

        # Создаем временную поверхность для предпросмотра
        temp_font = pygame.font.SysFont('segoeui', 64)

        for i, (piece_class, symbol, piece_name) in enumerate(options):
            y = menu_y + 50 + i * (SQUARE_SIZE + 10)
            rect = pygame.Rect(menu_x + 10, y, menu_width - 20, SQUARE_SIZE)

            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (80, 80, 100), rect, border_radius=5)
            else:
                pygame.draw.rect(self.screen, (60, 60, 70), rect, border_radius=5)

            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=5)

            # Рисуем символ фигуры
            text_color = BLACK if color == WHITE_PIECE else WHITE
            text = temp_font.render(symbol, True, text_color)
            self.screen.blit(text, (menu_x + 30, y + 10))

            font_small = pygame.font.SysFont('arial', 20)
            name = font_small.render(piece_name, True, WHITE)
            self.screen.blit(name, (menu_x + SQUARE_SIZE + 30, y + SQUARE_SIZE // 2 - 10))

    def draw_info_panel(self):
        """Рисует информационную панель справа"""
        panel_x = WIDTH + 10
        font = pygame.font.SysFont('arial', 22)

        info_lines = [
            f"Ход: {'белых' if self.board.current_turn == WHITE_PIECE else 'черных'}",
            f"Ходов: {len(self.board.move_history)}",
            "",
            "Управление:",
            "U - отменить ход",
            "T - подсветка угроз",
            "R - новая игра",
            "ESC - выход",
            ""
        ]

        if self.show_threats:
            self.calculate_threats()
            threats_count = len(self.threatened_squares)
            info_lines.append(f"Фигур под угрозой: {threats_count}")

            if self.board.is_in_check(self.board.current_turn):
                info_lines.append("ШАХ королю!")

        info_lines.append("")

        if self.board.is_checkmate():
            winner = "Черные" if self.board.current_turn == WHITE_PIECE else "Белые"
            status = f"МАТ! {winner} победили"
            color = (255, 50, 50)
        elif self.board.is_stalemate():
            status = "ПАТ"
            color = (255, 200, 50)
        elif self.board.is_in_check(self.board.current_turn):
            status = "ШАХ"
            color = (255, 150, 50)
        else:
            status = "Игра продолжается"
            color = (200, 200, 200)

        info_lines.append(status)

        for i, line in enumerate(info_lines):
            if "Фигур под угрозой:" in line:
                text_color = (255, 150, 0)
            elif "ШАХ королю!" in line:
                text_color = (255, 50, 50)
            elif line == status:
                text_color = color
            else:
                text_color = WHITE

            text = font.render(line, True, text_color)
            self.screen.blit(text, (panel_x, 30 + i * 30))

    def handle_click(self, pos):
        """Обрабатывает клики мыши"""
        if self.promotion_menu_active:
            self.handle_promotion_click(pos)
            return

        x, y = pos
        if x >= WIDTH:
            return

        col, row = x // SQUARE_SIZE, y // SQUARE_SIZE
        if not (0 <= col < 8 and 0 <= row < 8):
            return

        clicked_pos = (row, col)

        if self.selected_square is None:
            # Выбираем фигуру
            piece = self.board.grid[row][col]
            if piece and piece.color == self.board.current_turn:
                self.selected_square = clicked_pos
        else:
            # Пытаемся сделать ход
            piece = self.board.grid[self.selected_square[0]][self.selected_square[1]]

            if piece:
                valid_moves = piece.get_valid_moves(self.board)

                if clicked_pos in valid_moves:
                    # Проверка на превращение пешки
                    if isinstance(piece, Pawn):
                        if (piece.color == WHITE_PIECE and clicked_pos[0] == 0) or \
                                (piece.color == BLACK_PIECE and clicked_pos[0] == 7):
                            self.promotion_menu_active = True
                            self.pending_promotion_from = self.selected_square
                            self.pending_promotion_to = clicked_pos
                            return

                    # Обычный ход
                    move = self.board.make_move(self.selected_square, clicked_pos)
                    if move:
                        self.last_move = move
                        self.selected_square = None
                        self.load_pieces()  # Обновляем изображения
                    else:
                        self.selected_square = None
                elif clicked_pos == self.selected_square:
                    self.selected_square = None
                else:
                    # Проверяем, может быть кликнули на другую свою фигуру
                    new_piece = self.board.grid[row][col]
                    if new_piece and new_piece.color == self.board.current_turn:
                        self.selected_square = clicked_pos
                    else:
                        self.selected_square = None

    def handle_promotion_click(self, pos):
        """Обрабатывает клики в меню превращения"""
        if not self.promotion_menu_active:
            return

        x, y = pos

        menu_width = SQUARE_SIZE * 3
        menu_height = SQUARE_SIZE * 4 + 60
        menu_x = WIDTH // 2 - menu_width // 2
        menu_y = HEIGHT // 2 - menu_height // 2

        if not (menu_x <= x <= menu_x + menu_width and menu_y <= y <= menu_y + menu_height):
            self.promotion_menu_active = False
            self.pending_promotion_from = None
            self.pending_promotion_to = None
            return

        options = [QUEEN, ROOK, BISHOP, KNIGHT]

        for i, promotion_type in enumerate(options):
            option_y = menu_y + 50 + i * (SQUARE_SIZE + 10)
            option_rect = pygame.Rect(menu_x + 10, option_y, menu_width - 20, SQUARE_SIZE)

            if option_rect.collidepoint(x, y):
                move = self.board.make_move(
                    self.pending_promotion_from,
                    self.pending_promotion_to,
                    promotion=promotion_type
                )

                if move:
                    self.last_move = move
                    self.load_pieces()

                self.promotion_menu_active = False
                self.pending_promotion_from = None
                self.pending_promotion_to = None
                self.selected_square = None
                return

    def undo_move(self):
        """Отменяет последний ход (упрощенная версия)"""
        if len(self.board.move_history) > 0:
            # Просто пересоздаем доску (для простоты)
            self.board = Board()
            self.board.current_turn = WHITE_PIECE
            self.board.move_history = []
            self.last_move = None
            self.selected_square = None
            self.load_pieces()

    def run(self):
        """Главный игровой цикл"""
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif event.key == pygame.K_u and not self.promotion_menu_active:
                        self.undo_move()

                    elif event.key == pygame.K_t and not self.promotion_menu_active:
                        self.show_threats = not self.show_threats
                        if self.show_threats:
                            self.calculate_threats()

                    elif event.key == pygame.K_r and not self.promotion_menu_active:
                        self.board = Board()
                        self.selected_square = None
                        self.last_move = None
                        self.show_threats = False
                        self.load_pieces()

            self.screen.fill((30, 30, 30))
            self.draw_board()
            self.draw_pieces()
            self.draw_promotion_menu()
            self.draw_info_panel()

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()


def main():
    # Запуск pygame-версии шахмат (вариант друга)
    screen = pygame.display.set_mode((WIDTH + 300, HEIGHT))
    pygame.display.set_caption("Шахматы")
    game = ChessGame(screen)
    game.run()


if __name__ == "__main__":
    main()
