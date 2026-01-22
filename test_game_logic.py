import pytest
from game_logic import (
    TicTacToeGame,
    AIPlayer,
    Symbol,
    get_default_state,
    check_winner_from_board,
    make_ai_move,
)


class TestTicTacToeGame:
    """Тесты для класса TicTacToeGame"""

    def test_initial_board_is_empty(self):
        """Проверка, что начальное поле пустое"""
        game = TicTacToeGame()
        for row in game.board:
            for cell in row:
                assert cell == Symbol.FREE.value

    def test_make_valid_move(self):
        """Проверка успешного хода"""
        game = TicTacToeGame()
        result = game.make_move(0, 0, Symbol.CROSS)
        assert result is True
        assert game.board[0][0] == Symbol.CROSS.value

    def test_make_move_to_occupied_cell(self):
        """Проверка, что нельзя ходить в занятую клетку"""
        game = TicTacToeGame()
        game.make_move(0, 0, Symbol.CROSS)
        result = game.make_move(0, 0, Symbol.ZERO)
        assert result is False
        assert game.board[0][0] == Symbol.CROSS.value

    def test_make_move_invalid_position(self):
        """Проверка невалидных координат"""
        game = TicTacToeGame()
        assert game.make_move(-1, 0, Symbol.CROSS) is False
        assert game.make_move(0, 3, Symbol.CROSS) is False
        assert game.make_move(5, 5, Symbol.CROSS) is False

    def test_get_free_cells_initial(self):
        """Проверка количества свободных клеток в начале"""
        game = TicTacToeGame()
        free_cells = game.get_free_cells()
        assert len(free_cells) == 9

    def test_get_free_cells_after_moves(self):
        """Проверка количества свободных клеток после ходов"""
        game = TicTacToeGame()
        game.make_move(0, 0, Symbol.CROSS)
        game.make_move(1, 1, Symbol.ZERO)
        free_cells = game.get_free_cells()
        assert len(free_cells) == 7
        assert (0, 0) not in free_cells
        assert (1, 1) not in free_cells


class TestWinConditions:
    """Тесты для проверки условий победы"""

    def test_win_horizontal_row_0(self):
        """Проверка победы по горизонтали (первая строка)"""
        game = TicTacToeGame()
        game.make_move(0, 0, Symbol.CROSS)
        game.make_move(0, 1, Symbol.CROSS)
        game.make_move(0, 2, Symbol.CROSS)

        result = game.check_winner()
        assert result.is_finished is True
        assert result.winner == Symbol.CROSS

    def test_win_horizontal_row_1(self):
        """Проверка победы по горизонтали (вторая строка)"""
        game = TicTacToeGame()
        game.make_move(1, 0, Symbol.ZERO)
        game.make_move(1, 1, Symbol.ZERO)
        game.make_move(1, 2, Symbol.ZERO)

        result = game.check_winner()
        assert result.is_finished is True
        assert result.winner == Symbol.ZERO

    def test_win_vertical_col_0(self):
        """Проверка победы по вертикали (первый столбец)"""
        game = TicTacToeGame()
        game.make_move(0, 0, Symbol.CROSS)
        game.make_move(1, 0, Symbol.CROSS)
        game.make_move(2, 0, Symbol.CROSS)

        result = game.check_winner()
        assert result.is_finished is True
        assert result.winner == Symbol.CROSS

    def test_win_vertical_col_2(self):
        """Проверка победы по вертикали (третий столбец)"""
        game = TicTacToeGame()
        game.make_move(0, 2, Symbol.ZERO)
        game.make_move(1, 2, Symbol.ZERO)
        game.make_move(2, 2, Symbol.ZERO)

        result = game.check_winner()
        assert result.is_finished is True
        assert result.winner == Symbol.ZERO

    def test_win_main_diagonal(self):
        """Проверка победы по главной диагонали"""
        game = TicTacToeGame()
        game.make_move(0, 0, Symbol.CROSS)
        game.make_move(1, 1, Symbol.CROSS)
        game.make_move(2, 2, Symbol.CROSS)

        result = game.check_winner()
        assert result.is_finished is True
        assert result.winner == Symbol.CROSS

    def test_win_anti_diagonal(self):
        """Проверка победы по побочной диагонали"""
        game = TicTacToeGame()
        game.make_move(0, 2, Symbol.ZERO)
        game.make_move(1, 1, Symbol.ZERO)
        game.make_move(2, 0, Symbol.ZERO)

        result = game.check_winner()
        assert result.is_finished is True
        assert result.winner == Symbol.ZERO

    def test_draw(self):
        """Проверка ничьей"""
        # Создаём ничейную позицию:
        # X O X
        # X X O
        # O X O
        board = [
            ['X', 'O', 'X'],
            ['X', 'X', 'O'],
            ['O', 'X', 'O'],
        ]
        game = TicTacToeGame(board)

        result = game.check_winner()
        assert result.is_finished is True
        assert result.is_draw is True
        assert result.winner is None

    def test_game_not_finished(self):
        """Проверка незавершённой игры"""
        game = TicTacToeGame()
        game.make_move(0, 0, Symbol.CROSS)
        game.make_move(1, 1, Symbol.ZERO)

        result = game.check_winner()
        assert result.is_finished is False
        assert result.winner is None
        assert result.is_draw is False


