import pygame

from board import SquareBoard
from game import Game  # если у тебя Game уже собирает board+rules


CELL = 72
MARGIN = 40
W = MARGIN * 2 + CELL * 8
H = MARGIN * 2 + CELL * 8
FILES = "ABCDEFGH"


def cell_to_pixel(r, c):
    x = MARGIN + c * CELL
    y = MARGIN + r * CELL
    return x, y


def pixel_to_cell(x, y):
    x -= MARGIN
    y -= MARGIN
    if x < 0 or y < 0:
        return None
    c = x // CELL
    r = y // CELL
    if 0 <= r < 8 and 0 <= c < 8:
        return int(r), int(c)
    return None


def draw(screen, font, small, board: SquareBoard, selected=None):
    screen.fill((20, 20, 20))

    # клетки
    for r in range(8):
        for c in range(8):
            x, y = cell_to_pixel(r, c)
            light = (r + c) % 2 == 0
            color = (210, 210, 210) if light else (120, 120, 120)
            pygame.draw.rect(screen, color, (x, y, CELL, CELL))

    # выделение
    if selected:
        r, c = selected
        x, y = cell_to_pixel(r, c)
        pygame.draw.rect(screen, (220, 180, 60), (x + 2, y + 2, CELL - 4, CELL - 4), 4)

    # фигуры (буквы)
    for r in range(8):
        for c in range(8):
            sym = board.get(r, c)
            if sym == ".":
                continue
            x, y = cell_to_pixel(r, c)
            txt = font.render(sym, True, (0, 0, 0))
            rect = txt.get_rect(center=(x + CELL // 2, y + CELL // 2))
            screen.blit(txt, rect)

    # подписи A-H / 1-8
    for i, ch in enumerate(FILES):
        tx = MARGIN + i * CELL + CELL // 2 - 8
        screen.blit(small.render(ch, True, (240, 240, 240)), (tx, MARGIN - 28))
        screen.blit(small.render(ch, True, (240, 240, 240)), (tx, MARGIN + 8 * CELL + 8))

    for i in range(8):
        rank = str(8 - i)
        ty = MARGIN + i * CELL + CELL // 2 - 10
        screen.blit(small.render(rank, True, (240, 240, 240)), (MARGIN - 26, ty))
        screen.blit(small.render(rank, True, (240, 240, 240)), (MARGIN + 8 * CELL + 10, ty))


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Chess pygame UI (step 1)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    small = pygame.font.SysFont(None, 24)

    game = Game()              # у тебя уже создаёт board внутри
    board = game.board         # берём доску

    selected = None

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pixel_to_cell(*event.pos)
                if pos is not None:
                    selected = pos
                    r, c = selected
                    print("Выбрана клетка:", (r, c), "символ:", board.get(r, c))

        draw(screen, font, small, board, selected)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()