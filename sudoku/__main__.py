from tkinter import Tk
from sudoku.ui.app import Application

r = Tk()
app = Application(r)
app.pack()
r.title("Sudoku Solver")
r.mainloop()