class TestAIPlayer:
    """Тесты для ИИ-оппонента"""

    def test_ai_makes_move(self):
        """Проверка, что ИИ делает ход"""
        game = TicTacToeGame()
        ai = AIPlayer(Symbol.ZERO)

        move = ai.make_move(game)

        assert move is not None
        row, col = move
        assert game.board[row][col] == Symbol.ZERO.value

    def test_ai_move_on_full_board(self):
        """Проверка, что ИИ не ходит на заполненном поле"""
        board = [
            ['X', 'O', 'X'],
            ['X', 'X', 'O'],
            ['O', 'X', 'O'],
        ]
        game = TicTacToeGame(board)
        ai = AIPlayer(Symbol.ZERO)

        move = ai.make_move(game)

        assert move is None

    def test_ai_chooses_free_cell(self):
        """Проверка, что ИИ выбирает свободную клетку"""
        game = TicTacToeGame()
        ai = AIPlayer(Symbol.ZERO)

        # Делаем несколько ходов ИИ
        for _ in range(4):
            move = ai.make_move(game)
            if move:
                row, col = move
                # Проверяем, что в выбранной клетке теперь O
                assert game.board[row][col] == Symbol.ZERO.value


class TestHelperFunctions:
    """Тесты для вспомогательных функций"""

    def test_get_default_state(self):
        """Проверка создания начального состояния"""
        state = get_default_state()
        assert len(state) == 3
        assert all(len(row) == 3 for row in state)
        assert all(cell == Symbol.FREE.value for row in state for cell in row)

    def test_get_default_state_independence(self):
        """Проверка независимости копий состояния"""
        state1 = get_default_state()
        state2 = get_default_state()
        state1[0][0] = 'X'
        assert state2[0][0] == Symbol.FREE.value

    def test_check_winner_from_board(self):
        """Проверка функции check_winner_from_board"""
        board = [
            ['X', 'X', 'X'],
            ['.', 'O', '.'],
            ['O', '.', '.'],
        ]
        result = check_winner_from_board(board)
        assert result.is_finished is True
        assert result.winner == Symbol.CROSS

    def test_make_ai_move(self):
        """Проверка функции make_ai_move"""
        board = get_default_state()
        move = make_ai_move(board)

        assert move is not None
        row, col = move
        assert board[row][col] == Symbol.ZERO.value


class TestGameFlow:
    """Тесты для полного игрового процесса"""

    def test_full_game_x_wins(self):
        """Проверка полной игры с победой X"""
        game = TicTacToeGame()

        # X побеждает по диагонали
        moves = [
            (0, 0, Symbol.CROSS),
            (0, 1, Symbol.ZERO),
            (1, 1, Symbol.CROSS),
            (0, 2, Symbol.ZERO),
            (2, 2, Symbol.CROSS),
        ]

        for row, col, symbol in moves:
            game.make_move(row, col, symbol)

        result = game.check_winner()
        assert result.is_finished is True
        assert result.winner == Symbol.CROSS

    def test_full_game_o_wins(self):
        """Проверка полной игры с победой O"""
        game = TicTacToeGame()

        # O побеждает по вертикали
        moves = [
            (0, 0, Symbol.CROSS),
            (0, 1, Symbol.ZERO),
            (1, 0, Symbol.CROSS),
            (1, 1, Symbol.ZERO),
            (2, 2, Symbol.CROSS),
            (2, 1, Symbol.ZERO),
        ]

        for row, col, symbol in moves:
            game.make_move(row, col, symbol)

        result = game.check_winner()
        assert result.is_finished is True
        assert result.winner == Symbol.ZERO


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
