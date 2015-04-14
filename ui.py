from __future__ import print_function

import sys
import traceback

import sandbox
import tkwrapper as tk

class Editor(tk.Toplevel):
    editor_count = 0
    def __init__(self, *args):
        tk.Toplevel.__init__(self, *args)
        Editor.editor_count += 1
        self.protocol('WM_DELETE_WINDOW', self.dismiss)
        self.title("Editor")
        self.rowconfigure(2, weight=1)
        self.columnconfigure(1, weight=1)
        self.button_frame = tk.Frame(self)
        self.button_frame.grid(row=1, column=1, sticky='ew')
        self.buttons = {
            'new': tk.new_button(self.button_frame, 1, 1, 'New', lambda: Editor(root)),
            'run': tk.new_button(self.button_frame, 1, 4, 'Run', self.run),
        }
        self.field = tk.Text(self)
        self.field.grid(row=2, column=1, sticky='nsew')

    def dismiss(self):
        self.destroy()
        Editor.editor_count -= 1
        if Editor.editor_count <= 0:
            root.destroy()

    def run(self):
        Console(self).run(self.field.get('1.0', 'end'))

class Console(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.title('Console')
        self.rowconfigure(2, weight=1)
        self.columnconfigure(1, weight=1)
        self.button_frame = tk.Frame(self)
        self.button_frame.grid(row=1, column=1, sticky='ew')
        self.buttons = {
            'clear': tk.new_button(self.button_frame, 1, 1, 'Clear', self.clear),
            'close': tk.new_button(self.button_frame, 1, 2, 'Close', self.destroy),
        }
        self.field = tk.Text(self)
        self.field.grid(row=2, column=1, sticky='nsew')

    def run(self, code):
        vars = {}
        vars['print'] = self.print_
        vars['clear'] = self.clear
        try:
            exec(code, {}, vars)
        except Exception as e:
            _, _, tb = sys.exc_info()
            self.print_('Error on line %i: %s', traceback.extract_tb(tb)[-1][1], e)

    def clear(self):
        self.field.delete(1.0, 'end')

    def print_(self, fmt, *args):
        self.field.insert('end', str(fmt) % args)

def init():
    global root
    root = tk.Tk()
    root.withdraw()
    Editor(root)

def mainloop():
    tk.mainloop()
