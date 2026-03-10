def main():
    while True:
        print("\nВыберите режим:")
        print("1 - Шахматы / Шашки (pygame)")
        print("2 - Cекс-шахматы на двоих (консоль)")
        print("3 - Cекс-шахматы на троих (консоль)")
        print("0 - Выход")

        mode = input("Ваш выбор: ").strip()

        if mode == "1":
            import pygame_main
            pygame_main.main()

        elif mode == "2":
            import hex_chess_2p
            game = hex_chess_2p.HexChessGame()
            game.play()

        elif mode == "3":
            import hex_chess_3p
            game = hex_chess_3p.HexChessGame()
            game.play()

        elif mode == "0":
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор.")


if __name__ == "__main__":
    main()