
from . import tk, ttk, NEWS
from .sub_square import SudokuSubSquareWidget

class SudokuBoardWidget(ttk.Frame):

    def __init__(self, root, new_value, size=600 ):
        ttk.Frame.__init__(self, root, width=size, height=size)
        self.content_frame = ttk.Frame(root)
        self.data = [ tk.StringVar(self) for _ in range(81)]    
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.input_value = new_value
        ttk.Style(self).configure("Sudoku.TButton", font = ("Helvetica", 26, "bold"))
        self.setup_widgets()
        # self.set_aspect_ratio()

    def setup_widgets(self):

        for i in range(3):
            self.content_frame.rowconfigure(i, weight=1)
            self.content_frame.columnconfigure(i, weight=1)

            for j in range(3):
                idx = 3 * i + j
                sub_square_widget = SudokuSubSquareWidget(
                    self.content_frame, 
                    idx, 
                    self.data, 
                    update_callback=self.update_data,
                    remove_callback=self.remove_data)
                sub_square_widget.grid(row=i, column=j, sticky=NEWS)

        # self.bind("<Button-1>", self.update_data)
        # self.bind('<Button-3>', self.remove_data)

    def clear(self):
        [ el.set("") for el in self.data]

    def set_aspect_ratio(self):
        def enforce_aspect_ratio(event):
            desired_width = desired_height = min(event.width, event.height)
            self.content_frame.place(in_=self, x=0, y=0, width=desired_width, height=desired_height)
        self.bind("<Configure>", enforce_aspect_ratio)

    def update_data(self, idx):
        self.data[idx].set(self.input_value.get())

    def remove_data(self, idx):
        print("Remove")
        self.data[idx].set("")

    def load(self, sudoku_data):
        for idx, item in enumerate(sudoku_data):
            if item is not None:
                self.data[idx].set(item) 
            
    def iter_data(self):
        for el in self.data:
            yield el.get()

            
        