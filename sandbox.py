from __future__ import print_function
import sys
import threading
import traceback

class QueuedFunction(object):
    def __init__(self, func, args, kwargs):
        self.func, self.args, self.kwargs = func, args, kwargs
        frames = filter(lambda frame: frame[0] == '<string>', traceback.extract_stack())
        if len(frames):
            self.lineno = frames[0][1]
        self.called = False
        self.retval = None
        self.event = threading.Event()

    def call(self):
        self.retval = self.func(*self.args, **self.kwargs)
        self.called = True
        self.event.set()

    def interrupt(self):
        self.event.set()

    def wait(self):
        self.event.wait()
        assert self.called
        return self.retval

class QueuedCallback(QueuedFunction):
    def call(self):
        self.func(self.complete, *self.args, **self.kwargs)
    def complete(self, retval):
        self.retval = retval
        self.called = True
        self.event.set()

def create_function_wrapper(cls):
    def outer(func, queue):
        def wrapper(*args, **kwargs):
            q = QueuedFunction(func, args, kwargs)
            queue.put(q)
            return q.wait()
        return wrapper
    return outer

wrap_function = create_function_wrapper(QueuedFunction)
wrap_callback_function = create_function_wrapper(QueuedCallback)

class SandboxThread(threading.Thread):
    daemon = True
    def __init__(self, code, vars):
        super(SandboxThread, self).__init__()
        self.code, self.vars = code, vars
        self.complete = False
        self.error = None
    def run(self):
        try:
            exec(self.code, {}, self.vars)
        except Exception as e:
            if hasattr(e, 'lineno'):
                line = e.lineno
            else:
                line = traceback.extract_tb(sys.exc_info()[2])[-1][1]
            self.set_error(e, line=line)
        finally:
            self.complete = True
    def set_error(self, err, line=None):
        if line is None:
            line = 'unknown'
        self.error = err
        self.error_line = line
        self.complete = True
