from typing import Union
import base64 as b64
import numpy as np
import simplejpeg


class MJPEGEncoder:
    """MJPEG encoder based on simplejpeg library.

    Args:
        quality: JPEG quantization factor
        colorspace: source colorspace; one of
                        'RGB', 'BGR', 'RGBX', 'BGRX', 'XBGR', 'XRGB',
                        'GRAY', 'RGBA', 'BGRA', 'ABGR', 'ARGB', 'CMYK'.
        colorsubsampling: subsampling factor for color channels; one of
                                '444', '422', '420', '440', '411', 'Gray'.
        fastdct: If True, use fastest DCT method;
                        speeds up encoding by 4-5% for a minor loss in quality

    """

    def __init__(
        self,
        quality: int = 85,
        colorspace: str = "bgr",
        colorsubsampling: str = "444",
        fastdct: bool = True,
        *args,
        **kwargs,
    ):
        self.quality = quality
        self.colorspace = colorspace
        self.colorsubsampling = colorsubsampling
        self.fastdct = fastdct

    def setParams(
        self,
        quality: int = 85,
        colorspace: str = "rgb",
        colorsubsampling: str = "444",
        fastdct: bool = True,
    ):
        """Updates the encoder params.

        Args:
            image: uncompressed image as uint8 array
            quality: JPEG quantization factor
            colorspace: source colorspace; one of
                            'RGB', 'BGR', 'RGBX', 'BGRX', 'XBGR', 'XRGB',
                            'GRAY', 'RGBA', 'BGRA', 'ABGR', 'ARGB', 'CMYK'.
            colorsubsampling: subsampling factor for color channels; one of
                                    '444', '422', '420', '440', '411', 'Gray'.
            fastdct: If True, use fastest DCT method;
                            speeds up encoding by 4-5% for a minor loss in quality

        """
        self.quality = quality
        self.colorspace = colorspace
        self.colorsubsampling = colorsubsampling
        self.fastdct = fastdct

    def encode(
        self,
        frame: np.ndarray = None,
        base64: bool = True,
        quality: int = None,
        colorspace: str = None,
        colorsubsampling: str = None,
        fastdct: bool = False,
    ) -> Union[bytes, str]:
        """Encodes an array of images in JPEG format and, if possible, convert it to base64.

        Args:
            frame: image array
            base64: encode image in base64 format?
            quality: JPEG quantization factor
            colorspace: source colorspace; one of
                            'RGB', 'BGR', 'RGBX', 'BGRX', 'XBGR', 'XRGB',
                            'GRAY', 'RGBA', 'BGRA', 'ABGR', 'ARGB', 'CMYK'.
            colorsubsampling: subsampling factor for color channels; one of
                                    '444', '422', '420', '440', '411', 'Gray'.
            fastdct: If True, use fastest DCT method;
                            speeds up encoding by 4-5% for a minor loss in quality
        Returns:
            jpeg: encoded image as JPEG (JFIF) data or base64 string

        """
        if frame is not None and isinstance(frame, np.ndarray):
            colorspace = self.colorspace if colorspace is None else colorspace

            if frame.ndim == 2:
                frame = frame[:, :, np.newaxis]
                colorspace = "GRAY"

            quality = self.quality if quality is None else quality
            colorsubsampling = (
                self.colorsubsampling if colorsubsampling is None else colorsubsampling
            )
            fastdct = self.fastdct if fastdct is None else fastdct
            jpeg = simplejpeg.encode_jpeg(
                frame,
                quality,
                colorspace,
                colorsubsampling,
                fastdct,
            )

            if base64:
                jpeg = b64.b64encode(jpeg).decode()

            return jpeg

    def multipleEncode(self, frames: dict):
        """Encodes a dict with numpy arrays (frames)."""
        if isinstance(frames, dict):
            return {k: self.encode(v) for k, v in frames.items()}
        else:
            return self.encode(frames)
