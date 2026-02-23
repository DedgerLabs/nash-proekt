import pygame
from board import SquareBoard, make_start_checkers_board
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


def draw(screen, font, small, board, white_turn, halfmove_count,
         selected=None, info_text="", legal_moves=None, threatened=None):
    if legal_moves is None:
        legal_moves = []
    if threatened is None:
        threatened = set()

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

    # клетки под боем
    for (r, c) in threatened:
        x, y = cell_to_pixel(r, c)
        pygame.draw.rect(screen, (180, 80, 80), (x + 6, y + 6, CELL - 12, CELL - 12), 2)

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
    mode = input("1 - chess, 2 - checkers, 3 - hex: ").strip()
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Chess pygame UI (step 2)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    small = pygame.font.SysFont(None, 24)



    if mode == "2":
        from checkers_rules import CheckersRules
        from board import SquareBoard, make_start_checkers_board
        game = Game(board=SquareBoard(grid=make_start_checkers_board()), rules=CheckersRules())
    else:
        game = Game()
    board = game.board


    running = True
    selected = None
    info_text = ""
    legal_moves = []
    show_hint = True
    show_threatened = False
    threatened = set()

    while running:
        clock.tick(60)

        # 🔹 1. ОБРАБОТКА СОБЫТИЙ
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_u:
                    ok = game.undo()
                    info_text = "Undo: ход отменён" if ok else "Undo: нечего отменять"
                    selected = None
                    legal_moves = []
                    threatened = set()

                elif event.key == pygame.K_h:
                    show_hint = not show_hint
                    info_text = "Hint: ON" if show_hint else "Hint: OFF"
                    legal_moves = []

                elif event.key == pygame.K_t:
                    show_threatened = not show_threatened
                    if show_threatened:
                        attacker_white = not game.white_turn
                        threatened = game.rules.threatened_squares(board, attacker_white)
                        info_text = "Threatened: ON"
                    else:
                        threatened = set()
                        info_text = "Threatened: OFF"

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # твоя логика клика мыши
                pos = pixel_to_cell(*event.pos)
                if pos is None:
                    continue

                r, c = pos
                # ... дальше твой код выбора/хода ...

                # 1-й клик — выбрать фигуру
                if selected is None:
                    sym = board.get(r, c)
                    if sym == ".":
                        info_text = "Пустая клетка"
                        continue

                    # проверка цвета
                    if selected is None:
                        sym = board.get(r, c)
                        if sym == ".":
                            info_text = "Пустая клетка"
                            continue

                        # универсальная проверка "своя фигура?"
                        if hasattr(game.rules, "is_own_piece"):
                            if not game.rules.is_own_piece(sym, game.white_turn):
                                info_text = "Выбрана чужая фигура"
                                continue
                        else:
                            # fallback для шахмат (если не добавлял is_own_piece в chess rules)
                            if game.white_turn and not sym.isupper():
                                info_text = "Сейчас ход белых"
                                continue
                            if (not game.white_turn) and not sym.islower():
                                info_text = "Сейчас ход чёрных"
                                continue

                        selected = (r, c)
                        info_text = ""

                        legal_moves = []
                        if show_hint and hasattr(game.rules, "legal_moves_from"):
                            legal_moves = game.rules.legal_moves_from(board, r, c, game.white_turn)

                        continue

                # 2-й клик — сделать ход
                else:
                    r1, c1 = selected
                    r2, c2 = r, c

                    move = Move(r1, c1, r2, c2)
                    ok, result = game.rules.validate_move(board, move, game.white_turn)

                    if not ok:
                        info_text = f"Ошибка: {result}"
                        selected = None
                        legal_moves = []
                        continue

                    # сохраняем состояние для undo
                    game.push_state()

                    # применяем ход
                    game.rules.apply_move(board, move, game.white_turn, result)

                    # переключаем ход и счётчик
                    game.white_turn = not game.white_turn
                    game.move_count += 1

                    # обновить threatened если включён
                    if show_threatened:
                        attacker_white = not game.white_turn
                        threatened = game.rules.threatened_squares(board, attacker_white)

                    selected = None
                    legal_moves = []
                    info_text = ""

        # 🔹 2. РИСУЕМ КАДР
        draw(
            screen, font, small,
            board=board,
            white_turn=game.white_turn,
            halfmove_count=game.move_count,
            selected=selected,
            info_text=info_text,
            legal_moves=legal_moves,
            threatened=threatened
        )

        pygame.display.flip()


if __name__ == "__main__":
    main()