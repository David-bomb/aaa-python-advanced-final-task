import random
from copy import deepcopy
from typing import Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum


class Symbol(str, Enum):
    """Символы игры"""
    FREE = '.'
    CROSS = 'X'
    ZERO = 'O'


@dataclass
class GameResult:
    """Результат проверки состояния игры"""
    is_finished: bool
    winner: Optional[Symbol] = None
    is_draw: bool = False


class TicTacToeGame:
    """
    Класс, инкапсулирующий логику игры в крестики-нолики.
    Поддерживает расширение для мультиплеера.
    """
    BOARD_SIZE = 3

    def __init__(self, board: Optional[List[List[str]]] = None):
        """Инициализация игры с пустым полем или заданным состоянием"""
        if board is None:
            self.board = self._create_empty_board()
        else:
            self.board = deepcopy(board)

    def _create_empty_board(self) -> List[List[str]]:
        """Создание пустого игрового поля"""
        return [[Symbol.FREE.value for _ in range(self.BOARD_SIZE)]
                for _ in range(self.BOARD_SIZE)]

    def make_move(self, row: int, col: int, symbol: Symbol) -> bool:
        """
        Сделать ход.
        Возвращает True если ход успешен, False если клетка занята.
        """
        if not self._is_valid_position(row, col):
            return False
        if self.board[row][col] != Symbol.FREE.value:
            return False
        self.board[row][col] = symbol.value
        return True

    def _is_valid_position(self, row: int, col: int) -> bool:
        """Проверка валидности координат"""
        return 0 <= row < self.BOARD_SIZE and 0 <= col < self.BOARD_SIZE

    def get_free_cells(self) -> List[Tuple[int, int]]:
        """Получить список свободных клеток"""
        free_cells = []
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                if self.board[row][col] == Symbol.FREE.value:
                    free_cells.append((row, col))
        return free_cells

    def check_winner(self) -> GameResult:
        """
        Проверка состояния игры.
        Возвращает GameResult с информацией о победителе или ничьей.
        """
        # Проверка строк
        for row in self.board:
            if self._check_line(row):
                return GameResult(is_finished=True, winner=Symbol(row[0]))

        # Проверка столбцов
        for col in range(self.BOARD_SIZE):
            column = [self.board[row][col] for row in range(self.BOARD_SIZE)]
            if self._check_line(column):
                return GameResult(is_finished=True, winner=Symbol(column[0]))

        # Проверка главной диагонали
        main_diag = [self.board[i][i] for i in range(self.BOARD_SIZE)]
        if self._check_line(main_diag):
            return GameResult(is_finished=True, winner=Symbol(main_diag[0]))

        # Проверка побочной диагонали
        anti_diag = [
            self.board[i][self.BOARD_SIZE - 1 - i]
            for i in range(self.BOARD_SIZE)
        ]
        if self._check_line(anti_diag):
            return GameResult(is_finished=True, winner=Symbol(anti_diag[0]))

        # Проверка на ничью (нет свободных клеток)
        if not self.get_free_cells():
            return GameResult(is_finished=True, is_draw=True)

        # Игра продолжается
        return GameResult(is_finished=False)

    def _check_line(self, line: List[str]) -> bool:
        """Проверка, все ли символы в линии одинаковые и не пустые"""
        if line[0] == Symbol.FREE.value:
            return False
        return all(cell == line[0] for cell in line)

    def get_board(self) -> List[List[str]]:
        """Получить копию текущего состояния поля"""
        return deepcopy(self.board)


class AIPlayer:
    """
    ИИ-оппонент для игры в крестики-нолики.
    Использует случайный выбор хода (можно расширить для более умного ИИ).
    """

    def __init__(self, symbol: Symbol = Symbol.ZERO):
        self.symbol = symbol

    def make_move(self, game: TicTacToeGame) -> Optional[Tuple[int, int]]:
        """
        Выбрать и сделать ход.
        Возвращает координаты хода или None, если ход невозможен.
        """
        free_cells = game.get_free_cells()
        if not free_cells:
            return None

        # Случайный выбор клетки
        row, col = random.choice(free_cells)
        game.make_move(row, col, self.symbol)
        return (row, col)


# Вспомогательные функции для совместимости с шаблоном

def get_default_state() -> List[List[str]]:
    """Получить начальное состояние игрового поля"""
    return TicTacToeGame()._create_empty_board()


def check_winner_from_board(board: List[List[str]]) -> GameResult:
    """Проверить победителя по состоянию поля"""
    game = TicTacToeGame(board)
    return game.check_winner()


def make_ai_move(board: List[List[str]]) -> Optional[Tuple[int, int]]:
    """Сделать ход ИИ и вернуть координаты"""
    game = TicTacToeGame(board)
    ai = AIPlayer(Symbol.ZERO)
    move = ai.make_move(game)
    if move:
        row, col = move
        board[row][col] = Symbol.ZERO.value
    return move
