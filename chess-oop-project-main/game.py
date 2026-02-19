from board import SquareBoard
from rules import ClassicChessRules
from move import Move






class Game:
    def __init__(self):
        self.board = SquareBoard()
        self.rules = ClassicChessRules()
        self.white_turn = True
        self.move_count = 0
        self.history = []  # для undo

    @staticmethod
    def print_legend():
        print("Обозначения фигур:")
        print("  Белые:  П — пешка, Л — ладья, К — конь, С — слон, Ф — ферзь, K — король")
        print("  Чёрные: п — пешка, л — ладья, н — конь, с — слон, ф — ферзь, к — король")
        print()

    @staticmethod
    def print_menu():
        print("Команды:")
        print("  help                 - показать меню")
        print("  exit                 - выйти")
        print("  undo [n]             - откатить n полуходов (по умолчанию 1)")
        print("  hint e2              - подсказка ходов выбранной фигуры")
        print("  threatened           - показать ваши фигуры под боем + шах")
        print()
        print("Ход вводится так:")
        print("  e2 e4   или   e2e4")
        print("Рокировка (как ход королём на 2 клетки):")
        print("  e1 g1  (белые короткая)   |  e1 c1 (белые длинная)")
        print("  e8 g8  (чёрные короткая)  |  e8 c8 (чёрные длинная)")
        print()

    def snapshot(self):
        return {
            "grid": self.board.clone_grid(),
            "white_turn": self.white_turn,
            "move_count": self.move_count,
            "moved": dict(self.rules.moved),
            "ep": None if self.rules.ep is None else dict(self.rules.ep),
        }

    def restore(self, snap):
        self.board.grid = [row[:] for row in snap["grid"]]
        self.white_turn = snap["white_turn"]
        self.move_count = snap["move_count"]
        self.rules.moved = dict(snap["moved"])
        self.rules.ep = snap["ep"]

    def run(self):
        self.print_legend()
        self.print_menu()

        while True:
            self.board.print_board()
            side = "Белые" if self.white_turn else "Чёрные"
            print(f"{side} ходят. Сделано полуходов: {self.move_count}")
            print("Подсказка: help | undo [n] | hint e2 | threatened | exit")

            in_chk = self.rules.is_in_check(self.board, self.white_turn)
            if in_chk:
                print("Внимание: ШАХ!")

            if not self.rules.has_any_legal_move(self.board, self.white_turn):
                if in_chk:
                    print("МАТ! Игра окончена.")
                else:
                    print("ПАТ! Игра окончена.")
                break

            line = input("> ").strip()
            if not line:
                continue
            low = line.lower()

            if low == "help":
                self.print_menu()
                continue
            if low == "exit":
                print("Выход.")
                break

            if low.startswith("undo"):
                parts = low.split()
                n = 1
                if len(parts) >= 2 and parts[1].isdigit():
                    n = int(parts[1])
                if n <= 0:
                    continue
                if len(self.history) < n:
                    print("Нечего так много отменять.")
                    continue
                for _ in range(n):
                    snap = self.history.pop()
                    self.restore(snap)
                continue

            if low.startswith("hint"):
                parts = low.split()
                if len(parts) < 2:
                    print("Пример: hint e2")
                    continue
                self.rules.cmd_hint(self.board, self.white_turn, parts[1])
                continue

            if low == "threatened":
                self.rules.cmd_threatened(self.board, self.white_turn)
                continue

            parsed = Move.parse_move_input(line)
            if parsed is None:
                print("Не понял ввод. Пример: e2 e4 или e2e4.")
                continue

            frm_s, to_s = parsed
            frm = Move.parse_square(frm_s)
            to = Move.parse_square(to_s)
            if frm is None or to is None:
                print("Ошибка ввода. Пример: e2 e4")
                continue

            r1, c1 = frm
            r2, c2 = to
            mv = Move(r1, c1, r2, c2)

            ok, info = self.rules.validate_move(self.board, mv, self.white_turn)
            if not ok:
                print("Ошибка:", info)
                continue

            # undo snapshot ДО хода
            self.history.append(self.snapshot())

            self.rules.apply_move(self.board, mv, self.white_turn, info)
            self.move_count += 1
            self.white_turn = not self.white_turn
