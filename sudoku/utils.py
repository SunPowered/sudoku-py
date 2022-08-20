from sudoku.data import SudokuData

def write_to_file(file, data):
    file.write(",".join(data))
    file.close()

def read_from_file(file):
    
    data = file.read().strip().split(',')
    file.close()

    def validate(el):
        try:
            return int(el)
        except (TypeError, ValueError):
            return None

    return SudokuData(list(map(validate, data)))