from .exceptions import *
from .utils import *
from .cell import Cell

class Board:
    """
    Create the mainboard of the game

    :property rows: The amount of rows of the board.
    :property cols: The amount of columns of the board.
    :property board_array: The array of the board.
    :property game_over: Boolean that indicates if the game is over.
    :property correct_flags: The amount of flags that are correct.
    :property total_mined: The amount of mines on the board.
    """

    def __init__(self, rows: int, cols: int):
        if not 1 < rows < 100 or not 1 < cols < 100:
            raise ImplementationError("Invalid board size (Maximum 99x99, minimum 2x2)")
        self.rows = rows
        self.cols = cols
        self.board_array = [[Cell(i, j) for j in range(cols)] for i in range(rows)]
        self.game_over = False
        self.correct_flags = 0
        self.total_mined = 0

    def reveal(self, row: int, col: int):
        """
        Reveals a cell on the board.

        :param row: The row of the cell to reveal.
        :param col: The column of the cell to reveal.

        :return: A Set of tuples of the revealed cells {(row, column, revealed value), ...}, or just one tuple representing one revealed cell (row, column , revealed value).
        """
        if self.cell(row, col).flagged:
            self.cell(row, col).flagged = False
        if self.cell(row, col).revealed:
            raise GameError("Cell already revealed.")
        if self.cell(row, col).mine:
            raise GameOver(False)
        self.board_array[row][col].revealed = True
        self.total_mined += 1
        if self.correct_flags + self.total_mined == self.rows * self.cols:
            raise GameOver(True)
        self.revealed = set()
        self.AMine(row, col)
        self.revealed.add((row, col, self.cell(row, col).value))
        return self.revealed if len(self.revealed) > 1 else (row, col, self.cell(row, col).value)

    def flag(self, row: int, col: int):
        """
        Flags a cell with a specified row and column.

        :param row: The row of the cell.
        :param col: The column of the cell.

        :return: None
        """
        if self.cell(row, col).flagged:
            self.board_array[row][col].flagged = False
            if self.cell(row, col).mine:
                self.correct_flags -= 1
            return
        if self.cell(row, col).revealed:
            raise GameError("You cannot flag a revealed cell.")
        self.board_array[row][col].flagged = True
        if self.cell(row, col).mine:
            self.correct_flags += 1
            if self.correct_flags + self.total_mined == self.rows * self.cols:
                raise GameOver(True)

    def AMine(self, row: int, column: int):
        """
        Automatic Click (Not repeated)

        :param row: The row of the cell.
        :param column: The column of the cell.

        :return: None
        """
        if (self.rows * self.cols) / 2 < self.mines_n: 
            return
        self.checked = set()
        self._AMine(row, column)
        if self.correct_flags + self.total_mined == self.rows * self.cols:
            raise GameOver(True)
        

    def _AMine(self, row: int, column: int):
        """
        Automatic Click (Repeated)

        :param row: The row of the cell.
        :param column: The column of the cell.

        :return: None
        """
        if (row, column) in self.checked:
            return
        if self.board_array[row][column].revealed and len(self.checked) != 0:
            return
        self.checked.add((row, column))
        self.board_array[row][column].revealed = True
        self.total_mined += 1
        self.revealed.add((row, column, self.cell(row, column).value))
        if self.cell(row, column).value > 0:
            return
        else:
            for (i, j) in find_neighbors(self.board_array, row, column):
                self._AMine(i, j)

    def cell(self, row: int, col: int):
        """
        Returns a Cell object from the specified parameters.

        :param row: The row of the cell.
        :param col: The column of the cell.

        :return: The Cell object.
        """
        return self.board_array[row][col]

    def place_mines(self, amount: int, exclude: tuple=None):
        """
        Places the mines on the board.

        :param amount maximum=rows of the board * columns of the board: The amount of mines to place.
        :param exclude: Tuple of (row, column) of the cell to exclude from the placement, (Excludes other cells around it too, this will not work if the size of the board is less than 16 cells).

        :return: None
        """
        self.mines_n = amount
        if amount > (self.rows * self.cols):
            raise ImplementationError("Too many mines for board size.")
        self.board_array = make_mines(self.board_array, self.rows, self.cols, amount, exclude)

    def show_real_board(self):
        """
        Shows the real board with the positions of the mines and everything.

        :return: A string representing the real board.
        """
        res = ""
        for row in self.board_array:
            for col in row:
                if col.mine:
                    res += "*  "
                elif col.value != -1:
                    res += f"{col.value}  "
                else:
                    res += "-  "
            res += "\n"
        return res

    def visualize(self):
        """
        Visualizes the board that the player is supposed to see

        :return: A string representing the visualized board.
        """
        res = ""
        for row in self.board_array:
            for col in row:
                if col.flagged:
                    res += "F  "
                    continue
                if col.value != -1:
                    res += f"{col.value}  " if col.revealed else "?  "
                    continue
                else:
                    res += "-  " if col.revealed else "?  "
                    continue
                if col.mine:
                    res += "?  "
                    continue
            res += "\n"
        return res