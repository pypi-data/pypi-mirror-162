"""HTTP server functionalities."""
import time
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

from remio.network import get_ipv4


class Handler(BaseHTTPRequestHandler):
    """Custom HTTP handler for streaming video on MJPEG format."""

    def do_GET(self):
        if self.path == self.server.endpoint:
            self.send_response(200)
            self.send_header(
                "Content-type", "multipart/x-mixed-replace; boundary=--jpgboundary"
            )
            self.end_headers()

            if self.server.camera is not None:
                fps = self.server.fps
                while True:
                    try:
                        jpeg = self.server.camera.jpeg()
                        self.wfile.write(bytes("--jpgboundary\n", "utf8"))
                        self.send_header("Content-type", "image/jpeg")
                        self.send_header("Content-length", len(jpeg))
                        self.end_headers()

                        self.wfile.write(jpeg)
                        time.sleep(1 / fps)

                    except Exception as e:
                        print("--> MJPEGHandler error: ", e)
                        break


class CustomHTTPServer(HTTPServer):
    """HTTP server with custom params."""

    def __init__(
        self, camera=None, fps: int = 12, endpoint: str = "/", *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.camera = camera
        self.fps = fps
        self.endpoint = endpoint


class ThreadedHTTPServer(ThreadingMixIn, CustomHTTPServer):
    """Handle requests in a separate thread."""


class MJPEGServer:
    """A MJPEG server class based on HTTPServer and ThreadingMixIn.
    Args:
        camera: A camera instance.
        fps: server fps to stream.
        ip: ip address of the server.
        port: port value of the server.
        endpoint: a server router for example `/video` or '/mjpeg/video'.
    """

    def __init__(
        self,
        camera=None,
        fps: int = 10,
        ip: str = "0.0.0.0",
        port: int = 8080,
        display_url: bool = True,
        start_camera: bool = False,
        endpoint: str = "/",
        *args,
        **kwargs,
    ):
        self.camera = camera
        self.ip = ip
        self.port = port
        self.fps = fps
        self.endpoint = endpoint
        self.server = ThreadedHTTPServer(
            camera=self.camera,
            fps=self.fps,
            server_address=(ip, port),
            endpoint=endpoint,
            RequestHandlerClass=Handler,
        )
        self.display_url = display_url
        self.start_camera = start_camera
        self.thread = Thread(target=self.run)

    def start(self):
        """Starts listen loop on a thread."""
        self.thread.start()

    def run(self, display_url: bool = None, start_camera: bool = None):
        """Executes the streaming loop.
        Args:
            display_url: show a url with the server address?
            start_camera: call start method of the camera instance?
        """
        if display_url is None:
            display_url = self.display_url

        if start_camera is None:
            start_camera = self.start_camera
        try:
            if display_url:
                print(
                    f">> localhost :: MJPEG server running on http://{self.ip}:{self.port}{self.endpoint}"
                )
                if '0.0.0.0' in self.ip:
                    for ip in get_ipv4():
                        print(f">> local network :: MJPEG server running on http://{ip}:{self.port}{self.endpoint}")

            if start_camera:
                self.camera.start()

            self.server.serve_forever()
        except Exception as e:
            print(f"--> MJPEG server: {e}")
            self.stop()

    def stop(self, stop_camera: bool = True):
        """Stops the mjpeg server.
        Args:
            stop_camera: call the stop method of the camera?
        """
        self.server.shutdown()
        if self.camera is not None and stop_camera:
            self.camera.stop()
