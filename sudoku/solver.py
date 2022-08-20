from .data import SudokoSuperRow, SudokuData, DataState
from itertools import permutations, product, accumulate
from collections import defaultdict

from types import Dict, Set
from progress.bar import Bar
import time

import enum

class SudokuSolver:
    def __init__(self, puzzle_data):
        if isinstance(puzzle_data, SudokuData):
            self._puzzle_data = puzzle_data
        else:
            self._puzzle_data = SudokuData(puzzle_data)
        self.iter = 0
        self.possible_values = defaultdict(list)
        self.solution = self._puzzle_data.copy()

        self.pass_over_puzzle()  # Generate possible values

    @property
    def puzzle_data(self):
        return self._puzzle_data

    def pass_over_puzzle(self):
        
        for idx in self._puzzle_data.puzzle_idxs:
            if idx in self.solution:
                continue

            possible_values = SudokuData.ALL_NUMBERS.copy()

            row_values = set(self.puzzle_data.iter_row_from_idx(idx))
            col_values = set(self.puzzle_data.iter_column_from_idx(idx))
            subsquare_values = set(self.puzzle_data.iter_subsquare_from_idx(idx))

            possible_values = SudokuData.ALL_NUMBERS.copy()
            possible_values.difference_update(row_values)
            possible_values.difference_update(col_values)
            possible_values.difference_update(subsquare_values) 
            
            self.possible_values[idx] = possible_values

    def iter_single_possibles(self):
        """Filters the possible values to the ones with a single possibiity.
        Returns an iterator mapping of (idx, value) values"""

        return map(
            lambda els: (els[0], tuple(els[1])[0]), 
            filter(
                lambda items: len(items[1])==1, 
                self.possible_values.items()
            )
        )
    
    def iter_possble_values(self, row=None, column=None, sub_square=None):
        """Returns the possible values for a row, column, or subsquare"""

        if row is not None:
            for el in self.iter_possible_row(row):
                yield el

        if column is not None:
            for el in self.iter_possible_column(column):
                yield el
        
        if sub_square is not None:
            for el in self.iter_possible_subsquare(sub_square):
                yield el
        
    def iter_possible_row(self, row):
        for idx in self.puzzle_data.row_indices(row):
            if idx in self.possible_values:
                yield (idx, self.possible_values[idx])
    
    def iter_possible_column(self, column):
        for idx in self.puzzle_data.column_indices(column):
            if idx in self.possible_values:
                yield (idx, self.possible_values[idx])

    def iter_possible_subsquare(self, subsquare, ignore_row=None, ignore_column=None):
        ignore_idxs = []
        if ignore_row is not None:
            if SudokuData.is_row_in_subsquare(ignore_row, subsquare):
                ignore_idxs.extend(SudokuData.row_indices(ignore_row))
        
        if ignore_column is not None:
            if SudokuData.is_column_in_subsquare(ignore_column, subsquare):
                ignore_idxs.extend(SudokuData.column_indices(ignore_column))
        
        for idx in self.puzzle_data.subsquare_indices(subsquare):
            if idx in self.possible_values:
                if idx not in ignore_idxs:
                    yield (idx, self.possible_values[idx])
    
    def filter_iter_by_single_values(self, idx_iterator):
        # This monstrosity gets all possibles for an index iterator,
        # For each of these filter the possibles by values
        # Finally, filter the ones where there is only 1 result
        
        def possible_cells_for_value(possibles, value):
            return filter(lambda x: x[1] and value in x[1], possibles)
        
        possibles = [(idx, self.possible_values.get(idx)) for idx in idx_iterator]
        # [(idx: int, values: <{value:int,}|None>),]

        possibles_by_value = map(lambda value: (value, tuple(possible_cells_for_value(possibles, value))), SudokuData.ALL_NUMBERS)
        
        single_possibles_by_value = map(lambda el: (el[1][0][0], el[0]), filter(lambda x: len(x[1]) ==1, possibles_by_value))

        # [(idx: int, values: {value: int})]

        for idx, val in single_possibles_by_value:
            yield idx, val


        # [(idx, val), ]

    def iter_single_value_possibles(self):

        def do_the_thing(iterator):
            return map(lambda i: tuple(self.filter_iter_by_single_values(iterator(i))), range(9))

        for el in do_the_thing(SudokuData.column_indices):
            if el:
                yield el[0]
        
        for el in do_the_thing(SudokuData.row_indices):
            if el:
                yield el[0]
        
        for el in do_the_thing(SudokuData.subsquare_indices):
            if el:
                yield el[0]
        


    def remove_from_possibles(self, idx, value):
        try:
            self.possible_values[idx].remove(value)        
        except (KeyError, ValueError):
            pass

    def update_solution(self, idx, value):
        self.solution.set(idx, value)
        
        del self.possible_values[idx]

        for row_idx in SudokuData.row_indices(SudokuData.row_from_idx(idx)):
            self.remove_from_possibles(row_idx, value)

        for column_idx in SudokuData.column_indices(SudokuData.column_from_idx(idx)):
            self.remove_from_possibles(column_idx, value)

        for subsquare_idx in SudokuData.subsquare_indices(SudokuData.subsquare_from_idx(idx)):
            self.remove_from_possibles(subsquare_idx, value)

    def solve_by_passes(self):
        print("Solving Via Iterated Passes")

        while not self.solution.is_puzzle_solved():
            self.iter += 1
            solution_copy = self.solution.copy()
            # print(f"Iter: {self.iter}")
            # self.solution.print()
            
            # Check for any cells with only 1 possibility
            # Update and iterate until no more exist
            single_possibilities = tuple(self.iter_single_possibles())
            while single_possibilities:
                for (idx, val) in single_possibilities:
                    self.update_solution(idx, val)
                single_possibilities = tuple(self.iter_single_possibles())
            
            
            # Check for any values that have to be in a cell due to row/column/subsquare restrictions
            for (idx, val) in self.iter_single_value_possibles():
                self.update_solution(idx, val)
       
            if self.solution == solution_copy:
                print(f"No new free spaces found after {self.iter} passes")
                # self.solution.print()
                return

        print(f"Solution found after {self.iter} iterations")
        return self.solution

    def brute_force_possible_values(self):
        possible_lengths = map(lambda s: len(s), filter(lambda els: els, self.possible_values.values()))
        max_iterations = tuple(accumulate(possible_lengths, func=int.__mul__, initial=1))[-1]
        print(f"Max Brute Force Iterations: {max_iterations}")

        possible_idx_values = filter(lambda els: els[1], self.possible_values.items())
        possibles = tuple(map(lambda items: tuple(map(lambda v: (items[0], v) ,items[1])), possible_idx_values))

        iter = 0
        next_iter_report = max_iterations // 1000
        current_iter_report = 0

        bar = Bar("Brute Force", max = 1000)

        start_time = time.time()
        for possible_row in product(*possibles):
            if iter  == current_iter_report: 
                bar.next()
                current_iter_report += next_iter_report
            iter += 1
            solution = self.solution.copy()
            for idx, val in possible_row:
                solution.set(idx, val)
            
            if solution.is_puzzle_solved():
                break
        
        time_elapsed = time.time() - start_time
        if not solution.is_puzzle_solved():
            print(f"No solution found after {iter} iterations and {time_elapsed} seconds")

        else:
            print(f"Solution Found after {iter} iterations and {time_elapsed} seconds")
            solution.print()
            return solution

    def solve(self):
        print("Solving Sudoku puzzle")
        self.puzzle_data.print()

        match self.puzzle_data.check():
            case DataState.ERROR:
                raise ValueError("Input puzzle has an error")
            case DataState.COMPLETE:
                print("Puzzle is already complete")
                return self.puzzle_data
       
        solution = self.solve_by_passes()

        if not solution:
            # Brute force remaining
            print("Attempting brute force solver")

            def iter_puzzle(puzzle):
                pass
            
            idx, shortest_vals = self._get_shortest_possibles()

            for val in shortest_vals:
                solver = SudokuSolver(self.solution)
                solver.update_solution(idx, val)
                try:
                    solution = solver.solve()
                except ValueError:
                    continue
                else:
                    pass
                
            # solution = self.brute_force_possible_values()
            
        return solution


