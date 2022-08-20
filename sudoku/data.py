from mimetypes import init
from tkinter import ALL
import numpy as np
import enum

ALL_NUMBERS = set(range(1, 10))

class DataState(enum.Enum):
    ERROR = 0
    VALID = 1
    COMPLETE = 2


class SudokuData:
    ALL_NUMBERS = set(range(1,10))

    def __init__(self, initial_data=None):
        if initial_data is not None:
            if len(initial_data) != 81:
                raise ValueError("Wrong data length, expecting 81")

        if isinstance(initial_data, SudokuData):
            initial_data = initial_data.data

        self._data = initial_data or (None, ) * 81
        
        self._initial_idxs = set(map(lambda els: els[0],
            filter(lambda els: els[1] is not None, enumerate(initial_data) )
        ))
        self._puzzle_idxs = set(range(81)).difference(self._initial_idxs)  # The initial indices of the puzzle, these are fixed and cannot be set

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __contains__(self, idx):
        return self._data[idx] is not None

    def __eq__(self, other):
        return self._data == other.data

    @property
    def data(self):
        return self._data

    @property
    def initial_idxs(self):
        return self._initial_idxs

    @property
    def puzzle_idxs(self):
        return self._puzzle_idxs

    def copy(self):
        return SudokuData(self._data.copy())

    def get(self, idx):
        if idx < 0 or idx > 81:
            raise ValueError("index out of bounds")
        return self._data[idx]

    def set(self, idx, value):
        if idx < 0 or idx > 81:
            raise ValueError("index out of bounds")

        if idx in self._initial_idxs:
            raise IndexError("Cannot write to a puzzle index")
        
        try:
            self._data[idx] = int(value)
        except (ValueError, TypeError):
            raise ValueError("Unable to convert value to integer")
    
    def as_pretty_str(self):

        border_row = "".join(["+" + "-" * 5]*3 + ["+\n"]) 
        data_row = "".join(["|{} {} {}"] * 3 + ['|\n'])
        
        res = ""
        row_idx = 0

        def val_or_empty(val):
            if val is None:
                return " "
            else: return str(val)

        for _ in range(3):
            res += border_row
            for subsquare in range(3):
                data_values = tuple(map(lambda val: val_or_empty(val), self.row(row_idx)))
                row_idx += 1
                res += data_row.format(*data_values)

        res += border_row
        return res

    def print(self):
        print(self.as_pretty_str())

    @classmethod
    def row_from_idx(cls, idx):
        return idx // 9

    @classmethod
    def column_from_idx(cls, idx):
        return idx % 9

    @classmethod
    def subsquare_from_idx(cls, idx):
        return 3 * (cls.row_from_idx(idx) // 3) + cls.column_from_idx(idx) // 3

    @classmethod
    def row_indices(cls, row, ignore=None):
        if row < 0 or row >= 9:
            raise ValueError(f"Row index out of bounds {row}")

        start = row * 9
        for i in range(9):
            idx = start + i
            if ignore and idx in ignore: continue
            yield idx
    
    def row(self, row, ignore_initials=False):
        initials = self._initial_idxs if ignore_initials else None
        for idx in SudokuData.row_indices(row, ignore = initials):
            yield self._data[idx]
    
    @classmethod
    def column_indices(cls, column, ignore=None):
        if column < 0 or column >= 9: 
            raise ValueError("Column index out of bounds")
        offset = column
        for i in range(9):
            if ignore and i in ignore: continue
            yield 9 * i + offset

    def column(self, column, ignore_initials=False):
        initials = self._initial_idxs if ignore_initials else None
        for idx in SudokuData.column_indices(column, ignore=initials):
            yield self._data[idx]

    @classmethod
    def subsquare_indices(cls, sub_square, ignore=None):
        if sub_square < 0 or sub_square > 9:
            raise ValueError("Sub-square index is out of bounds")
            
        start = 27 * (sub_square // 3 ) + 3 * (sub_square % 3 )

        for _ in range(3):
            for j in range(3):
                idx = start + j
                if ignore and idx in ignore: continue
                yield idx
            start += 9
          
    def sub_square(self, sub_square, ignore_initials=False):
        initials = self._initial_idxs if ignore_initials else None
        for idx in SudokuData.subsquare_indices(sub_square, ignore=initials):
            yield self._data[idx]
    
    @classmethod
    def is_row_in_subsquare(row_idx, subsquare_idx):
        return row_idx // 3 == subsquare_idx // 3

    @classmethod
    def is_column_in_subsquare(column_idx, subsquare_idx):
        return column_idx // 3 == subsquare_idx % 3

    @classmethod
    def superrow_indices(cls, super_row, ignore=None):
        if 0 > super_row or super_row >= 3:
            raise ValueError("Super row index out of bounds")

        start = 27 * super_row
        for i in range(27):
            idx = start + i
            if ignore and idx in ignore: continue
            yield idx
    
    def super_row(self, super_row, ignore_initials=False):
        initials = self._initial_idxs if ignore_initials else None
        for idx in SudokuData.superrow_indices(super_row, ignore=initials):
            yield self._data[idx]

    def are_rows_solved(self):
        for row in range(9):
            if set(self.row(row)) != self.ALL_NUMBERS:
                return False
        return True
    
    def are_columns_solved(self):
        for column in range(9):
            if set(self.column(column)) != self.ALL_NUMBERS:
                return False
        return True

    def are_subsquares_solved(self):
        for subsquare in range(9):
            if set(self.sub_square(subsquare)) != self.ALL_NUMBERS:
                return False
        return True

    def is_puzzle_solved(self):
        if not self.are_rows_solved(): return False
        if not self.are_columns_solved(): return False
        if not self.are_subsquares_solved(): return False
        return True

    def iter_row_from_idx(self, idx):
        return self.row(self.row_from_idx(idx))

    def iter_column_from_idx(self, idx):
        return self.column(self.column_from_idx(idx))
    
    def iter_subsquare_from_idx(self, idx):
        return self.sub_square(self.subsquare_from_idx(idx))

    def iter_valid_row_from_idx(self, idx):
        return self.row(self.row_from_idx(idx), ignore_initials=True)

    def iter_valid_column_from_idx(self, idx):
        return self.column(self.column_from_idx(idx), ignore_initials=True)
    
    def iter_valid_subsquare_from_idx(self, idx):
        return self.sub_square(self.subsquare_from_idx(idx), ignore_initials=True)

    def check(self):

        if not self.check_for_errors(): return DataState.ERROR
        if not self.check_complete(): return DataState.VALID
        
        return DataState.COMPLETE


    def check_for_errors(self):

        for i in range(9):
            row = tuple(self.row(i))
            if len(row) != len(set(row)): return False

            column = tuple(self.column(i))
            if len(column) != len(set(column)): return False

            subsquare = tuple(self.sub_square(i))
            if len(subsquare)  != len(set(subsquare)): return False
        
        return True

    def check_complete(self):

        for i in range(9):
            if set(self.row(i)) != ALL_NUMBERS: return False
            if set(self.column(i)) != ALL_NUMBERS: return False
            if set(self.sub_square(i)) != ALL_NUMBERS: return False

        return True

class SudokoSuperRow:
    ALL_NUMBERS = set(range(1, 10))

    def __init__(self, data):
        if len(data) != 27:
            raise ValueError("Expecting data length of 27")

        self._data = data

    @property
    def data(self):
        return self._data

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        return str(self._data)

    def row(self, row):
        start = 9 * row
        for idx in range(9):
            yield self.data[start + idx]
    
    def subsquare(self, subsquare):
        start = 3 * subsquare
        for _ in range(3):
            for idx in range(3):
                yield self._data[start + idx]
            start += 9
    
    def column(self, column):
        for idx in range(9):
            yield self._data[9 * idx + column]
        
    def is_valid(self):
        # if not self.are_valid_rows(): return False
        # if not self.are_valid_columns(): return False
        if not self.are_valid_subsquares(): return False

        return True

    def are_valid_rows(self):
        for row in range(3):
            if set(self.row(row)) != self.ALL_NUMBERS: return False
        return True

    def are_valid_subsquares(self):
        for subsquare in range(3):
            if set(self.subsquare(subsquare)) != self.ALL_NUMBERS: return False
        return True

    def are_valid_columns(self):
        for column in range(9):
            if len(set(self.column(column))) != 3: return False
        return True

    def dict(self):
        return dict(((idx, el) for idx, el in enumerate(self._data) if el is not None))
        

class SudokuDataNP:
    def __init__(self, puzzle_data):
        self.data = np.array(puzzle_data).reshape((9,9))

    def row(self, row):
        return self.data[row, :]

    def column(self, column):
        return self.data[:, column]

    def subsquare(self, subsquare):
        row = subsquare // 3
        column = subsquare % 3

        return self.data[3 * row : 3 * (row + 1), 3 * column : 3 * (column + 1)].reshape(9)

    def is_row_solved(self, row):
        return set(self.row(row)) == ALL_NUMBERS

    def is_column_solved(self, column):
        return set(self.column(column)) == ALL_NUMBERS

    def is_subsquare_solved(self, subsquare):
        return set(self.subsquare(subsquare)) == ALL_NUMBERS

    def is_puzzle_solved(self):
        for i in range(9):
            if not self.is_row_solved(i): return False
            if not self.is_column_solved(i): return False
            if not self.is_subsquare_solved(i): return False
        return True

    