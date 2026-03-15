import math
import sys
import pygame


BG_COLOR = (24, 28, 36)
HEX_COLORS = [
    (238, 220, 190),
    (188, 154, 122),
    (132, 104, 77),
]
GRID_COLOR = (45, 45, 50)

MOVE_HIGHLIGHT = (80, 170, 255, 110)
SELECT_HIGHLIGHT = (255, 196, 0, 120)

TEXT_COLOR = (245, 245, 245)
SUBTEXT_COLOR = (210, 210, 210)
PANEL_COLOR = (18, 21, 28)


# ----------------------------------------------------------------------
# Классы фигур
# ----------------------------------------------------------------------
class Piece:
    def __init__(self, color, x, y, z, symbol):
        self.color = color      # 'green', 'gray', 'white'
        self.x = x
        self.y = y
        self.z = z
        self.symbol = symbol    # 'P', 'N', 'B', 'R', 'Q', 'K'

    def get_moves(self, board, occupied):
        return []

    def __repr__(self):
        return f"{self.color[0]}{self.symbol}"


class Pawn(Piece):
    def __init__(self, color, x, y, z):
        super().__init__(color, x, y, z, "P")

    def get_moves(self, board, occupied):
        moves = []

        forward_map = {
            "green": (1, 0, -1),
            "gray": (0, -1, 1),
            "white": (-1, 1, 0),
        }

        capture_map = {
            "green": [(1, -1, 0), (0, 1, -1)],
            "gray": [(-1, 0, 1), (1, -1, 0)],
            "white": [(0, 1, -1), (-1, 0, 1)],
        }

        fdx, fdy, fdz = forward_map[self.color]

        nx, ny, nz = self.x + fdx, self.y + fdy, self.z + fdz
        if board.is_on_board(nx, ny, nz) and (nx, ny, nz) not in occupied:
            moves.append((nx, ny, nz))

        for cdx, cdy, cdz in capture_map[self.color]:
            nx, ny, nz = self.x + cdx, self.y + cdy, self.z + cdz
            if board.is_on_board(nx, ny, nz):
                if (nx, ny, nz) in occupied and occupied[(nx, ny, nz)].color != self.color:
                    moves.append((nx, ny, nz))

        return moves


class Knight(Piece):
    def __init__(self, color, x, y, z):
        super().__init__(color, x, y, z, "N")

    def get_moves(self, board, occupied):
        moves = []
        knight_dirs = [
            (3, -2, -1), (2, -3, 1), (3, -1, -2), (2, 1, -3),
            (1, 2, -3), (-1, 3, -2), (-2, 3, -1), (-3, 2, 1),
            (-3, 1, 2), (-2, -1, 3), (-1, -2, 3), (1, -3, 2),
        ]

        for dx, dy, dz in knight_dirs:
            nx, ny, nz = self.x + dx, self.y + dy, self.z + dz
            if board.is_on_board(nx, ny, nz):
                if (nx, ny, nz) not in occupied or occupied[(nx, ny, nz)].color != self.color:
                    moves.append((nx, ny, nz))

        return moves


