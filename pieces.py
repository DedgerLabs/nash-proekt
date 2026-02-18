# pieces.py
from __future__ import annotations


class Piece:
    """
    Базовый класс фигуры.
    Пока доска хранит СИМВОЛЫ (строки), а мы создаём объект фигуры "на лету"
    по символу и спрашиваем у него псевдоходы.
    """
    def __init__(self, is_white: bool):
        self.is_white = is_white

    def pseudo_moves(self, board, r: int, c: int):
        raise NotImplementedError


def _slide_moves(board, r: int, c: int, is_white: bool, directions):
    """
    Универсальный генератор ходов для слона/ладьи/ферзя.
    directions: список (dr, dc)
    """
    moves = []
    for dr, dc in directions:
        r2, c2 = r + dr, c + dc
        while board.in_bounds(r2, c2):
            target = board.get(r2, c2)
            if target == ".":
                moves.append((r2, c2))
            else:
                target_white = target.isupper()
                if target_white != is_white:  # можно бить чужую
                    moves.append((r2, c2))
                break  # дальше за фигурой идти нельзя
            r2 += dr
            c2 += dc
    return moves


class Bishop(Piece):
    DIRECTIONS = (
        (-1, -1), (-1, +1),
        (+1, -1), (+1, +1),
    )

    def pseudo_moves(self, board, r: int, c: int):
        return _slide_moves(board, r, c, self.is_white, self.DIRECTIONS)


class Rook(Piece):
    DIRECTIONS = (
        (-1, 0), (+1, 0),
        (0, -1), (0, +1),
    )

    def pseudo_moves(self, board, r: int, c: int):
        return _slide_moves(board, r, c, self.is_white, self.DIRECTIONS)

class Queen(Piece):
    DIRECTIONS = (
        # как ладья
        (-1, 0), (+1, 0), (0, -1), (0, +1),
        # как слон
        (-1, -1), (-1, +1), (+1, -1), (+1, +1),
    )

    def pseudo_moves(self, board, r: int, c: int):
        return _slide_moves(board, r, c, self.is_white, self.DIRECTIONS)

class King(Piece):
    OFFSETS = (
        (-1, -1), (-1, 0), (-1, +1),
        (0, -1),           (0, +1),
        (+1, -1), (+1, 0), (+1, +1),
    )

    def pseudo_moves(self, board, r: int, c: int):
        moves = []
        for dr, dc in self.OFFSETS:
            r2, c2 = r + dr, c + dc
            if not board.in_bounds(r2, c2):
                continue
            target = board.get(r2, c2)
            if target == ".":
                moves.append((r2, c2))
            else:
                target_white = target.isupper()
                if target_white != self.is_white:
                    moves.append((r2, c2))
        return moves





class Knight(Piece):
    OFFSETS = (
        (-2, -1), (-2, +1),
        (-1, -2), (-1, +2),
        (+1, -2), (+1, +2),
        (+2, -1), (+2, +1),
    )

    def pseudo_moves(self, board, r: int, c: int):
        moves = []
        for dr, dc in self.OFFSETS:
            r2, c2 = r + dr, c + dc
            if not board.in_bounds(r2, c2):
                continue

            target = board.get(r2, c2)

            # пустая клетка
            if target == ".":
                moves.append((r2, c2))
            else:
                # можно бить только чужую фигуру
                target_white = target.isupper()
                if target_white != self.is_white:
                    moves.append((r2, c2))

        return moves


def piece_from_symbol(symbol: str) -> Piece | None:
    if symbol == ".":
        return None

    is_white = symbol.isupper()

    # конь: белый "К", чёрный "н"
    if symbol == "К" or symbol == "н":
        return Knight(is_white=is_white)

    # слон: белый "С", чёрный "с"
    if symbol == "С" or symbol == "с":
        return Bishop(is_white=is_white)

    # ладья: белая "Л", чёрная "л"
    if symbol == "Л" or symbol == "л":
        return Rook(is_white=is_white)

    # ферзь: белый "Ф", чёрный "ф"
    if symbol == "Ф" or symbol == "ф":
        return Queen(is_white=is_white)

    # король: белый "K", чёрный "к"
    if symbol == "K" or symbol == "к":
        return King(is_white=is_white)

    return None
