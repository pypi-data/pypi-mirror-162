import threading
import multiprocessing


class Worker:
    def __init__(self, mode="thread"):
        self.mode = mode
        self._thread = None
        self._running = None
        self._writeEvent = None

    def __configure(self):
        if self.mode == "thread":
            self._thread = threading.Thread(target=self.__execute)
            self._running = threading.Event()
            self._writeEvent = threading.Event()
        elif self.mode == "process":
            self._thread = multiprocessing.Process(target=self.__execute)
            self._running = multiprocessing.Event()

    def isProcess(self):
        return self.mode == "process"

    def isThread(self):
        return self.mode == "thread"
