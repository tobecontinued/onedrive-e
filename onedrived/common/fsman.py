import threading


class FileSystemMonitor(threading.Thread):
    def __init__(self):
        super().__init__(name='fsmon', daemon=True)

    def run(self):
        pass
