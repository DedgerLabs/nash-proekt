import pygame

from board import SquareBoard, make_start_checkers_board
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


def draw(
    screen,
    font,
    small,
    board,
    white_turn,
    halfmove_count,
    selected=None,
    info_text="",
    legal_moves=None,
    threatened=None,
):
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

    # подсветка возможных ходов
    for (r, c) in legal_moves:
        x, y = cell_to_pixel(r, c)
        pygame.draw.rect(screen, (80, 180, 80), (x + 4, y + 4, CELL - 8, CELL - 8), 3)

    # выделение выбранной клетки
    if selected is not None:
        r, c = selected
        x, y = cell_to_pixel(r, c)
        pygame.draw.rect(screen, (220, 180, 60), (x + 2, y + 2, CELL - 4, CELL - 4), 4)

    # клетки под боем
    for (r, c) in threatened:
        x, y = cell_to_pixel(r, c)
        pygame.draw.rect(screen, (180, 80, 80), (x + 6, y + 6, CELL - 12, CELL - 12), 2)

    # фигуры
    for r in range(8):
        for c in range(8):
            sym = board.get(r, c)
            if sym == ".":
                continue

            x, y = cell_to_pixel(r, c)
            txt = font.render(sym, True, (0, 0, 0))
            rect = txt.get_rect(center=(x + CELL // 2, y + CELL // 2))
            screen.blit(txt, rect)

    # подписи A-H
    for i, ch in enumerate(FILES):
        tx = MARGIN + i * CELL + CELL // 2 - 8
        screen.blit(small.render(ch, True, (240, 240, 240)), (tx, MARGIN - 28))
        screen.blit(small.render(ch, True, (240, 240, 240)), (tx, MARGIN + 8 * CELL + 8))

    # подписи 1-8
    for i in range(8):
        rank = str(8 - i)
        ty = MARGIN + i * CELL + CELL // 2 - 10
        screen.blit(small.render(rank, True, (240, 240, 240)), (MARGIN - 26, ty))
        screen.blit(small.render(rank, True, (240, 240, 240)), (MARGIN + 8 * CELL + 10, ty))

    side = "Белые" if white_turn else "Чёрные"
    status = f"{side} ходят | полуходов: {halfmove_count}"
    screen.blit(small.render(status, True, (240, 240, 240)), (10, 10))

    if info_text:
        screen.blit(small.render(info_text, True, (255, 80, 80)), (10, 30))


def is_current_players_piece(sym: str, game) -> bool:
    if sym == ".":
        return False

    if hasattr(game.rules, "is_own_piece"):
        return game.rules.is_own_piece(sym, game.white_turn)

    # fallback
    if game.white_turn:
        return sym.isupper()
    return sym.islower()


def run_checkers():
    from checkers_rules import CheckersRules

    game = Game(
        board=SquareBoard(grid=make_start_checkers_board()),
        rules=CheckersRules(),
    )
    board = game.board

    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Шашки")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    small = pygame.font.SysFont(None, 24)

    running = True
    game_over = False
    selected = None
    info_text = ""
    legal_moves = []
    show_hint = True
    show_threatened = False
    threatened = set()

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    continue

                if event.key == pygame.K_u:
                    ok = game.undo()
                    info_text = "Undo: ход отменён" if ok else "Undo: нечего отменять"
                    selected = None
                    legal_moves = []
                    threatened = set()
                    game_over = False
                    continue

                if event.key == pygame.K_h:
                    show_hint = not show_hint
                    info_text = "Hint: ON" if show_hint else "Hint: OFF"
                    if not show_hint:
                        legal_moves = []
                    elif selected is not None and hasattr(game.rules, "legal_moves_from"):
                        r_sel, c_sel = selected
                        legal_moves = game.rules.legal_moves_from(board, r_sel, c_sel, game.white_turn)
                    continue

                if event.key == pygame.K_t:
                    show_threatened = not show_threatened

                    if show_threatened:
                        if hasattr(game.rules, "threatened_squares"):
                            threatened = game.rules.threatened_squares(board, game.white_turn)
                            info_text = "Threatened: ON"
                        else:
                            threatened = set()
                            info_text = "Threatened: нет метода"
                            show_threatened = False
                    else:
                        threatened = set()
                        info_text = "Threatened: OFF"
                    continue

            if game_over:
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pixel_to_cell(*event.pos)
                if pos is None:
                    continue

                r, c = pos
                sym = board.get(r, c)

                # первый клик: выбор фигуры
                if selected is None:
                    if sym == ".":
                        info_text = "Пустая клетка"
                        continue

                    if not is_current_players_piece(sym, game):
                        info_text = "Выбрана чужая фигура"
                        continue

                    selected = (r, c)
                    info_text = ""

                    if show_hint and hasattr(game.rules, "legal_moves_from"):
                        legal_moves = game.rules.legal_moves_from(board, r, c, game.white_turn)
                    else:
                        legal_moves = []

                    continue

                # повторный клик по своей фигуре = перевыбор
                if is_current_players_piece(sym, game):
                    selected = (r, c)
                    info_text = ""

                    if show_hint and hasattr(game.rules, "legal_moves_from"):
                        legal_moves = game.rules.legal_moves_from(board, r, c, game.white_turn)
                    else:
                        legal_moves = []

                    continue

                # второй клик: попытка хода
                r1, c1 = selected
                r2, c2 = r, c

                move = Move(r1, c1, r2, c2)
                ok, move_type = game.rules.validate_move(board, move, game.white_turn)

                if not ok:
                    info_text = f"Ошибка: {move_type}"
                    selected = None
                    legal_moves = []
                    continue

                game.push_state()
                game.rules.apply_move(board, move, game.white_turn, move_type)
                game.move_count += 1

                # продолжается серия рубки
                if hasattr(game.rules, "forced_piece") and game.rules.forced_piece is not None:
                    selected = game.rules.forced_piece
                    r_sel, c_sel = selected

                    if show_hint and hasattr(game.rules, "legal_moves_from"):
                        legal_moves = game.rules.legal_moves_from(board, r_sel, c_sel, game.white_turn)
                    else:
                        legal_moves = []

                    info_text = "Продолжай рубку этой же шашкой!"
                else:
                    game.white_turn = not game.white_turn
                    selected = None
                    legal_moves = []
                    info_text = ""

                if show_threatened and hasattr(game.rules, "threatened_squares"):
                    threatened = game.rules.threatened_squares(board, game.white_turn)
                else:
                    threatened = set()

                game_result = game.rules.game_result(board, game.white_turn)
                if game_result == "white":
                    info_text = "Победа белых!"
                    game_over = True
                elif game_result == "black":
                    info_text = "Победа чёрных!"
                    game_over = True

        draw(
            screen,
            font,
            small,
            board=board,
            white_turn=game.white_turn,
            halfmove_count=game.move_count,
            selected=selected,
            info_text=info_text,
            legal_moves=legal_moves,
            threatened=threatened,
        )
        pygame.display.flip()

    pygame.quit()


def main():
    mode = input("1 - chess, 2 - checkers, 3 - hex 2p, 4 - hex 3p: ").strip()

    if mode == "1":
        import friend_chess

        pygame.init()
        screen = pygame.display.set_mode((friend_chess.WIDTH + 300, friend_chess.HEIGHT))
        pygame.display.set_caption("Классические шахматы")

        game = friend_chess.ChessGame(screen)
        game.run()
        return

    if mode == "2":
        run_checkers()
        return

    if mode == "3":
        import hex_chess_2p_pygame
        hex_chess_2p_pygame.main()
        return

    if mode == "4":
        import hex_chess_3p_pygame
        hex_chess_3p_pygame.main()
        return

    print("Неверный ввод")


if __name__ == "__main__":
    main()