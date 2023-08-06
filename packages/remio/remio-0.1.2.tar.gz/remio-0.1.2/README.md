<div align="center"><h1> REMIO </h1></div>
<div align="center">

[Documentation][docs] &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; [License](#copyright)

[![Code Style][black-badge]][black]
[![Codecov branch][codecov]][codecov-repo]
[![PyPi version][pypi-badge]][pypi] 
</div>

# Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Development](#development)
5. [Simplejpeg API](#simplejpeg-api)
6. [Simple MJPEG Server](#simple-mjpeg-server)
7. [Multiple Cameras API](#multiple-cameras-api)
8. [Multiple Serial API](#multiple-serial-api)
9. [Examples](#examples)

## Introduction
REMIO is a library for managing concurrent socketio, cv2, and pyserial processes. Useful for making robots or devices with Arduinos and Raspberry Pi. It was born in the context of remote laboratories, hence its name, where I used and developed several prototypes where the code began to redound. That's where I extracted the modules from this library. The hardware architecture that I used to employ was the following:

<img src="./docs/assets/images/arch-1.png" style="margin: 1rem 0;">

So I programmed the following architecture
<img src="./docs/assets/images/modules-arch.png" style="margin: 2rem 0;">

## Features
- Multiple Camera API
- Multiple Serial API
- Event-driven programming API for Serial.
- Event-driven programming API for Cameras.
- MJPEG streamer with SocketIO

<!-- ----------------------------------------- -->

## Installation

First you need to create a virtualenv:
```
python3 -m venv venv
```
Then you should active it:
```
source venv/bin/activate
```
After choose an option for install remio, for example using pip:
```
# Pypi source
pip install remio

# Github source
pip install "git+https://github.com/Hikki12/remio"
```
Or if you prefer, clone the repository:
```
git clone https://github.com/Hikki12/remio

cd remio

pip install .
```

<!-- ----------------------------------------- -->

## Development
If you are a devolper, install the library as follows:
```
pip install -e .
```

<!-- ----------------------------------------- -->

## Multiple Cameras API
```python
import time
import cv2
from remio import Cameras


# Define devices
devices = {
    "webcam1": {
        "src": 0,
        "size": [400, 300],
        "fps": None,
        "reconnectDelay": 5,
        "backgroundIsEnabled": True,
        "emitterIsEnabled": False,
    },
    "webcam2": {
        "src": "http://192.168.100.70:3000/video/mjpeg",
        "size": [400, 300],
        "fps": None,
        "reconnectDelay": 5,
        "backgroundIsEnabled": True,
        "emitterIsEnabled": False,
    },
}

# Intialize Serial manager
camera = Cameras(devices=devices)

# Start device(s) connection on background
camera.startAll()

# Set a FPS speed to display image(s)
FPS = 20
T = 1 / FPS

while True:

    t0 = time.time()

    webcam1, webcam2 = camera.read(asDict=False)
    camera.clearAllFrames()  # to avoid repeated frames

    if webcam1 is not None:
        cv2.imshow("webcam1", webcam1)

    if webcam2 is not None:
        cv2.imshow("webcam2", webcam2)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    t1 = time.time()

    # Get a fixed delay value (t1 - t0) + delay = T
    delay = abs(T - (t1 - t0))
    time.sleep(delay)


# Close all Windows
cv2.destroyAllWindows()

# Stop all Running devices
camera.stopAll()

```
<!-- ----------------------------------------- -->

## Multiple Serial API
```python
"""Multiple serial devices management."""
import time
from remio import Serials


# Define devices
devices = {
    "arduino1": {
        "port": "/dev/cu.usbserial-1440",
        "baudrate": 9600,
        "emitterIsEnabled": True,  # Enable on/emit callbacks
        "reconnectDelay": 5,
    },
    "arduino2": {
        "port": "COM2",
        "baudrate": 9600,
        "emitterIsEnabled": True,
        "reconnectDelay": 5,
    },
}

# Intialize Serial manager
serial = Serials(devices=devices)

# Configure callbacks
serial.on("connection", lambda status: print(f"serial connected: {status}"))

# Start device(s) connection on background
serial.startAll()


while True:
    print("Doing some tasks...")
    time.sleep(1)

```
<!-- ----------------------------------------- -->

## Simplejpeg API
REMIO uses [simplejpeg](https://gitlab.com/jfolz/simplejpeg) library for encode camera images. You could used its API as follows:
```python
import time
from remio import Camera

# Initialize camera device
camera = Camera(src=0, fps=15, size=[800, 600], flipX=True)

while True:
    jpeg = camera.jpeg()
    time.sleep(1/10)
```
<!-- ----------------------------------------- -->
## A simple MJPEG Server
You could server your camera image with the MJPEG server, with a few lines:
```python
"""A simple MJPEG."""
from remio import Camera, MJPEGServer


encoderParams = {
    "quality": 90,
    "colorspace": "bgr",
    "colorsubsampling": "422",
    "fastdct": True,
}


# Initialize camera device
camera = Camera(src=0, fps=15, size=[800, 600], flipX=True, encoderParams=encoderParams)

# Configure MJPEG Server
server = MJPEGServer(
    camera=camera, ip="0.0.0.0", port=8080, endpoint="/video/mjpeg", fps=15
)

try:
    server.run(display_url=True, start_camera=True)
except KeyboardInterrupt:
    server.stop(stop_camera=True)
```
```bash
# The video must be accessible through the generated link
>> MJPEG server running on http://0.0.0.0:8080/video/mjpeg
```

<!-- ----------------------------------------- -->

## Examples
You could see more examples [here](https://github.com/Hikki12/remio/tree/master/examples).


Resources
---------
- [Changelog](./CHANGELOG.md)

## Copyright
**Copyright © hikki12 2022** <br/>
This library is released under the **[Apache 2.0 License][license]**.


<!--
External URLs
-->
[black]: https://github.com/psf/black
[pypi]: https://pypi.org/project/remio/


[docs]: https://hikki12.github.io/remio/
[license]: https://github.com/Hikki12/remio/blob/master/LICENSE
[codecov-repo]:https://codecov.io/gh/Hikki12/remio
<!--
Badges
-->
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge&logo=github
[pypi-badge]: https://img.shields.io/pypi/v/remio?style=for-the-badge&logo=pypi
[codecov]: https://img.shields.io/codecov/c/gh/Hikki12/remio?logo=codecov&style=for-the-badge&token=RQZV5HOILN