import pygame
import sys
import math

# ----------------------------------------------------------------------
# Классы фигур
# ----------------------------------------------------------------------
class Piece:
    def __init__(self, color, x, y, z, symbol):
        self.color = color      # 'green', 'gray', 'white'
        self.x = x
        self.y = y
        self.z = z
        self.symbol = symbol    # 'P','N','B','R','Q','K'

    def get_moves(self, board, occupied):
        """Будет переопределён в подклассах."""
        return []

    def __repr__(self):
        return f"{self.color[0]}{self.symbol}"

class Pawn(Piece):
    def __init__(self, color, x, y, z):
        super().__init__(color, x, y, z, 'P')

    def get_moves(self, board, occupied):
        moves = []
        # Направление вперёд для каждого цвета (циклически симметричные)
        forward_map = {
            'green': (1, 0, -1),
            'gray': (0, -1, 1),
            'white': (-1, 1, 0)
        }
        # Направления взятия (влево и вправо) для каждого цвета
        capture_map = {
            'green': [(1, -1, 0), (0, 1, -1)],
            'gray': [(-1, 0, 1), (1, -1, 0)],
            'white': [(0, 1, -1), (-1, 0, 1)]
        }
        fdx, fdy, fdz = forward_map[self.color]
        # Ход на одну клетку вперёд
        nx, ny, nz = self.x + fdx, self.y + fdy, self.z + fdz
        if board.is_on_board(nx, ny, nz) and (nx, ny, nz) not in occupied:
            moves.append((nx, ny, nz))

        # Взятие
        for cdx, cdy, cdz in capture_map[self.color]:
            nx, ny, nz = self.x + cdx, self.y + cdy, self.z + cdz
            if board.is_on_board(nx, ny, nz):
                if (nx, ny, nz) in occupied and occupied[(nx, ny, nz)].color != self.color:
                    moves.append((nx, ny, nz))
        return moves

class Knight(Piece):
    def __init__(self, color, x, y, z):
        super().__init__(color, x, y, z, 'N')

    def get_moves(self, board, occupied):
        moves = []
        # 12 направлений коня (2 шага в одном ладейном + 1 в соседнем)
        knight_dirs = [
            (3, -2, -1), (2, -3, 1), (3, -1, -2), (2, 1, -3),
            (1, 2, -3), (-1, 3, -2), (-2, 3, -1), (-3, 2, 1),
            (-3, 1, 2), (-2, -1, 3), (-1, -2, 3), (1, -3, 2)
        ]
        for dx, dy, dz in knight_dirs:
            nx, ny, nz = self.x + dx, self.y + dy, self.z + dz
            if board.is_on_board(nx, ny, nz):
                if (nx, ny, nz) not in occupied or occupied[(nx, ny, nz)].color != self.color:
                    moves.append((nx, ny, nz))
        return moves

class Bishop(Piece):
    def __init__(self, color, x, y, z):
        super().__init__(color, x, y, z, 'B')

    def get_moves(self, board, occupied):
        moves = []
        # Шесть диагональных (слоновьих) направлений
        directions = [
            (2, -1, -1), (1, 1, -2), (-1, 2, -1),
            (-2, 1, 1), (-1, -1, 2), (1, -2, 1)
        ]
        for dx, dy, dz in directions:
            x, y, z = self.x, self.y, self.z
            while True:
                x += dx
                y += dy
                z += dz
                if not board.is_on_board(x, y, z):
                    break
                if (x, y, z) in occupied:
                    if occupied[(x, y, z)].color != self.color:
                        moves.append((x, y, z))
                    break
                else:
                    moves.append((x, y, z))
        return moves

class Rook(Piece):
    def __init__(self, color, x, y, z):
        super().__init__(color, x, y, z, 'R')

    def get_moves(self, board, occupied):
        moves = []
        # Шесть ладейных направлений (через стороны)
        directions = [
            (1, -1, 0), (1, 0, -1), (0, 1, -1),
            (-1, 1, 0), (-1, 0, 1), (0, -1, 1)
        ]
        for dx, dy, dz in directions:
            x, y, z = self.x, self.y, self.z
            while True:
                x += dx
                y += dy
                z += dz
                if not board.is_on_board(x, y, z):
                    break
                if (x, y, z) in occupied:
                    if occupied[(x, y, z)].color != self.color:
                        moves.append((x, y, z))
                    break
                else:
                    moves.append((x, y, z))
        return moves

