from pieces import piece_from_symbol
from board import SquareBoard
from move import Move






class ClassicChessRules:
    def __init__(self):
        # moved — нужно для рокировки
        self.moved = {
            "K": False, "к": False,
            (7, 0): False, (7, 7): False,  # белые ладьи
            (0, 0): False, (0, 7): False,  # чёрные ладьи
        }
        # en passant состояние
        self.ep = None  # None или dict {"target":(r,c),"captured":(r,c),"for_white":bool}

    # --- цвет/тип фигур ---
    @staticmethod
    def is_white(piece):
        return piece != "." and piece.isupper()

    @staticmethod
    def is_black(piece):
        return piece != "." and piece.islower()

    @staticmethod
    def same_color(a, b):
        if a == "." or b == ".":
            return False
        return (ClassicChessRules.is_white(a) and ClassicChessRules.is_white(b)) or \
               (ClassicChessRules.is_black(a) and ClassicChessRules.is_black(b))

    @staticmethod
    def piece_type(piece):
        if piece == ".":
            return None
        # чёрные отдельными символами
        if piece == "к":
            return "K"
        if piece == "н":
            return "N"

        p = piece.upper()
        if p == "П": return "P"
        if p == "Л": return "R"
        if p == "К": return "N"  # белый конь
        if p == "С": return "B"
        if p == "Ф": return "Q"
        if p == "K": return "K"  # белый король
        return None

    # --- геометрия ходов ---
    @staticmethod
    def path_clear(board: SquareBoard, r1, c1, r2, c2):
        dr = r2 - r1
        dc = c2 - c1
        step_r = 0 if dr == 0 else (1 if dr > 0 else -1)
        step_c = 0 if dc == 0 else (1 if dc > 0 else -1)

        r = r1 + step_r
        c = c1 + step_c
        while (r, c) != (r2, c2):
            if board.get(r, c) != ".":
                return False
            r += step_r
            c += step_c
        return True

    def find_king(self, board: SquareBoard, white_turn: bool):
        target = "K" if white_turn else "к"
        for r in range(8):
            for c in range(8):
                if board.get(r, c) == target:
                    return (r, c)
        return None

    def can_attack(self, board: SquareBoard, r1, c1, r2, c2):
        p = board.get(r1, c1)
        if p == ".":
            return False

        dr = r2 - r1
        dc = c2 - c1

        # Пешка: атакует только по диагонали на 1 вперёд
        if p == "П" or p == "п":
            is_white = p.isupper()
            direction = -1 if is_white else 1
            return (dr == direction) and (abs(dc) == 1)

        # Остальные фигуры: через ООП
        obj = piece_from_symbol(p)
        if obj is None:
            return False
        return (r2, c2) in obj.pseudo_moves(board, r1, c1)

    def square_attacked_by(self, board: SquareBoard, attacker_white: bool, tr, tc):
        for r in range(8):
            for c in range(8):
                p = board.get(r, c)
                if p == ".":
                    continue
                if attacker_white and not self.is_white(p):
                    continue
                if (not attacker_white) and not self.is_black(p):
                    continue
                if self.can_attack(board, r, c, tr, tc):
                    return True
        return False

    def is_in_check(self, board: SquareBoard, white_turn: bool):
        kp = self.find_king(board, white_turn)
        if kp is None:
            return False
        kr, kc = kp
        return self.square_attacked_by(board, not white_turn, kr, kc)

    # --- пешка / en passant ---
    def validate_pawn_move(self, board: SquareBoard, r1, c1, r2, c2, white_turn: bool):
        p = board.get(r1, c1)
        dr = r2 - r1
        dc = c2 - c1
        target = board.get(r2, c2)

        direction = -1 if white_turn else 1
        start_row = 6 if white_turn else 1

        # вперёд на 1
        if dc == 0 and dr == direction and target == ".":
            return True, "ok"

        # вперёд на 2
        if dc == 0 and r1 == start_row and dr == 2 * direction and target == ".":
            between_r = r1 + direction
            if board.get(between_r, c1) == ".":
                return True, "double"

        # взятие по диагонали
        if abs(dc) == 1 and dr == direction and target != "." and not self.same_color(p, target):
            return True, "ok"

        # en passant
        if abs(dc) == 1 and dr == direction and target == "." and self.ep is not None:
            if self.ep.get("for_white") == white_turn and self.ep.get("target") == (r2, c2):
                return True, "enpassant"

        return False, "bad"

    # --- рокировка ---
    def validate_castling(self, board: SquareBoard, r1, c1, r2, c2, white_turn: bool):
        if r1 != r2 or abs(c2 - c1) != 2:
            return False

        king_piece = "K" if white_turn else "к"
        rook_piece = "Л" if white_turn else "л"

        if board.get(r1, c1) != king_piece:
            return False
        if self.moved.get(king_piece, False):
            return False

        if c2 > c1:
            rook_from = (r1, 7)
            squares_between = [(r1, 5), (r1, 6)]
            pass_squares = [(r1, 5), (r1, 6)]
        else:
            rook_from = (r1, 0)
            squares_between = [(r1, 1), (r1, 2), (r1, 3)]
            pass_squares = [(r1, 3), (r1, 2)]

        rf, cf = rook_from
        if board.get(rf, cf) != rook_piece:
            return False
        if self.moved.get(rook_from, False):
            return False

        for rr, cc in squares_between:
            if board.get(rr, cc) != ".":
                return False

        if self.is_in_check(board, white_turn):
            return False

        for rr, cc in pass_squares:
            if self.square_attacked_by(board, not white_turn, rr, cc):
                return False

        return True

    # --- симуляция хода (для проверки шаха после хода) ---
    def simulate_move(self, board: SquareBoard, move: Move, white_turn: bool, move_type: str):
        tmp = board.clone_grid()
        r1, c1, r2, c2 = move.r1, move.c1, move.r2, move.c2
        piece = tmp[r1][c1]

        def get(r, c): return tmp[r][c]
        def set_(r, c, v): tmp[r][c] = v

        if move_type == "castle":
            set_(r2, c2, piece)
            set_(r1, c1, ".")
            if c2 > c1:
                rook_from = (r1, 7)
                rook_to = (r1, 5)
            else:
                rook_from = (r1, 0)
                rook_to = (r1, 3)
            rf, cf = rook_from
            rt, ct = rook_to
            set_(rt, ct, get(rf, cf))
            set_(rf, cf, ".")
            return tmp

        if move_type == "enpassant":
            set_(r2, c2, piece)
            set_(r1, c1, ".")
            if self.ep and self.ep.get("captured"):
                cr, cc = self.ep["captured"]
                set_(cr, cc, ".")
            return tmp

        set_(r2, c2, piece)
        set_(r1, c1, ".")
        return tmp

    # --- легальность хода ---
    def validate_move(self, board: SquareBoard, move: Move, white_turn: bool):
        r1, c1, r2, c2 = move.r1, move.c1, move.r2, move.c2

        if not board.in_bounds(r1, c1) or not board.in_bounds(r2, c2):
            return False, "Координаты вне доски."

        piece = board.get(r1, c1)
        if piece == ".":
            return False, "На выбранной клетке нет фигуры."

        if white_turn and not self.is_white(piece):
            return False, "Сейчас ход белых."
        if (not white_turn) and not self.is_black(piece):
            return False, "Сейчас ход чёрных."

        target = board.get(r2, c2)
        if self.same_color(piece, target):
            return False, "Нельзя ходить на свою фигуру."

        P = self.piece_type(piece)
        if P is None:
            return False, "Неизвестная фигура (ошибка в доске)."

        dr = r2 - r1
        dc = c2 - c1
        move_type = "ok"

        # рокировка
        if P == "K" and dr == 0 and abs(dc) == 2:
            if self.validate_castling(board, r1, c1, r2, c2, white_turn):
                move_type = "castle"
            else:
                return False, "Рокировка невозможна."
        else:
            ok = False
            if P == "P":
                ok, pawn_info = self.validate_pawn_move(board, r1, c1, r2, c2, white_turn)
                if ok and pawn_info == "enpassant":
                    move_type = "enpassant"
                elif ok:
                    move_type = "ok"
                else:
                    ok = False


            elif P == "N":

                # Переход на ООП: конь сам знает свои ходы

                obj = piece_from_symbol(piece)  # piece — это символ с доски

                if obj is None:

                    ok = False

                else:

                    ok = (r2, c2) in obj.pseudo_moves(board, r1, c1)

            # --- en passant: пешка может идти по диагонали на ПУСТУЮ клетку, если совпало с ep target
            if (not ok) and self.ep and board.get(r2, c2) == ".":
                ep_target = self.ep.get("target") or self.ep.get("to")
                if ep_target == (r2, c2):
                    # доп. безопасность: ход действительно диагональный на 1 вперёд
                    direction = -1 if piece.isupper() else 1
                    if (r2 - r1) == direction and abs(c2 - c1) == 1:
                        ok = True
                        return True, "enpassant"




            elif P == "B":

                obj = piece_from_symbol(piece)

                if obj is None:

                    ok = False

                else:

                    ok = (r2, c2) in obj.pseudo_moves(board, r1, c1)



            elif P == "R":

                obj = piece_from_symbol(piece)

                if obj is None:

                    ok = False

                else:

                    ok = (r2, c2) in obj.pseudo_moves(board, r1, c1)


            elif P == "Q":

                obj = piece_from_symbol(piece)

                if obj is None:

                    ok = False

                else:

                    ok = (r2, c2) in obj.pseudo_moves(board, r1, c1)



            elif P == "K":

                obj = piece_from_symbol(piece)

                if obj is None:

                    ok = False

                else:

                    ok = (r2, c2) in obj.pseudo_moves(board, r1, c1)

        # нельзя оставлять короля под шахом
        tmp_grid = self.simulate_move(board, move, white_turn, move_type)
        tmp_board = SquareBoard()
        tmp_board.grid = tmp_grid
        if self.is_in_check(tmp_board, white_turn):
            return False, "Нельзя: после хода король под шахом."

        return True, move_type

    # --- применить ход (реальный) ---
    def apply_move(self, board: SquareBoard, move: Move, white_turn: bool, move_type: str):
        r1, c1, r2, c2 = move.r1, move.c1, move.r2, move.c2
        piece = board.get(r1, c1)
        king_piece = "K" if white_turn else "к"

        # по умолчанию en passant исчезает, появится только после double пешки
        new_ep = None

        if move_type == "castle":
            board.set(r2, c2, piece)
            board.set(r1, c1, ".")
            if c2 > c1:
                rook_from = (r1, 7)
                rook_to = (r1, 5)
            else:
                rook_from = (r1, 0)
                rook_to = (r1, 3)
            rf, cf = rook_from
            rt, ct = rook_to
            board.set(rt, ct, board.get(rf, cf))
            board.set(rf, cf, ".")
            self.moved[king_piece] = True
            self.moved[rook_from] = True
            self.ep = None
            return

        if move_type == "enpassant":
            board.set(r2, c2, piece)
            board.set(r1, c1, ".")
            if self.ep and self.ep.get("captured"):
                cr, cc = self.ep["captured"]
                board.set(cr, cc, ".")
            self.ep = None
            return

        # обычный ход
        board.set(r2, c2, piece)
        board.set(r1, c1, ".")

        if piece == king_piece:
            self.moved[king_piece] = True
        if piece.upper() == "Л":
            self.moved[(r1, c1)] = True

        # превращение пешки
        if piece == "П" and r2 == 0:
            board.set(r2, c2, "Ф")
        if piece == "п" and r2 == 7:
            board.set(r2, c2, "ф")

        # double пешки -> включить ep
        if piece.upper() == "П" and abs(r2 - r1) == 2:
            mid_r = (r1 + r2) // 2
            new_ep = {"target": (mid_r, c1), "captured": (r2, c1), "for_white": (not white_turn)}

        self.ep = new_ep



    # --- подсказки / мат-пат ---
    def all_legal_moves(self, board: SquareBoard, white_turn: bool):
        moves = []
        for r1 in range(8):
            for c1 in range(8):
                p = board.get(r1, c1)
                if p == ".":
                    continue
                if white_turn and not self.is_white(p):
                    continue
                if (not white_turn) and not self.is_black(p):
                    continue
                for r2 in range(8):
                    for c2 in range(8):
                        mv = Move(r1, c1, r2, c2)
                        ok, info = self.validate_move(board, mv, white_turn)
                        if ok:
                            moves.append((mv, info))
        return moves

    def has_any_legal_move(self, board: SquareBoard, white_turn: bool):
        return len(self.all_legal_moves(board, white_turn)) > 0

    def cmd_hint(self, board: SquareBoard, white_turn: bool, sq: str):
        pos = Move.parse_square(sq)
        if pos is None:
            print("Пример: hint e2")
            return
        r1, c1 = pos
        piece = board.get(r1, c1)
        if piece == ".":
            print("На этой клетке нет фигуры.")
            return
        if white_turn and not self.is_white(piece):
            print("Сейчас ход белых — выбери белую фигуру.")
            return
        if (not white_turn) and not self.is_black(piece):
            print("Сейчас ход чёрных — выбери чёрную фигуру.")
            return

        targets = []
        for r2 in range(8):
            for c2 in range(8):
                mv = Move(r1, c1, r2, c2)
                ok, _ = self.validate_move(board, mv, white_turn)
                if ok:
                    targets.append(Move.rc_to_sq(r2, c2))

        if not targets:
            print("У этой фигуры нет легальных ходов.")
        else:
            print("Легальные ходы:", ", ".join(targets))

    def cmd_threatened(self, board: SquareBoard, white_turn: bool):
        attacked = []
        for r in range(8):
            for c in range(8):
                p = board.get(r, c)
                if p == ".":
                    continue
                if white_turn and not self.is_white(p):
                    continue
                if (not white_turn) and not self.is_black(p):
                    continue
                if self.square_attacked_by(board, not white_turn, r, c):
                    attacked.append(Move.rc_to_sq(r, c))

        if attacked:
            print("Под боем ваши фигуры на:", ", ".join(attacked))
        else:
            print("Сейчас ни одна ваша фигура не под боем.")

        if self.is_in_check(board, white_turn):
            print("ВАШ КОРОЛЬ ПОД ШАХОМ!")
