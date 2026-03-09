# pygame_hex_ui.py  (hex chess playable MVP)
import math
import pygame

from hex_board import HexBoard
from hex_chess_rules import HexChessRulesMcCooey, HexMove

SQRT3 = math.sqrt(3)


def rotate_point(x, y, ox, oy, angle_rad):
    dx, dy = x - ox, y - oy
    ca, sa = math.cos(angle_rad), math.sin(angle_rad)
    rx = dx * ca - dy * sa
    ry = dx * sa + dy * ca
    return ox + rx, oy + ry


def axial_to_pixel(q, r, size, origin):
    """pointy-top axial -> pixel (+ optional rotation)"""
    ox, oy = origin
    x = size * SQRT3 * (q + r / 2) + ox
    y = size * 1.5 * r + oy

    # ПОВОРОТ ДОСКИ (если хочешь)
    angle = math.radians(30)  # можно 0 / 30 / 60 / 90
    x, y = rotate_point(x, y, ox, oy, angle)

    return x, y


def hex_corners(cx, cy, size):
    """corners for pointy-top hex (match axial_to_pixel)"""
    pts = []
    for i in range(6):
        angle = math.radians(60 * i - 30)  # <-- ВАЖНО: -30 для pointy-top
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


def make_start_mccooey_wiki(board: HexBoard):
    for q, r in board.all_cells():
        board.set(q, r, ".")

    white_pieces = {
        (-3, 4): 'P', (-2, 3): 'P', (-1, 3): 'P', (0, 3): 'P',
        (1, 2):  'P', (2, 2):  'P', (3, 1):  'P',
        (-4, 5): 'R', (-3, 5): 'N', (-2, 5): 'B',
        (-1, 5): 'Q', (0, 5):  'B', (1, 4):  'K',
        (2, 3):  'N', (3, 2):  'R',
        (0, 4):  'B',
    }

    for (q, r), sym in white_pieces.items():
        if board.in_bounds(q, r):
            board.set(q, r, sym)

    # Чёрные — точное зеркало через центр доски
    for (q, r), sym in white_pieces.items():
        qb, rb = -q, -r
        if board.in_bounds(qb, rb):
            board.set(qb, rb, sym.lower())


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
    make_start_mccooey_wiki(board)

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
            # 3-цветная раскраска (как в hex chess)
            k = (q - r) % 3
            if k == 0:
                color = (210, 200, 170)
            elif k == 1:
                color = (170, 150, 110)
            else:
                color = (120, 120, 120)

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