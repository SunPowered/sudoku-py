from . import tk, ttk, NEWS
from sudoku.data import SudokuData

class SudokuButton(ttk.Button):
    def __init__(self, idx, *args, **kwargs):
        self.idx = idx
        kwargs['style'] = "Sudoku.TButton"
        ttk.Button.__init__(self, *args, **kwargs)

class SudokuSubSquareWidget(ttk.Frame):

    def __init__(self, root, sub_square, data, update_callback=None, remove_callback=None):
        tk.Frame.__init__(self, root, border=2, highlightthickness=1, highlightbackground="gray")
        self.sub_square = sub_square
        self.update_callback = update_callback
        self.remove_callback = remove_callback
        self.setup_widgets(data)

    def setup_widgets(self, data):
        data_indices = SudokuData.subsquare_indices(self.sub_square)

        def update_index(idx):
            return lambda: self.update_callback(idx) if self.update_callback else None

        def remove_index(idx):
            return lambda _: self.remove_callback(idx) if self.remove_callback else None

        
        for i in range(3):
            self.rowconfigure(i, weight=1)
            self.columnconfigure(i, weight=1)

            for j in range(3):
                data_idx = next(data_indices)
                btn = SudokuButton(
                    data_idx,
                    self, 
                    textvariable=data[data_idx],
                    command=update_index(data_idx)
                )
                btn.grid(row=i, column=j, sticky=NEWS)
                btn.bind("<Button-3>", remove_index(data_idx))
    