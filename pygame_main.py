import pygame

from board import SquareBoard
from game import Game
from move import Move


CELL = 72
MARGIN = 40
W = MARGIN * 2 + CELL * 8
H = MARGIN * 2 + CELL * 8
FILES = "ABCDEFGH"


def cell_to_pixel(r: int, c: int):
    x = MARGIN + c * CELL
    y = MARGIN + r * CELL
    return x, y


def pixel_to_cell(x: int, y: int):
    x -= MARGIN
    y -= MARGIN
    if x < 0 or y < 0:
        return None
    c = x // CELL
    r = y // CELL
    if 0 <= r < 8 and 0 <= c < 8:
        return int(r), int(c)
    return None


def draw(screen, font, small, board: SquareBoard, white_turn: bool, halfmove_count: int,
         selected=None, info_text: str = "", legal_moves=None):
    if legal_moves is None:
        legal_moves = []

    screen.fill((20, 20, 20))

    # клетки
    for r in range(8):
        for c in range(8):
            x, y = cell_to_pixel(r, c)
            light = (r + c) % 2 == 0
            color = (210, 210, 210) if light else (120, 120, 120)
            pygame.draw.rect(screen, color, (x, y, CELL, CELL))

    # подсветка легальных ходов (если есть)
    for (r, c) in legal_moves:
        x, y = cell_to_pixel(r, c)
        pygame.draw.rect(screen, (80, 180, 80), (x + 4, y + 4, CELL - 8, CELL - 8), 3)

    # выделение выбранной клетки
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

    # статус + ошибка
    side = "Белые" if white_turn else "Чёрные"
    status = f"{side} ходят | полуходов: {halfmove_count}"
    screen.blit(small.render(status, True, (240, 240, 240)), (10, 10))

    if info_text:
        screen.blit(small.render(info_text, True, (255, 80, 80)), (10, 30))


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Chess pygame UI (step 2)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    small = pygame.font.SysFont(None, 24)

    game = Game()
    board = game.board

    running = True
    selected = None
    info_text = ""
    legal_moves = []

    while running:
        clock.tick(60)

        # рисуем кадр
        draw(
            screen, font, small,
            board=board,
            white_turn=game.white_turn,
            halfmove_count=getattr(game, "halfmove_count", 0),
            selected=selected,
            info_text=info_text,
            legal_moves=legal_moves
        )
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pixel_to_cell(*event.pos)
                if pos is None:
                    continue

                r, c = pos

                # 1-й клик — выбрать фигуру
                if selected is None:
                    sym = board.get(r, c)
                    if sym == ".":
                        info_text = "Пустая клетка"
                        continue

                    # проверка цвета
                    if game.white_turn and not sym.isupper():
                        info_text = "Сейчас ход белых"
                        continue
                    if (not game.white_turn) and not sym.islower():
                        info_text = "Сейчас ход чёрных"
                        continue

                    selected = (r, c)
                    info_text = ""

                    # подсветка легальных ходов (если такой метод есть)
                    if hasattr(game.rules, "legal_moves_from"):
                        legal_moves = game.rules.legal_moves_from(board, r, c, game.white_turn)
                    else:
                        legal_moves = []
                    continue

                # 2-й клик — сделать ход
                else:
                    r1, c1 = selected
                    r2, c2 = r, c

                    # клик по той же клетке — снять выделение
                    if (r2, c2) == (r1, c1):
                        selected = None
                        legal_moves = []
                        info_text = ""
                        continue

                    move = Move(r1, c1, r2, c2)

                    ok, result = game.rules.validate_move(board, move, game.white_turn)
                    if not ok:
                        info_text = str(result)
                        selected = None
                        legal_moves = []
                        continue

                    # применяем ход
                    game.rules.apply_move(board, move, game.white_turn, result)

                    game.white_turn = not game.white_turn
                    if hasattr(game, "halfmove_count"):
                        game.halfmove_count += 1

                    selected = None
                    legal_moves = []
                    info_text = ""

    pygame.quit()


if __name__ == "__main__":
    main()