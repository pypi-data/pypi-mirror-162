# Minesweeper
This is a library to make simple minesweeper games using OOP

Example Usage:
```py
from Minesweeper import Board # Import the Board object from the library

b = Board(5, 5) # Create the Board instance
b.place_mines(5) # Place 5 mines on our 5x5 board
while True: # Loop forever
    inp = input("Enter row, column: ") # Take input
    f_or_r = inp[0] # Check if user wants to flag or reveal
    row = int(inp[1:].split()[0]) # Get the row from the input  
    col = int(inp[1:].split()[1]) # Get the column from the input
    if f_or_r == "f": # If input is to flag
        b.flag(row, col) # Use flag() to flag the cell
        print(b.visualize()) # Use visualize() to get a string of the updated board
    elif f_or_r == "r": # If the input is to reveal
        b.reveal(row, col) # Use reveal() to reveal the value of the cell
        print(b.visualize()) # Use visualize() to get a string of the updated board
```

Made by: Ousama Alhennawi