class BruteForceSolver(SudokuSolver):

    def solve(self):
        print("Solving by Brute Force")
        return self.solve_by_brute_force()

    def solve_by_brute_force(self):
        
        # lets try brute force

        # Can we solve by super rows first?  3 subsquares in a row?
        counter = [ 0 ] * 3
        for super_row_3 in self.iter_valid_super_row(2):
            counter[0] += 1
            for super_row_2 in self.iter_valid_super_row(1):
                counter[1] +=1
                for super_row_1 in self.iter_valid_super_row(0):
                    counter[2] += 1
                    solution = SudokuData(super_row_1.data + super_row_2.data + super_row_3.data)
                    self.iter += 1
                    if solution.is_puzzle_solved():
                        return solution
        
        return None

    def iter_valid_super_row(self, super_row):
        if super_row < 0 or super_row >= 3:
            raise ValueError(f"Super Row index out bounds {super_row}")
        start = 3 * super_row
        iter_count = 0

        initials = []
        for i in range(3):
            row_initials = []

            for idx, el in enumerate(self._puzzle_data.row(start + i)):
                if el is not None:
                    row_initials.append((idx, el))

            initials.append(row_initials)


        for row1 in self.permute_allowed_rows(initials[0]):
            for row2 in self.permute_allowed_rows(initials[1], previous_row=row1):
                for row3 in self.permute_allowed_rows(initials[2]):
                    superrow = SudokoSuperRow(row1 + row2 + row3)
                    iter_count += 1
                    if superrow.is_valid(): 
                        yield superrow

    def check_stub(self, data):
        # 2 row stub
        for i in range(9):
            if data[i] == data [i + 9]:
                return False
        
        for i in range(3):
            if len(set(data[3*i : 3*(i+1)] + data[9+3*i : 12 + 3*i]))!=6:
                return False
        
        return True

    def permute_allowed_rows(self, initials, previous_row=None):
        previous_row = previous_row or []
        initial_positions, initial_values = list(zip(*initials))
        numbers_to_permute = SudokuData.ALL_NUMBERS.difference(set(initial_values))

        for permutation in permutations(numbers_to_permute):
            row = list(permutation)
            [row.insert(idx, val) for idx, val in initials]
            
            if previous_row:
                if not self.check_stub(previous_row + row): 
                    continue
            yield row

    def brute_force_possible_values(self):
        max_iterations = list(accumulate(map(lambda s: len(s), self.possible_values.values()), func=int.__mul__, initial=1))[-1]
        print(f"Max Brute Force Iterations: {max_iterations}")

        
        possibles = tuple(map(lambda items: tuple(zip(*items)), self.possible_values.items()))

        iter = 0
        for possible_row in product(*possibles):
            iter += 1
            solution = self.solution.copy()
            for idx, val in possible_row:
                solution.set(idx, val)
            
            if solution.is_puzzle_solved():
                break
        
        if not solution.is_puzzle_solved():
            print(f"No solution found after {iter} iterations")
        
        else:
            print(f"Solution Found after {iter} iterations")
            solution.print()
            return solution
