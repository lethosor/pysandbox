import threading

class SandboxThread(threading.Thread):
    def __init__(self, code):
        super(SandboxThread, self).__init__()
        self.code = code
    def run():
        pass
