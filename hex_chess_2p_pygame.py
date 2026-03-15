import pygame
import sys
import math

class Board:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 1200, 900
        self.SIDE = 36

        self.BACKGROUND = (24, 28, 36)
        self.COLORS = [
            (238, 220, 190),
            (188, 154, 122),
            (132, 104, 77)
        ]
        self.LINE_COLOR = (45, 45, 50)

        self.PLAYER_COLORS = {
            'white': (245, 245, 245),
            'black': (35, 35, 35)
        }

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Hex Chess — 2 Players")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 40)
        self.small_font = pygame.font.Font(None, 28)
        
        self.SQRT3 = math.sqrt(3)
        self.ANGLES = [i * math.pi / 3 for i in range(6)]
        
        self.hexes = []
        for x in range(-5, 6):
            for y in range(-5, 6):
                z = -x - y
                if abs(z) <= 5:
                    self.hexes.append((x, y, z))
        
        self.offset_x = self.WIDTH // 2
        self.offset_y = self.HEIGHT // 2
        self.pieces = []
        self.game_over = False
        self.winner = None

    def cube_to_pixel(self, x, y, z):
        q = x
        r = z
        px = self.SIDE * 1.5 * q + self.offset_x
        py = self.SIDE * self.SQRT3 * (r + q / 2.0) + self.offset_y
        return int(px), int(py)

    def pixel_to_cube(self, px, py):
        x = (px - self.offset_x) / (self.SIDE * 1.5)
        z = (py - self.offset_y) / (self.SIDE * self.SQRT3) - x / 2.0
        y = -x - z
        return x, y, z

    def cube_round(self, x, y, z):
        rx = round(x)
        ry = round(y)
        rz = round(z)

        x_diff = abs(rx - x)
        y_diff = abs(ry - y)
        z_diff = abs(rz - z)

        if x_diff > y_diff and x_diff > z_diff:
            rx = -ry - rz
        elif y_diff > z_diff:
            ry = -rx - rz
        else:
            rz = -rx - ry
        return int(rx), int(ry), int(rz)

    def get_hex_at(self, px, py):
        fx, fy, fz = self.pixel_to_cube(px, py)
        x, y, z = self.cube_round(fx, fy, fz)
        if (x, y, z) in self.hexes:
            return (x, y, z)
        return None

    def get_piece_at(self, x, y, z):
        for p in self.pieces:
            if p.x == x and p.y == y and p.z == z:
                return p
        return None

    def draw_hex(self, surface, x, y, z, color):
        cx, cy = self.cube_to_pixel(x, y, z)
        vertices = []
        for angle in self.ANGLES:
            vx = cx + self.SIDE * math.cos(angle)
            vy = cy + self.SIDE * math.sin(angle)
            vertices.append((vx, vy))
        pygame.draw.polygon(surface, color, vertices)
        pygame.draw.polygon(surface, self.LINE_COLOR, vertices, 2)

    def draw_piece(self, surface, piece):
        cx, cy = self.cube_to_pixel(piece.x, piece.y, piece.z)
        color = self.PLAYER_COLORS[piece.color]
        radius = int(self.SIDE * 0.42)

        pygame.draw.circle(surface, color, (cx, cy), radius)
        pygame.draw.circle(surface, (20, 20, 20), (cx, cy), radius, 3)

        font = pygame.font.Font(None, int(radius * 1.6))
        text_color = (250, 250, 250) if piece.color == 'black' else (15, 15, 15)
        text = font.render(piece.symbol, True, text_color)
        text_rect = text.get_rect(center=(cx, cy))
        surface.blit(text, text_rect)

    def draw_highlight(self, surface, x, y, z, color=(80, 170, 255, 110)):
        cx, cy = self.cube_to_pixel(x, y, z)
        s = pygame.Surface((self.SIDE * 2, self.SIDE * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (self.SIDE, self.SIDE), int(self.SIDE * 0.32))
        surface.blit(s, (cx - self.SIDE, cy - self.SIDE))

    def draw_status_panel(self, current_turn, status_text=""):
        panel_rect = pygame.Rect(0, 0, self.WIDTH, 70)
        pygame.draw.rect(self.screen, (18, 21, 28), panel_rect)

        turn_label = "Белые" if current_turn == "white" else "Чёрные"
        title = self.font.render(f"Ход: {turn_label}", True, (245, 245, 245))
        self.screen.blit(title, (20, 15))

        if status_text:
            msg = self.small_font.render(status_text, True, (210, 210, 210))
            self.screen.blit(msg, (20, 42))

    def draw_text(self, text, y_offset=0, color=(255,255,255)):
        text_surf = self.font.render(text, True, color)
        text_rect = text_surf.get_rect(center=(self.WIDTH//2, 30 + y_offset))
        self.screen.blit(text_surf, text_rect)

    # Новые методы для проверки шаха и мата
    def find_king(self, color):
        for piece in self.pieces:
            if piece.color == color and isinstance(piece, King):
                return piece
        return None

    def is_square_attacked(self, x, y, z, attacking_color):
        for piece in self.pieces:
            if piece.color == attacking_color:
                moves = piece.get_moves(self)  # все возможные ходы (включая взятие)
                if (x, y, z) in moves:
                    return True
        return False

    def is_in_check(self, color):
        king = self.find_king(color)
        if not king:
            return False
        opponent = 'black' if color == 'white' else 'white'
        return self.is_square_attacked(king.x, king.y, king.z, opponent)

    def move_leaves_king_in_check(self, piece, dest_x, dest_y, dest_z):
        # Сохраняем исходные координаты
        orig_x, orig_y, orig_z = piece.x, piece.y, piece.z
        # Находим фигуру на клетке назначения (если есть)
        captured = None
        for p in self.pieces:
            if p.x == dest_x and p.y == dest_y and p.z == dest_z and p != piece:
                captured = p
                break
        if captured:
            self.pieces.remove(captured)
        # Перемещаем фигуру
        piece.x, piece.y, piece.z = dest_x, dest_y, dest_z
        # Проверяем, остался ли король под шахом
        in_check = self.is_in_check(piece.color)
        # Откатываем изменения
        piece.x, piece.y, piece.z = orig_x, orig_y, orig_z
        if captured:
            self.pieces.append(captured)
        return in_check

    def get_legal_moves(self, piece):
        all_moves = piece.get_moves(self)
        legal = []
        for move in all_moves:
            if not self.move_leaves_king_in_check(piece, *move):
                legal.append(move)
        return legal

    def has_any_legal_moves(self, color):
        for piece in self.pieces:
            if piece.color == color:
                if self.get_legal_moves(piece):
                    return True
        return False

class Piece:
    def __init__(self, color, x, y, z, symbol):
        self.color = color
        self.x = x
        self.y = y
        self.z = z
        self.symbol = symbol

    def get_moves(self, board):
        return []

    def __repr__(self):
        return f"{self.color[0]}{self.symbol}"

class Pawn(Piece):
    def __init__(self, color, x, y, z):
        super().__init__(color, x, y, z, 'P')
        self.has_moved = False

    def get_moves(self, board):
        moves = []
        if self.color == 'white':
            forward = (0, 1, -1)
            captures = [(-1, 2, -1), (1, 1, -2)]
        else:
            forward = (0, -1, 1)
            captures = [(1, -2, 1), (-1, -1, 2)]

        nx, ny, nz = self.x + forward[0], self.y + forward[1], self.z + forward[2]
        if (nx, ny, nz) in board.hexes and board.get_piece_at(nx, ny, nz) is None:
            moves.append((nx, ny, nz))
            if not self.has_moved:
                nx2, ny2, nz2 = self.x + 2*forward[0], self.y + 2*forward[1], self.z + 2*forward[2]
                if (nx2, ny2, nz2) in board.hexes and board.get_piece_at(nx2, ny2, nz2) is None:
                    moves.append((nx2, ny2, nz2))

        for dx, dy, dz in captures:
            nx, ny, nz = self.x + dx, self.y + dy, self.z + dz
            if (nx, ny, nz) in board.hexes:
                p = board.get_piece_at(nx, ny, nz)
                if p and p.color != self.color:
                    moves.append((nx, ny, nz))
        return moves

class Knight(Piece):
    def __init__(self, color, x, y, z):
        super().__init__(color, x, y, z, 'N')

    def get_moves(self, board):
        moves = []
        knight_dirs = [
            (1,2,-3), (1,-3,2), (2,1,-3), (2,-3,1), (-3,1,2), (-3,2,1),
            (-1,-2,3), (-1,3,-2), (-2,-1,3), (-2,3,-1), (3,-1,-2), (3,-2,-1)
        ]
        for dx, dy, dz in knight_dirs:
            nx, ny, nz = self.x + dx, self.y + dy, self.z + dz
            if (nx, ny, nz) in board.hexes:
                p = board.get_piece_at(nx, ny, nz)
                if p is None or p.color != self.color:
                    moves.append((nx, ny, nz))
        return moves

class Bishop(Piece):
    def __init__(self, color, x, y, z):
        super().__init__(color, x, y, z, 'B')

    def get_moves(self, board):
        moves = []
        diag_dirs = [
            (2,-1,-1), (-2,1,1),
            (-1,2,-1), (1,-2,1),
            (-1,-1,2), (1,1,-2)
        ]
        for dx, dy, dz in diag_dirs:
            step = 1
            while True:
                nx, ny, nz = self.x + step*dx, self.y + step*dy, self.z + step*dz
                if (nx, ny, nz) not in board.hexes:
                    break
                p = board.get_piece_at(nx, ny, nz)
                if p is None:
                    moves.append((nx, ny, nz))
                    step += 1
                elif p.color != self.color:
                    moves.append((nx, ny, nz))
                    break
                else:
                    break
        return moves

class Rook(Piece):
    def __init__(self, color, x, y, z):
        super().__init__(color, x, y, z, 'R')

    def get_moves(self, board):
        moves = []
        orth_dirs = [
            (1,-1,0), (-1,1,0),
            (1,0,-1), (-1,0,1),
            (0,1,-1), (0,-1,1)
        ]
        for dx, dy, dz in orth_dirs:
            step = 1
            while True:
                nx, ny, nz = self.x + step*dx, self.y + step*dy, self.z + step*dz
                if (nx, ny, nz) not in board.hexes:
                    break
                p = board.get_piece_at(nx, ny, nz)
                if p is None:
                    moves.append((nx, ny, nz))
                    step += 1
                elif p.color != self.color:
                    moves.append((nx, ny, nz))
                    break
                else:
                    break
        return moves

class Queen(Piece):
    def __init__(self, color, x, y, z):
        super().__init__(color, x, y, z, 'Q')

    def get_moves(self, board):
        moves = []
        all_dirs = [
            (1,-1,0), (-1,1,0),
            (1,0,-1), (-1,0,1),
            (0,1,-1), (0,-1,1),
            (2,-1,-1), (-2,1,1),
            (-1,2,-1), (1,-2,1),
            (-1,-1,2), (1,1,-2)
        ]
        for dx, dy, dz in all_dirs:
            step = 1
            while True:
                nx, ny, nz = self.x + step*dx, self.y + step*dy, self.z + step*dz
                if (nx, ny, nz) not in board.hexes:
                    break
                p = board.get_piece_at(nx, ny, nz)
                if p is None:
                    moves.append((nx, ny, nz))
                    step += 1
                elif p.color != self.color:
                    moves.append((nx, ny, nz))
                    break
                else:
                    break
        return moves

class King(Piece):
    def __init__(self, color, x, y, z):
        super().__init__(color, x, y, z, 'K')

    def get_moves(self, board):
        moves = []
        orth_dirs = [
            (1,-1,0), (-1,1,0),
            (1,0,-1), (-1,0,1),
            (0,1,-1), (0,-1,1)
        ]
        for dx, dy, dz in orth_dirs:
            nx, ny, nz = self.x + dx, self.y + dy, self.z + dz
            if (nx, ny, nz) in board.hexes:
                p = board.get_piece_at(nx, ny, nz)
                if p is None or p.color != self.color:
                    moves.append((nx, ny, nz))
        return moves

def create_initial_pieces():
    white_data = [
        (0, -5, 5, 'B'), (0, -4, 4, 'B'), (0, -3, 3, 'B'),
        (1, -5, 4, 'K'), (2, -5, 3, 'N'), (3, -5, 2, 'R'), (4, -5, 1, 'P'),
        (-1, -4, 5, 'Q'), (-2, -3, 5, 'N'), (-3, -2, 5, 'R'), (-4, -1, 5, 'P'),
        (3, -4, 1, 'P'), (-3, -1, 4, 'P'),
        (2, -3, 1, 'P'), (-2, -1, 3, 'P'),
        (1, -2, 1, 'P'), (-1, -1, 2, 'P'),
        (0, -1, 1, 'P')
    ]

    pieces = []
    for x, y, z, sym in white_data:
        if sym == 'P':
            pieces.append(Pawn('white', x, y, z))
        elif sym == 'N':
            pieces.append(Knight('white', x, y, z))
        elif sym == 'B':
            pieces.append(Bishop('white', x, y, z))
        elif sym == 'R':
            pieces.append(Rook('white', x, y, z))
        elif sym == 'Q':
            pieces.append(Queen('white', x, y, z))
        elif sym == 'K':
            pieces.append(King('white', x, y, z))

    for x, y, z, sym in white_data:
        if sym == 'P':
            pieces.append(Pawn('black', -x, -y, -z))
        elif sym == 'N':
            pieces.append(Knight('black', -x, -y, -z))
        elif sym == 'B':
            pieces.append(Bishop('black', -x, -y, -z))
        elif sym == 'R':
            pieces.append(Rook('black', -x, -y, -z))
        elif sym == 'Q':
            pieces.append(Queen('black', -x, -y, -z))
        elif sym == 'K':
            pieces.append(King('black', -x, -y, -z))

    return pieces

def main():
    board = Board()
    pieces = create_initial_pieces()
    board.pieces = pieces

    selected_piece = None
    possible_moves = []
    turn = "white"
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and not board.game_over
            ):
                mx, my = pygame.mouse.get_pos()
                hex_coord = board.get_hex_at(mx, my)

                if hex_coord is None:
                    selected_piece = None
                    possible_moves = []
                    continue

                hx, hy, hz = hex_coord
                piece_here = board.get_piece_at(hx, hy, hz)

                # если кликнули по доступному ходу — делаем ход
                if selected_piece is not None and (hx, hy, hz) in possible_moves:
                    if piece_here is not None:
                        board.pieces.remove(piece_here)

                    selected_piece.x = hx
                    selected_piece.y = hy
                    selected_piece.z = hz

                    if isinstance(selected_piece, Pawn):
                        selected_piece.has_moved = True

                    selected_piece = None
                    possible_moves = []

                    # меняем сторону
                    turn = "black" if turn == "white" else "white"

                    # проверяем окончание игры
                    if board.is_in_check(turn):
                        if not board.has_any_legal_moves(turn):
                            board.game_over = True
                            board.winner = "white" if turn == "black" else "black"
                    else:
                        if not board.has_any_legal_moves(turn):
                            board.game_over = True
                            board.winner = None  # пат

                else:
                    # выбор фигуры
                    if piece_here is not None and piece_here.color == turn:
                        selected_piece = piece_here
                        possible_moves = board.get_legal_moves(piece_here)
                    else:
                        selected_piece = None
                        possible_moves = []

        # ---------- ОТРИСОВКА ----------
        board.screen.fill(board.BACKGROUND)

        # доска
        for x, y, z in board.hexes:
            color_index = (x + 2 * y) % 3
            board.draw_hex(board.screen, x, y, z, board.COLORS[color_index])

        # подсветка выбранной фигуры
        if selected_piece is not None:
            board.draw_highlight(
                board.screen,
                selected_piece.x,
                selected_piece.y,
                selected_piece.z,
                (255, 196, 0, 120)
            )

        # подсветка возможных ходов
        for mx, my, mz in possible_moves:
            board.draw_highlight(
                board.screen,
                mx,
                my,
                mz,
                (80, 170, 255, 110)
            )

        # фигуры
        for piece in board.pieces:
            board.draw_piece(board.screen, piece)

        # статус игры
        if board.game_over:
            if board.winner:
                board.draw_text(
                    f"Мат! Победили {'Белые' if board.winner == 'white' else 'Чёрные'}"
                )
            else:
                board.draw_text("Пат! Ничья")
        else:
            turn_text = f"Ход: {'Белые' if turn == 'white' else 'Чёрные'}"
            if board.is_in_check(turn):
                turn_text += " (ШАХ!)"
                board.draw_text(turn_text, color=(255, 100, 100))
            else:
                board.draw_text(turn_text)

        pygame.display.set_caption("Hex Chess — 2 Players")
        pygame.display.flip()
        board.clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()