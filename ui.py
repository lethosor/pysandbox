from __future__ import print_function

import sys
import threading
import time
import traceback
if sys.version.startswith('2'):
    import Queue as queue
else:
    import queue

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
        self.field.bind('<Key>', lambda e: 'break')
        self.input_active = False
        self.field.tag_config('error', foreground='red')
        self.input_label = tk.Label(self)
        self.input_label.grid(row=3, column=1)
        self.input_field = tk.Text(self, height=1, state='disabled')
        self.input_field.grid(row=4, column=1, sticky='ew')
        self.input_field.bind('<Return>', self.input_submit)
        self.func_queue = queue.Queue()

    def run(self, code):
        wrap = lambda func: sandbox.wrap_function(func, self.func_queue)
        cwrap = lambda func: sandbox.wrap_callback_function(func, self.func_queue)
        vars = {}
        vars['print'] = wrap(self.print_)
        vars['clear'] = wrap(self.clear)
        vars['sleep'] = time.sleep
        vars['input'] = cwrap(self.input)
        self.code_thread = sandbox.SandboxThread(code, vars)
        self.code_thread.start()
        self.after(10, self.code_process)

    def code_process(self):
        i = 0
        while True:
            func = None
            try:
                func = self.func_queue.get(timeout=0.01)
                func.call()
                i += 1
                if i > 10:
                    break
            except queue.Empty:
                break
            except Exception as e:
                self.code_thread.set_error(e, func.lineno if func else None)
                if func is not None:
                    func.interrupt()
                break
        if not self.code_thread.complete:
            self.after(1, self.code_process)
        else:
            if self.code_thread.error is not None:
                self.print_error('Error: line %s: %s',
                    self.code_thread.error_line, self.code_thread.error)

    def raise_error(self, *args, **kwargs):
        self.code_thread.set_error(*args, **kwargs)

    def clear(self):
        self.field.delete(1.0, 'end')
        if self.input_active:
            self.print_(self.input_prompt, newline=False)

    def print_(self, fmt, *args, **kwargs):
        out = str(fmt) % args
        self.field.insert('end', out, kwargs.get('tags', ()))
        if kwargs.get('newline', True):
            self.field.insert('end', '\n')
        self.field.see('end')

    def print_error(self, fmt, *args):
        self.print_(fmt, *args, tags=('error',))

    def input(self, func, prompt=''):
        self.input_active = True
        self.input_func = func
        self.input_callback = func.callback
        self.input_label.config(text=prompt)
        self.input_field.config(state='normal')
        self.input_field.focus()

    def input_submit(self, event):
        if not self.input_active:
            return 'break'
        self.input_callback(self.input_field.get(1.0, 'end').rstrip('\r\n'))
        self.input_active = False
        self.input_callback = None
        self.input_field.delete(1.0, 'end')
        self.input_label.config(text='')
        self.input_field.config(state='disabled')

def init():
    global root
    root = tk.Tk()
    root.withdraw()
    Editor(root)

def mainloop():
    tk.mainloop()