class Queen(Piece):
    def __init__(self, color, x, y, z):
        super().__init__(color, x, y, z, 'Q')

    def get_moves(self, board, occupied):
        moves = []
        # Ладейные направления
        rook_dirs = [
            (1, -1, 0), (1, 0, -1), (0, 1, -1),
            (-1, 1, 0), (-1, 0, 1), (0, -1, 1)
        ]
        # Слоновьи направления
        bishop_dirs = [
            (2, -1, -1), (1, 1, -2), (-1, 2, -1),
            (-2, 1, 1), (-1, -1, 2), (1, -2, 1)
        ]
        for directions in (rook_dirs, bishop_dirs):
            for dx, dy, dz in directions:
                x, y, z = self.x, self.y, self.z
                while True:
                    x += dx
                    y += dy
                    z += dz
                    if not board.is_on_board(x, y, z):
                        break
                    if (x, y, z) in occupied:
                        if occupied[(x, y, z)].color != self.color:
                            moves.append((x, y, z))
                        break
                    else:
                        moves.append((x, y, z))
        return moves

class King(Piece):
    def __init__(self, color, x, y, z):
        super().__init__(color, x, y, z, 'K')

    def get_moves(self, board, occupied):
        moves = []
        # Шесть ладейных направлений на одну клетку
        directions = [
            (1, -1, 0), (1, 0, -1), (0, 1, -1),
            (-1, 1, 0), (-1, 0, 1), (0, -1, 1)
        ]
        for dx, dy, dz in directions:
            nx, ny, nz = self.x + dx, self.y + dy, self.z + dz
            if board.is_on_board(nx, ny, nz):
                if (nx, ny, nz) not in occupied or occupied[(nx, ny, nz)].color != self.color:
                    moves.append((nx, ny, nz))
        return moves


