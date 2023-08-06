class Cell:
    """
    Cell object

    :property row: The row of the cell.
    :property column: The column of the cell.
    :property mine: Whether the cell is a mine.
    :property flagged: Whether the cell is flagged.
    :property revealed: Whether the cell is revealed.
    :property value: The value of the cell (-1 if unknown).
    """
    def __init__(self, row: int, column: int):
        self.row = row
        self.column = column
        self.mine = False
        self.flagged = False
        self.revealed = False
        self.value = -1