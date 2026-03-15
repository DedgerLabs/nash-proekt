def main():
    while True:
        print("\nВыберите режим:")
        print("1 - Все игры (pygame)")
        print("0 - Выход")

        mode = input("Ваш выбор: ").strip()

        if mode == "1":
            import pygame_main
            pygame_main.main()
        elif mode == "0":
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор.")


if __name__ == "__main__":
    main()