class Bishop(Piece):
    def __init__(self, color, x, y, z):
        super().__init__(color, x, y, z, "B")

    def get_moves(self, board, occupied):
        moves = []
        directions = [
            (2, -1, -1), (1, 1, -2), (-1, 2, -1),
            (-2, 1, 1), (-1, -1, 2), (1, -2, 1),
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
        super().__init__(color, x, y, z, "R")

    def get_moves(self, board, occupied):
        moves = []
        directions = [
            (1, -1, 0), (1, 0, -1), (0, 1, -1),
            (-1, 1, 0), (-1, 0, 1), (0, -1, 1),
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
        super().__init__(color, x, y, z, "Q")

    def get_moves(self, board, occupied):
        moves = []

        rook_dirs = [
            (1, -1, 0), (1, 0, -1), (0, 1, -1),
            (-1, 1, 0), (-1, 0, 1), (0, -1, 1),
        ]
        bishop_dirs = [
            (2, -1, -1), (1, 1, -2), (-1, 2, -1),
            (-2, 1, 1), (-1, -1, 2), (1, -2, 1),
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
        super().__init__(color, x, y, z, "K")

    def get_moves(self, board, occupied):
        moves = []
        directions = [
            (1, -1, 0), (1, 0, -1), (0, 1, -1),
            (-1, 1, 0), (-1, 0, 1), (0, -1, 1),
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

        self.WIDTH, self.HEIGHT = 1400, 980
        self.BACKGROUND = BG_COLOR
        self.COLORS = HEX_COLORS
        self.LINE_COLOR = GRID_COLOR

        self.PLAYER_COLORS = {
            "green": (88, 166, 117),
            "gray": (155, 160, 168),
            "white": (245, 245, 245),
        }

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Hex Chess — 3 Players")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(None, 40)
        self.small_font = pygame.font.Font(None, 26)

        self.SQRT3 = math.sqrt(3)
        self.ANGLES = [math.pi / 2 + i * math.pi / 3 for i in range(6)]

        self.x_min, self.x_max = -7, 8
        self.y_min, self.y_max = -8, 7
        self.z_min, self.z_max = -7, 8

        self.hexes = []
        for x in range(self.x_min, self.x_max + 1):
            for y in range(self.y_min, self.y_max + 1):
                z = -x - y
                if self.z_min <= z <= self.z_max:
                    self.hexes.append((x, y, z))

        self._compute_scale_and_offset()

    def _compute_scale_and_offset(self):
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

        margin = 30
        available_width = self.WIDTH - 2 * margin
        available_height = self.HEIGHT - 2 * margin - 60  # место под верхнюю панель

        scale_x = available_width / board_width
        scale_y = available_height / board_height
        self.SIDE = min(scale_x, scale_y)

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

        self.offset_x = self.WIDTH // 2 - int((min_x2 + max_x2) / 2)
        self.offset_y = self.HEIGHT // 2 - int((min_y2 + max_y2) / 2) + 25

    def is_on_board(self, x, y, z):
        return (x, y, z) in self.hexes

    def cube_to_pixel(self, x, y, z):
        q, r = x, z
        px = self.SIDE * self.SQRT3 * (q + r / 2.0) + self.offset_x
        py = self.SIDE * 1.5 * r + self.offset_y
        return int(px), int(py)

    def get_hex_at(self, screen_x, screen_y):
        min_dist = float("inf")
        best_hex = None

        for (x, y, z) in self.hexes:
            cx, cy = self.cube_to_pixel(x, y, z)
            dist = math.hypot(screen_x - cx, screen_y - cy)
            if dist < self.SIDE and dist < min_dist:
                min_dist = dist
                best_hex = (x, y, z)

        return best_hex

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

        font = pygame.font.Font(None, int(radius * 1.55))
        text_color = (20, 20, 20) if piece.color == "white" else (245, 245, 245)

        text = font.render(piece.symbol, True, text_color)
        text_rect = text.get_rect(center=(cx, cy))
        surface.blit(text, text_rect)

    def draw_status_panel(self, current_player):
        labels = {
            "green": "зелёных",
            "gray": "серых",
            "white": "белых",
        }

        panel_rect = pygame.Rect(0, 0, self.WIDTH, 76)
        pygame.draw.rect(self.screen, PANEL_COLOR, panel_rect)

        title = self.font.render(f"Ход: {labels[current_player]}", True, TEXT_COLOR)
        subtitle = self.small_font.render("Hex Chess — 3 Players", True, SUBTEXT_COLOR)

        self.screen.blit(title, (20, 14))
        self.screen.blit(subtitle, (20, 44))

    def draw_highlight_circle(self, x, y, z, color, scale=0.5):
        cx, cy = self.cube_to_pixel(x, y, z)
        s = pygame.Surface((int(self.SIDE * 2), int(self.SIDE * 2)), pygame.SRCALPHA)
        pygame.draw.circle(
            s,
            color,
            (int(self.SIDE), int(self.SIDE)),
            int(self.SIDE * scale),
        )
        self.screen.blit(s, (cx - self.SIDE, cy - self.SIDE))


# ----------------------------------------------------------------------
# Начальная расстановка
# ----------------------------------------------------------------------
def create_initial_pieces(board):
    pieces = []

    # ----- Зелёные -----
    z1 = board.z_max
    z2 = board.z_max - 1
    z3 = board.z_max - 2

    green_row1 = [h for h in board.hexes if h[2] == z1]
    green_row1.sort(key=lambda h: h[0])
    green_figures = ["R", "B", "N", "Q", "K", "N", "B", "R"]

    for i, (x, y, z) in enumerate(green_row1):
        ptype = green_figures[i]
        if ptype == "R":
            pieces.append(Rook("green", x, y, z))
        elif ptype == "B":
            pieces.append(Bishop("green", x, y, z))
        elif ptype == "N":
            pieces.append(Knight("green", x, y, z))
        elif ptype == "Q":
            pieces.append(Queen("green", x, y, z))
        elif ptype == "K":
            pieces.append(King("green", x, y, z))

    green_row2 = [h for h in board.hexes if h[2] == z2]
    green_row2.sort(key=lambda h: h[0])
    center = len(green_row2) // 2
    for i, (x, y, z) in enumerate(green_row2):
        if i == center:
            pieces.append(Bishop("green", x, y, z))
        else:
            pieces.append(Pawn("green", x, y, z))

    green_row3 = [h for h in board.hexes if h[2] == z3]
    green_row3.sort(key=lambda h: h[0])
    for i, (x, y, z) in enumerate(green_row3):
        if i == 0 or i == len(green_row3) - 1:
            continue
        pieces.append(Pawn("green", x, y, z))

    # ----- Серые -----
    y1 = board.y_max
    y2 = board.y_max - 1
    y3 = board.y_max - 2

    gray_row1 = [h for h in board.hexes if h[1] == y1]
    gray_row1.sort(key=lambda h: h[0])
    gray_figures = ["R", "B", "N", "Q", "K", "N", "B", "R"]

    for i, (x, y, z) in enumerate(gray_row1):
        ptype = gray_figures[i]
        if ptype == "R":
            pieces.append(Rook("gray", x, y, z))
        elif ptype == "B":
            pieces.append(Bishop("gray", x, y, z))
        elif ptype == "N":
            pieces.append(Knight("gray", x, y, z))
        elif ptype == "Q":
            pieces.append(Queen("gray", x, y, z))
        elif ptype == "K":
            pieces.append(King("gray", x, y, z))

    gray_row2 = [h for h in board.hexes if h[1] == y2]
    gray_row2.sort(key=lambda h: h[0])
    center = len(gray_row2) // 2
    for i, (x, y, z) in enumerate(gray_row2):
        if i == center:
            pieces.append(Bishop("gray", x, y, z))
        else:
            pieces.append(Pawn("gray", x, y, z))

    gray_row3 = [h for h in board.hexes if h[1] == y3]
    gray_row3.sort(key=lambda h: h[0])
    for i, (x, y, z) in enumerate(gray_row3):
        if i == 0 or i == len(gray_row3) - 1:
            continue
        pieces.append(Pawn("gray", x, y, z))

    # ----- Белые -----
    x1 = board.x_max
    x2 = board.x_max - 1
    x3 = board.x_max - 2

    white_row1 = [h for h in board.hexes if h[0] == x1]
    white_row1.sort(key=lambda h: -h[1])
    white_figures = ["R", "B", "N", "Q", "K", "N", "B", "R"]

    for i, (x, y, z) in enumerate(white_row1):
        ptype = white_figures[i]
        if ptype == "R":
            pieces.append(Rook("white", x, y, z))
        elif ptype == "B":
            pieces.append(Bishop("white", x, y, z))
        elif ptype == "N":
            pieces.append(Knight("white", x, y, z))
        elif ptype == "Q":
            pieces.append(Queen("white", x, y, z))
        elif ptype == "K":
            pieces.append(King("white", x, y, z))

    white_row2 = [h for h in board.hexes if h[0] == x2]
    white_row2.sort(key=lambda h: -h[1])
    center = len(white_row2) // 2
    for i, (x, y, z) in enumerate(white_row2):
        if i == center:
            pieces.append(Bishop("white", x, y, z))
        else:
            pieces.append(Pawn("white", x, y, z))

    white_row3 = [h for h in board.hexes if h[0] == x3]
    white_row3.sort(key=lambda h: -h[1])
    for i, (x, y, z) in enumerate(white_row3):
        if i == 0 or i == len(white_row3) - 1:
            continue
        pieces.append(Pawn("white", x, y, z))

    return pieces


# ----------------------------------------------------------------------
# Главная функция
# ----------------------------------------------------------------------
def main():
    board = Board()
    pieces = create_initial_pieces(board)
    occupied = {(p.x, p.y, p.z): p for p in pieces}

    current_player = "green"
    selected_piece = None
    possible_moves = []

    def next_player():
        nonlocal current_player
        if current_player == "green":
            current_player = "gray"
        elif current_player == "gray":
            current_player = "white"
        else:
            current_player = "green"

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                coord = board.get_hex_at(mouse_x, mouse_y)

                if coord is None:
                    selected_piece = None
                    possible_moves = []
                    continue

                x, y, z = coord

                if selected_piece is None:
                    if (x, y, z) in occupied and occupied[(x, y, z)].color == current_player:
                        selected_piece = occupied[(x, y, z)]
                        possible_moves = selected_piece.get_moves(board, occupied)
                else:
                    if (x, y, z) in possible_moves:
                        target = (x, y, z)

                        if target in occupied:
                            captured = occupied[target]
                            if captured in pieces:
                                pieces.remove(captured)
                            del occupied[target]

                        old_coord = (selected_piece.x, selected_piece.y, selected_piece.z)
                        if old_coord in occupied:
                            del occupied[old_coord]

                        selected_piece.x, selected_piece.y, selected_piece.z = target
                        occupied[target] = selected_piece

                        selected_piece = None
                        possible_moves = []
                        next_player()

                    elif (x, y, z) in occupied and occupied[(x, y, z)].color == current_player:
                        selected_piece = occupied[(x, y, z)]
                        possible_moves = selected_piece.get_moves(board, occupied)

                    else:
                        selected_piece = None
                        possible_moves = []

        board.screen.fill(board.BACKGROUND)
        board.draw_status_panel(current_player)

        for x, y, z in board.hexes:
            color_index = (x + 2 * y) % 3
            board.draw_hex(board.screen, x, y, z, board.COLORS[color_index])

        for mx, my, mz in possible_moves:
            board.draw_highlight_circle(mx, my, mz, MOVE_HIGHLIGHT, 0.46)

        if selected_piece is not None:
            board.draw_highlight_circle(
                selected_piece.x,
                selected_piece.y,
                selected_piece.z,
                SELECT_HIGHLIGHT,
                0.56,
            )

        for piece in pieces:
            board.draw_piece(board.screen, piece)

        pygame.display.set_caption("Hex Chess — 3 Players")
        pygame.display.flip()
        board.clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()