# ----------------------------------------------------------------------
# Класс доски
# ----------------------------------------------------------------------
class Board:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.BACKGROUND = (30, 30, 30)
        # цвета для заливки гексов
        self.COLORS = [(80, 80, 80), (34, 139, 34), (245, 245, 220)]
        self.LINE_COLOR = (0, 0, 0)
        # цвета игроков
        self.PLAYER_COLORS = {
            'green': (0, 255, 0),
            'gray': (128, 128, 128),
            'white': (255, 255, 255)
        }

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Гексагональные шахматы (3 игрока)")
        self.clock = pygame.time.Clock()

        self.SQRT3 = math.sqrt(3)
        # Вершины направлены вверх (pointy-top)
        self.ANGLES = [math.pi/2 + i * math.pi/3 for i in range(6)]

        # Границы доски (из первого кода)
        self.x_min, self.x_max = -7, 8
        self.y_min, self.y_max = -8, 7
        self.z_min, self.z_max = -7, 8

        # Генерация всех гексов, удовлетворяющих условию z = -x-y
        self.hexes = []
        for x in range(self.x_min, self.x_max + 1):
            for y in range(self.y_min, self.y_max + 1):
                z = -x - y
                if self.z_min <= z <= self.z_max:
                    self.hexes.append((x, y, z))

        # Автоматический расчёт масштаба и смещения
        self._compute_scale_and_offset()
        # Вывод длин сторон для информации
        self._print_side_lengths()

    def _compute_scale_and_offset(self):
        """Вычисляет SIDE и offset_x, offset_y так, чтобы доска помещалась в окно."""
        # Предварительные координаты (без масштаба)
        coords = []
        for (x, y, z) in self.hexes:
            q, r = x, z
            px = self.SQRT3 * (q + r / 2.0)
            py = 1.5 * r
            coords.append((px, py))

        xs = [p[0] for p in coords]
        ys = [p[1] for p in coords]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        board_width = (max_x - min_x) + 2
        board_height = (max_y - min_y) + 2

        MARGIN = 20
        available_width = self.WIDTH - 2 * MARGIN
        available_height = self.HEIGHT - 2 * MARGIN

        scale_x = available_width / board_width
        scale_y = available_height / board_height
        self.SIDE = min(scale_x, scale_y)

        # Пересчёт с реальным SIDE
        coords2 = []
        for (x, y, z) in self.hexes:
            q, r = x, z
            px = self.SIDE * self.SQRT3 * (q + r / 2.0)
            py = self.SIDE * 1.5 * r
            coords2.append((px, py))

        xs2 = [p[0] for p in coords2]
        ys2 = [p[1] for p in coords2]
        min_x2, max_x2 = min(xs2), max(xs2)
        min_y2, max_y2 = min(ys2), max(ys2)

        self.offset_x = self.WIDTH // 2 - (min_x2 + max_x2) // 2
        self.offset_y = self.HEIGHT // 2 - (min_y2 + max_y2) // 2

    def _print_side_lengths(self):
        """Подсчитывает количество гексов на каждой границе и выводит на печать."""
        cnt_xmin = sum(1 for (x, y, z) in self.hexes if x == self.x_min)
        cnt_xmax = sum(1 for (x, y, z) in self.hexes if x == self.x_max)
        cnt_ymin = sum(1 for (x, y, z) in self.hexes if y == self.y_min)
        cnt_ymax = sum(1 for (x, y, z) in self.hexes if y == self.y_max)
        cnt_zmin = sum(1 for (x, y, z) in self.hexes if z == self.z_min)
        cnt_zmax = sum(1 for (x, y, z) in self.hexes if z == self.z_max)
        print("Длины сторон (xmin, xmax, ymin, ymax, zmin, zmax):",
              (cnt_xmin, cnt_xmax, cnt_ymin, cnt_ymax, cnt_zmin, cnt_zmax))

    def is_on_board(self, x, y, z):
        """Проверяет, находится ли клетка с данными координатами на доске."""
        return (x, y, z) in self.hexes

    def cube_to_pixel(self, x, y, z):
        """Преобразует кубические координаты в экранные."""
        q, r = x, z
        px = self.SIDE * self.SQRT3 * (q + r / 2.0) + self.offset_x
        py = self.SIDE * 1.5 * r + self.offset_y
        return int(px), int(py)

    def get_hex_at(self, screen_x, screen_y):
        """Возвращает координаты гекса, на который пришёлся клик, или None."""
        # Перебираем все гексы и ищем ближайший центр в пределах радиуса
        min_dist = float('inf')
        best_hex = None
        for (x, y, z) in self.hexes:
            cx, cy = self.cube_to_pixel(x, y, z)
            dist = math.hypot(screen_x - cx, screen_y - cy)
            if dist < self.SIDE and dist < min_dist:
                min_dist = dist
                best_hex = (x, y, z)
        return best_hex

    def draw_hex(self, surface, x, y, z, color):
        """Рисует один гекс с заданным цветом заливки."""
        cx, cy = self.cube_to_pixel(x, y, z)
        vertices = []
        for angle in self.ANGLES:
            vx = cx + self.SIDE * math.cos(angle)
            vy = cy + self.SIDE * math.sin(angle)
            vertices.append((vx, vy))
        pygame.draw.polygon(surface, color, vertices)
        pygame.draw.polygon(surface, self.LINE_COLOR, vertices, 2)

    def draw_piece(self, surface, piece):
        """Рисует фигуру в центре гекса."""
        cx, cy = self.cube_to_pixel(piece.x, piece.y, piece.z)
        color = self.PLAYER_COLORS[piece.color]
        radius = int(self.SIDE * 0.45)
        pygame.draw.circle(surface, color, (cx, cy), radius)
        pygame.draw.circle(surface, self.LINE_COLOR, (cx, cy), radius, 2)
        font = pygame.font.Font(None, int(radius * 1.5))
        text = font.render(piece.symbol, True, self.LINE_COLOR)
        text_rect = text.get_rect(center=(cx, cy))
        surface.blit(text, text_rect)


