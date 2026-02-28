# pygame_hex_ui.py  (hex chess playable MVP)
import math
import pygame

from hex_board import HexBoard
from hex_rules import HexChessRulesMcCooey, HexMove

SQRT3 = math.sqrt(3)


def axial_to_pixel(q, r, size, origin):
    ox, oy = origin
    x = size * SQRT3 * (q + r / 2) + ox
    y = size * 1.5 * r + oy
    return (x, y)


def hex_corners(cx, cy, size):
    pts = []
    for i in range(6):
        angle = math.radians(60 * i - 30)  # pointy-top
        pts.append((cx + size * math.cos(angle), cy + size * math.sin(angle)))
    return pts


def point_in_poly(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1):
            inside = not inside
    return inside



def make_start_mccooey_official(board: HexBoard):
    # очистить поле
    for q, r in board.all_cells():
        board.set(q, r, ".")

    # --- WHITE (заглавные внизу) ---
    # 7 пешек
    for q in [-3, -2, -1, 0, 1, 2, 3]:
        board.set(q, 3, "P")

    # 3 слона (важно для McCooey/hex) + остальные фигуры
    # делаем компактно и симметрично, влезает в radius=5
    placements_white = {
        (-2, 4): "B",
        (0, 4): "B",
        (2, 4): "B",

        (-3, 4): "R",
        (3, 4): "R",

        (-1, 4): "N",
        (1, 4): "N",

        (0, 5): "K",
        (-1, 5): "Q",
    }
    for (q, r), s in placements_white.items():
        if board.in_bounds(q, r):
            board.set(q, r, s)

    # --- BLACK (строчные сверху) ---
    for q in [-3, -2, -1, 0, 1, 2, 3]:
        board.set(q, -3, "p")

    placements_black = {
        (-2, -4): "b",
        (0, -4): "b",
        (2, -4): "b",

        (-3, -4): "r",
        (3, -4): "r",

        (-1, -4): "n",
        (1, -4): "n",

        (0, -5): "k",
        (1, -5): "q",
    }
    for (q, r), s in placements_black.items():
        if board.in_bounds(q, r):
            board.set(q, r, s)




def main():
    pygame.init()

    radius = 5
    HEX_SIZE = 34
    W, H = 1000, 860

    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Hex Chess (McCooey) — MVP")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    big = pygame.font.SysFont(None, 30)

    board = HexBoard(radius=radius)
    make_start_mccooey_official(board)
    rules = HexChessRulesMcCooey()

    origin = (W // 2, H // 2 + 20)

    polys = {}
    for (q, r) in board.all_cells():
        cx, cy = axial_to_pixel(q, r, HEX_SIZE, origin)
        polys[(q, r)] = hex_corners(cx, cy, HEX_SIZE - 1)

    white_turn = True
    selected = None
    legal_moves = []
    info = "ЛКМ: выбрать/ход | ESC: выйти"

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
                for cell, poly in polys.items():
                    if point_in_poly((mx, my), poly):
                        hit = cell
                        break
                if not hit:
                    continue

                q, r = hit

                if selected is None:
                    sym = board.get(q, r)
                    if sym == ".":
                        continue
                    if not rules.is_own_piece(sym, white_turn):
                        continue
                    selected = (q, r)
                    legal_moves = rules.legal_moves_from(board, q, r, white_turn)
                else:
                    q1, r1 = selected
                    mv = HexMove(q1, r1, q, r)
                    ok, msg = rules.validate_move(board, mv, white_turn)
                    if ok:
                        rules.apply_move(board, mv, white_turn, msg)
                        white_turn = not white_turn
                        res = rules.game_result(board, white_turn)
                        if res == "white":
                            info = "Победа белых (мат)!"
                        elif res == "black":
                            info = "Победа чёрных (мат)!"
                        elif res == "draw":
                            info = "Ничья (пат)!"
                        else:
                            info = "Ход сделан."
                    else:
                        info = f"Ошибка: {msg}"

                    selected = None
                    legal_moves = []

        # draw
        screen.fill((18, 18, 18))

        for (q, r), poly in polys.items():
            color = (200, 200, 200) if ((q + r) & 1) == 0 else (120, 120, 120)
            pygame.draw.polygon(screen, color, poly)
            pygame.draw.polygon(screen, (40, 40, 40), poly, 2)

            if (q, r) in legal_moves:
                pygame.draw.polygon(screen, (80, 180, 80), poly, 3)

            sym = board.get(q, r)
            if sym != ".":
                cx, cy = axial_to_pixel(q, r, HEX_SIZE, origin)
                txt = big.render(sym, True, (0, 0, 0))
                rect = txt.get_rect(center=(cx, cy))
                screen.blit(txt, rect)

        if selected:
            pygame.draw.polygon(screen, (220, 180, 60), polys[selected], 4)

        side = "WHITE" if white_turn else "BLACK"
        screen.blit(font.render(f"Turn: {side}", True, (240, 240, 240)), (10, 10))
        screen.blit(font.render(info, True, (240, 240, 240)), (10, 34))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
