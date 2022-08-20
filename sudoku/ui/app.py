import tkinter.filedialog as filedialog

from sudoku import utils

from .widgets import tk, ttk, NEWS
from .widgets.board import SudokuBoardWidget


class Application(ttk.Frame):

    def __init__(self, root):
        ttk.Frame.__init__(self, root)
        self.setup_widgets()


    def setup_widgets(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)
        self.input_value = tk.IntVar(self, 1, "Sudoku_Spinbox")
        self.setup_menu().grid(row=0, column=0, ipadx=5, pady=10, padx=10)
        
        self.board = SudokuBoardWidget(self, self.input_value)
        self.board.grid(row=0, column=1, ipadx=10, ipady=10, padx=10, pady=10, sticky=NEWS)
        self.board.set_aspect_ratio()


    def setup_menu(self):

        menu = ttk.Frame(self)
        ttk.Button(menu, text="Clear", command=self.onClearButton).pack()
        ttk.Spinbox(menu, from_=1, to=9, width=2, textvariable=self.input_value).pack(pady=10)
        ttk.Button(menu, text="Save to File", command=self.onSaveToFile).pack()
        ttk.Button(menu, text="Load from File", command=self.onLoadFromFile).pack()
        return menu

    def onClearButton(self):
        self.board.clear()

    def onLoadFromFile(self):
        file = filedialog.askopenfile(title="Select File to Load")
        if file: 
            self.board.load( utils.read_from_file(file) )

    def onSaveToFile(self):
        file = filedialog.asksaveasfile(title="Select File to Save")
        if file:
            utils.write_to_file(file, self.board.iter_data())