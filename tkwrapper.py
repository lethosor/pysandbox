import sys
if sys.version.startswith('2'):
    from tkMessageBox import *
    from Tkinter import *
    import Tkinter as tk
else:
    from tkinter.messagebox import *
    from tkinter import *
    import tkinter as tk

def new_button(parent, row, column, text, callback):
    b = tk.Button(parent, text=text, command=callback)
    b.grid(row=row, column=column)
    return b

class Tk(tk.Tk):
    def __init__(self, *args):
        tk.Tk.__init__(self, *args)
        self.on_idle()
    def on_idle(self):
        # This prevents Tkinter's event loop from blocking completely,
        # allowing keyboard interrupts to work without further interaction
        self.after(100, self.on_idle)
