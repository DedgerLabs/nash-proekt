import math
import pygame

# ---------------------------
# Hex math (axial coordinates)
# ---------------------------

SQRT3 = math.sqrt(3)

def axial_neighbors(q, r):
    return [
        (q + 1, r), (q - 1, r),
        (q, r + 1), (q, r - 1),
        (q + 1, r - 1), (q - 1, r + 1),
    ]

def axial_to_pixel(q, r, size, origin):
    ox, oy = origin
    x = size * SQRT3 * (q + r / 2) + ox
    y = size * 1.5 * r + oy
    return (x, y)

def hex_corners(cx, cy, size):
    # pointy-top
    pts = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        pts.append((cx + size * math.cos(angle), cy + size * math.sin(angle)))
    return pts

def point_in_poly(pt, poly):
    # ray casting
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1):
            inside = not inside
    return inside

# ---------------------------
# Hex board model (radius)
# ---------------------------

class HexBoard:
    """
    Гекс-доска радиуса R (Глинский: обычно R=5 -> 91 клетка).
    Храним клетки в axial (q,r). Допустимые клетки: |q|<=R, |r|<=R, |q+r|<=R.
    """
    def __init__(self, radius=5):
        self.radius = radius
        self.cells = {}  # (q,r) -> symbol
        for q in range(-radius, radius + 1):
            for r in range(-radius, radius + 1):
                s = -q - r
                if max(abs(q), abs(r), abs(s)) <= radius:
                    self.cells[(q, r)] = "."  # пусто

    def get(self, q, r):
        return self.cells.get((q, r))

    def set(self, q, r, v):
        if (q, r) in self.cells:
            self.cells[(q, r)] = v

    def in_bounds(self, q, r):
        return (q, r) in self.cells

    def all_cells(self):
        return list(self.cells.keys())

# ---------------------------
# Pygame UI
# ---------------------------

def main():
    pygame.init()

    # Настройки
    radius = 5          # Глинский = 5 (91 клетка)
    HEX_SIZE = 34       # размер клетки (подбери под своё окно)
    W, H = 900, 800

    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Hex Chess board (preview)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    board = HexBoard(radius=radius)

    # Центрируем поле
    origin = (W // 2, H // 2)

    selected = None
    info = "Кликни по клетке"

    # Предрасчёт полигонов для клика
    # (q,r) -> poly points
    polys = {}
    for (q, r) in board.all_cells():
        cx, cy = axial_to_pixel(q, r, HEX_SIZE, origin)
        polys[(q, r)] = hex_corners(cx, cy, HEX_SIZE - 1)

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                hit = None
                # простой перебор (91 клетка — нормально)
                for cell, poly in polys.items():
                    if point_in_poly((mx, my), poly):
                        hit = cell
                        break
                if hit:
                    selected = hit
                    info = f"Выбрана клетка axial q={hit[0]} r={hit[1]}"

        # рисуем
        screen.fill((18, 18, 18))

        for (q, r), poly in polys.items():
            # шахматный “узор” по parity
            color = (200, 200, 200) if ((q + r) & 1) == 0 else (120, 120, 120)
            pygame.draw.polygon(screen, color, poly)
            pygame.draw.polygon(screen, (40, 40, 40), poly, 2)

            # символ (пока пусто)
            sym = board.get(q, r)
            if sym != ".":
                cx, cy = axial_to_pixel(q, r, HEX_SIZE, origin)
                txt = font.render(sym, True, (0, 0, 0))
                rect = txt.get_rect(center=(cx, cy))
                screen.blit(txt, rect)

        if selected:
            pygame.draw.polygon(screen, (220, 180, 60), polys[selected], 4)

        # инфо
        txt = font.render(info + " | ESC выйти", True, (240, 240, 240))
        screen.blit(txt, (10, 10))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()