from typing import Union, Callable
from threading import Thread, Event


class SetInterval:
    """A timer that executes a recurring task each certain time, using thread events for it."""

    def __init__(
        self, interval: Union[int, float], callback: Callable = None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.interval = interval
        self.timeout = interval
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.running = Event()
        self.pauseEvent = Event()
        self.thread = Thread(target=self.run, daemon=True)
        self.start()
        self.pause()
        self._quit = False

    def start(self):
        """Starts timer execution."""
        self.thread.start()

    def run(self):
        """Excutes the recurrent task."""
        while True:
            self.pauseEvent.wait()
            self.running.wait(self.timeout)
            self.callback(*self.args, **self.kwargs)
            if self._quit:
                break

    def resume(self, now: bool = True):
        """Resumes the task execution."""
        self.pauseEvent.set()
        if now:
            self.running.set()

    def pause(self, reset: bool = False):
        """Pauses the task execution."""
        self.pauseEvent.clear()
        if reset:
            self.running.clear()

    def stop(self):
        """Stops the timer execution."""
        self.resume(now=True)
        self._quit = True