# ----------------------------------------------------------------------
# Функция создания начальной расстановки (из первого кода)
# ----------------------------------------------------------------------
def create_initial_pieces(board):
    """Возвращает список фигур, расставленных на трёх сторонах доски."""
    pieces = []

    # ----- Зелёные (по оси z) -----
    z1 = board.z_max
    z2 = board.z_max - 1
    z3 = board.z_max - 2

    # первая линия (тяжёлые фигуры)
    green_row1 = [h for h in board.hexes if h[2] == z1]
    green_row1.sort(key=lambda h: h[0])  # сортировка по x
    green_figures = ['R', 'B', 'N', 'Q', 'K', 'N', 'B', 'R']
    for i, (x, y, z) in enumerate(green_row1):
        ptype = green_figures[i]
        if ptype == 'R':
            pieces.append(Rook('green', x, y, z))
        elif ptype == 'B':
            pieces.append(Bishop('green', x, y, z))
        elif ptype == 'N':
            pieces.append(Knight('green', x, y, z))
        elif ptype == 'Q':
            pieces.append(Queen('green', x, y, z))
        elif ptype == 'K':
            pieces.append(King('green', x, y, z))

    # вторая линия (пешки + слон в центре)
    green_row2 = [h for h in board.hexes if h[2] == z2]
    green_row2.sort(key=lambda h: h[0])
    N2 = len(green_row2)
    center = N2 // 2
    for i, (x, y, z) in enumerate(green_row2):
        if i == center:
            pieces.append(Bishop('green', x, y, z))
        else:
            pieces.append(Pawn('green', x, y, z))

    # третья линия (пешки, кроме крайних)
    green_row3 = [h for h in board.hexes if h[2] == z3]
    green_row3.sort(key=lambda h: h[0])
    N3 = len(green_row3)
    for i, (x, y, z) in enumerate(green_row3):
        if i == 0 or i == N3 - 1:
            continue
        pieces.append(Pawn('green', x, y, z))

    # ----- Серые (по оси y) -----
    y1 = board.y_max
    y2 = board.y_max - 1
    y3 = board.y_max - 2

    gray_row1 = [h for h in board.hexes if h[1] == y1]
    gray_row1.sort(key=lambda h: h[0])
    gray_figures = ['R', 'B', 'N', 'Q', 'K', 'N', 'B', 'R']
    for i, (x, y, z) in enumerate(gray_row1):
        ptype = gray_figures[i]
        if ptype == 'R':
            pieces.append(Rook('gray', x, y, z))
        elif ptype == 'B':
            pieces.append(Bishop('gray', x, y, z))
        elif ptype == 'N':
            pieces.append(Knight('gray', x, y, z))
        elif ptype == 'Q':
            pieces.append(Queen('gray', x, y, z))
        elif ptype == 'K':
            pieces.append(King('gray', x, y, z))

    gray_row2 = [h for h in board.hexes if h[1] == y2]
    gray_row2.sort(key=lambda h: h[0])
    N2 = len(gray_row2)
    center = N2 // 2
    for i, (x, y, z) in enumerate(gray_row2):
        if i == center:
            pieces.append(Bishop('gray', x, y, z))
        else:
            pieces.append(Pawn('gray', x, y, z))

    gray_row3 = [h for h in board.hexes if h[1] == y3]
    gray_row3.sort(key=lambda h: h[0])
    N3 = len(gray_row3)
    for i, (x, y, z) in enumerate(gray_row3):
        if i == 0 or i == N3 - 1:
            continue
        pieces.append(Pawn('gray', x, y, z))

    # ----- Белые (по оси x) -----
    x1 = board.x_max
    x2 = board.x_max - 1
    x3 = board.x_max - 2

    white_row1 = [h for h in board.hexes if h[0] == x1]
    white_row1.sort(key=lambda h: -h[1])  # сортировка по убыванию y
    white_figures = ['R', 'B', 'N', 'Q', 'K', 'N', 'B', 'R']
    for i, (x, y, z) in enumerate(white_row1):
        ptype = white_figures[i]
        if ptype == 'R':
            pieces.append(Rook('white', x, y, z))
        elif ptype == 'B':
            pieces.append(Bishop('white', x, y, z))
        elif ptype == 'N':
            pieces.append(Knight('white', x, y, z))
        elif ptype == 'Q':
            pieces.append(Queen('white', x, y, z))
        elif ptype == 'K':
            pieces.append(King('white', x, y, z))

    white_row2 = [h for h in board.hexes if h[0] == x2]
    white_row2.sort(key=lambda h: -h[1])
    N2 = len(white_row2)
    center = N2 // 2
    for i, (x, y, z) in enumerate(white_row2):
        if i == center:
            pieces.append(Bishop('white', x, y, z))
        else:
            pieces.append(Pawn('white', x, y, z))

    white_row3 = [h for h in board.hexes if h[0] == x3]
    white_row3.sort(key=lambda h: -h[1])
    N3 = len(white_row3)
    for i, (x, y, z) in enumerate(white_row3):
        if i == 0 or i == N3 - 1:
            continue
        pieces.append(Pawn('white', x, y, z))

    return pieces


