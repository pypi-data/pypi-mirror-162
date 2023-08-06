"""Stream Utils/Classes."""
from typing import Union, Callable
from threading import Thread, Event, Lock
import time
import numpy as np
from socketio import Client
from .mjpeg import MJPEGEncoder


class SocketStreamer:
    """SocketIO video mjpeg streamer.

    Args:
        socket: a socketIO-client instance.
        reader: a read frame function.
        endpoint: route to stream the video.
        fps: fps streaming speed.

    """

    def __init__(
        self,
        socket: Union[Client, None] = None,
        reader: Callable = None,
        endpoint: str = "",
        fps: int = 10,
        enabled: bool = True,
        *args,
        **kwargs,
    ):
        self.socket = socket
        self.encoder = MJPEGEncoder(*args, **kwargs)
        self.lastFrame = None
        self.frame = None
        self.reader = reader
        self.fps = fps
        self.endpoint = endpoint
        self.enabled = enabled
        self.thread = Thread(target=self.run, name="stream-thread", daemon=True)
        self.running = Event()
        self.pauseEvent = Event()
        self.streamLock = Lock()
        self.configureSocket()
        self.resume()

    def resume(self):
        """Resumes the stream loop."""
        self.pauseEvent.set()

    def pause(self):
        """Pauses the stream loop."""
        self.pauseEvent.clear()

    def needAPause(self):
        """Controls the pause or resume of the stream loop."""
        self.pauseEvent.wait()

    def setPause(self, value: bool = True):
        """Updates the pause/resume state."""
        if value:
            self.pause()
        else:
            self.resume()

    def configureSocket(self):
        """Configures autostop/autoresume stream loop for save cpu resources."""
        if self.hasSocket():
            self.socket.on("connect", self.resume)
            self.socket.on("disconnect", self.pause)

    def setEnabled(self, value: bool = True):
        """Updates enabled value."""
        self.enabled = value

    def setReader(self, reader=None):
        """Updates the reader function."""
        self.reader = reader

    def hasReader(self):
        """ "Checks if there is an available reader function."""
        return self.reader is not None

    def hasSocket(self):
        """Checks if a socket object is available."""
        return self.socket is not None

    def start(self):
        """Starts the stream loop."""
        if self.enabled:
            self.running.set()
            self.thread.start()

    def stop(self):
        """Stops the stream loop."""
        self.resume()
        if self.running.is_set():
            self.running.clear()
            self.thread.join()

    def readAndStream(self, *args, **kwargs):
        """Reads and streams available frames."""
        if self.hasSocket() and self.hasReader():
            frames = self.reader(*args, **kwargs)
            self.stream(frames)

    def stream(self, frames: np.ndarray):
        """Streams a frame directly to the endpoint.

        Args:
            frame: image array
        """
        if frames is not None:
            if self.socket.connected:
                if self.pauseEvent.is_set():
                    if frames is not str:
                        frames = self.encoder.multipleEncode(frames)
                    self.streamLock.acquire()
                    try:
                        self.socket.emit(self.endpoint, frames)
                    except Exception as e:
                        print(f"Streamer:: {e}")
                    self.streamLock.release()

    def run(self):
        """Executes the stream loop."""
        while self.running.is_set():
            if self.hasSocket():
                self.readAndStream()
            time.sleep(1 / self.fps)
            self.needAPause()
