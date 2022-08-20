from sudoku.solver import SudokuSolver
from sudoku.utils import read_from_file
from sudoku.data import SudokuData


filename = "./puzzles/puzzle2.txt"

with open(filename) as f:
    puzzle = read_from_file(f)

solver = SudokuSolver(puzzle)
solution = solver.solve()
if solution: solution.print()