# ----------------------------------------------------------------------
# Главная функция
# ----------------------------------------------------------------------
def main():
    board = Board()
    pieces = create_initial_pieces(board)

    # Словарь занятых клеток для быстрой проверки
    occupied = {(p.x, p.y, p.z): p for p in pieces}

    # Состояние игры
    current_player = 'green'  # порядок: green -> gray -> white -> green...
    selected_piece = None
    possible_moves = []

    # Цвета для подсветки
    HIGHLIGHT_COLOR = (255, 255, 0, 100)  # жёлтый полупрозрачный
    SELECT_COLOR = (0, 255, 255, 100)     # голубой для выбранной фигуры

    def next_player():
        nonlocal current_player
        if current_player == 'green':
            current_player = 'gray'
        elif current_player == 'gray':
            current_player = 'white'
        else:
            current_player = 'green'

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Левый клик мыши
                mouse_x, mouse_y = pygame.mouse.get_pos()
                coord = board.get_hex_at(mouse_x, mouse_y)
                if coord:
                    x, y, z = coord
                    print(f"Clicked on hex ({x},{y},{z})")
                    if selected_piece is None:
                        # Пытаемся выбрать фигуру текущего игрока
                        if (x, y, z) in occupied and occupied[(x, y, z)].color == current_player:
                            selected_piece = occupied[(x, y, z)]
                            possible_moves = selected_piece.get_moves(board, occupied)
                            print(f"Selected {selected_piece} with {len(possible_moves)} moves")
                    else:
                        # Уже есть выбранная фигура
                        if (x, y, z) in possible_moves:
                            # Выполняем ход
                            target = (x, y, z)
                            # Если на целевой клетке есть фигура противника, удаляем её
                            if target in occupied:
                                captured = occupied[target]
                                pieces.remove(captured)
                                del occupied[target]
                                print(f"Captured {captured}")
                            # Перемещаем выбранную фигуру
                            old_coord = (selected_piece.x, selected_piece.y, selected_piece.z)
                            del occupied[old_coord]
                            selected_piece.x, selected_piece.y, selected_piece.z = target
                            occupied[target] = selected_piece
                            print(f"Moved {selected_piece} to {target}")
                            # Снимаем выделение и переключаем игрока
                            selected_piece = None
                            possible_moves = []
                            next_player()
                        elif (x, y, z) in occupied and occupied[(x, y, z)].color == current_player:
                            # Выбираем другую свою фигуру
                            selected_piece = occupied[(x, y, z)]
                            possible_moves = selected_piece.get_moves(board, occupied)
                            print(f"Switched to {selected_piece} with {len(possible_moves)} moves")
                        else:
                            # Клик в недопустимое место — снимаем выделение
                            selected_piece = None
                            possible_moves = []
                            print("Deselected")

        # Отрисовка
        board.screen.fill(board.BACKGROUND)

        # Рисуем гексы
        for x, y, z in board.hexes:
            color_index = (x + 2 * y) % 3
            board.draw_hex(board.screen, x, y, z, board.COLORS[color_index])

        # Подсветка возможных ходов (полупрозрачные круги)
        for (mx, my, mz) in possible_moves:
            cx, cy = board.cube_to_pixel(mx, my, mz)
            # Создаём поверхность для прозрачности
            s = pygame.Surface((board.SIDE*2, board.SIDE*2), pygame.SRCALPHA)
            pygame.draw.circle(s, HIGHLIGHT_COLOR, (int(board.SIDE), int(board.SIDE)), int(board.SIDE*0.5))
            board.screen.blit(s, (cx - board.SIDE, cy - board.SIDE))

        # Подсветка выбранной фигуры
        if selected_piece:
            cx, cy = board.cube_to_pixel(selected_piece.x, selected_piece.y, selected_piece.z)
            s = pygame.Surface((board.SIDE*2, board.SIDE*2), pygame.SRCALPHA)
            pygame.draw.circle(s, SELECT_COLOR, (int(board.SIDE), int(board.SIDE)), int(board.SIDE*0.55))
            board.screen.blit(s, (cx - board.SIDE, cy - board.SIDE))

        # Рисуем фигуры
        for piece in pieces:
            board.draw_piece(board.screen, piece)

        # Отображение текущего игрока (просто текст в углу)
        font = pygame.font.Font(None, 36)
        text = font.render(f"Ход: {current_player}", True, (255, 255, 255))
        board.screen.blit(text, (10, 10))

        pygame.display.flip()
        board.clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()