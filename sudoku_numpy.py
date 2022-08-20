from fileinput import filename
import numpy as np
from typing import List
from sudoku.utils import read_from_file

from numba import int8, jit
from numba.experimental import jitclass

ALL_NUMBERS = set(range(1, 10))

spec = [
    ("data", int8[:, :])
]

@jitclass(spec)
class SudokuDataNP:
    
    def __init__(self, puzzle_data):
        self.data = np.array(puzzle_data, dtype=int8).reshape((9,9))

    
    def column(self, column: int):
        return self.data[:,column]

    
    def row(self, row:int):
        return self.data[row, :]

    @jit(int8[:](int8))
    def subsquare(self, subsquare: int):
        col = subsquare % 3
        row = subsquare // 3

        return self.data[3*row:3*(row+1), 3*col:3*(col+1)].reshape((9))

    
    def is_row_solved(self, row: int):
        return set(self.row(row)) == self.ALL_NUMBERS

    
    def is_column_solved(self, column: int):
        return set(self.column(column)) == self.ALL_NUMBERS

    
    def is_subsquare_solved(self, subsquare: int):
        return set(self.subsquare(subsquare)) == self.ALL_NUMBERS

    
    def is_puzzle_solved(self):
        for i in range(9):
            if not self.is_row_solved(i): return False
            if not self.is_column_solved(i): return False
            if not self.is_subsquare_solved(i): return False
        return True



filename = "./puzzles/puzzle_bad.txt"
with open(filename) as f:
    sudoku_data = read_from_file(f)

sudoku_data_np = SudokuDataNP(sudoku_data.data)

sudoku_data.print()

print(sudoku_data_np.data)

print("Row 1")
print(tuple(sudoku_data.row(1)))
print(sudoku_data_np.row(1))

print("Column 2")
print(tuple(sudoku_data.column(2)))
print(sudoku_data_np.column(2))

print("Subsquare 4")
print(tuple(sudoku_data.sub_square(4)))
print(sudoku_data_np.subsquare(4))

print(sudoku_data_np.is_puzzle_solved())