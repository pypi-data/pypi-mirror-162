from socketio import AsyncClient
import threading
from typing import Optional


VIDEO_TO_SERVER = "v2s"
MACHINE_TO_SERVER = "m2s"
SERVER_TO_MACHINE = "s2m"
STOP_MACHINE = "stop"


class CustomAsyncSocketIO(AsyncClient):
    """
    :param identifier:
    """

    def __init__(
        self,
        identifier: str = "default",
        serverAddress: str = "",
        manager: str = None,
        streamingRoute: str = None,
        *args,
        **kwargs
    ):
        self.serverAddress = serverAddress
        self.io = AsyncClient(*args, **kwargs)
        self.thread = threading.Thread(target=self.run, name="SocketIO-Thread")

        self.running = threading.Event()
        self.connectionEvent = threading.Event()
        self.writeEvent = threading.Event()

    def start(self):
        self.running.set()

    def write(self, data, route: Optional[str] = None):
        self.io.emit(route, data)

    async def run(self):
        while self.running.is_set():
            pass
