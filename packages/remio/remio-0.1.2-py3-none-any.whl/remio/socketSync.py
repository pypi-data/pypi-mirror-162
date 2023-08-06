from socketio import Client


class CustomSocketIO(Client):
    """A custom socketio client."""

    def __init__(self, address: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.address = address

    def stop(self):
        try:
            self.disconnect()
        except Exception as e:
            print("Socket:: ", e)

    def start(self):
        if self.address is not None:
            try:
                self.connect(self.address, wait=True)
            except Exception as e:
                print("socket:: ", e)

    def emit(self, *args, **kwargs):
        try:
            super().emit(*args, **kwargs)
        except Exception as e:
            print("socket:: ", e)

    def on(self, *args, **kwargs):
        event = args[0]
        handler = args[1]
        if event == "connection":
            super().on("connect", handler)
            super().on("disconnect", handler)
        else:
            super().on(*args, **kwargs)

    def isConnected(self):
        return not self.connected

    def toogle(self, value: bool):
        if value:
            self.start()
        else:
            self.stop()
