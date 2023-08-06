import time
from typing import Union, Tuple, Optional
import numpy as np

from scistag.imagestag import Image
from scistag.mediastag.video_source_camera import VideoSourceCamera


class VideoSourceCameraCv2(VideoSourceCamera):
    """
    A camera source wrapping OpenCV's camera access capabilities
    """

    def __init__(self, source: Union[int, str]):
        """
        Initializer

        :param source: The camera source. When a number is passed it will be interpreted as "web cam" index, e.g. 0,
        otherwise it will be handled as gstreamer pipeline definition.
        """
        super().__init__()
        self.source: Union[int, str] = source
        self.handle: Optional["cv.VideoCapture"] = None

    def handle_initialize_camera(self):
        import cv2 as cv
        if isinstance(self.source, str):  # if a full pipeline is defined, connect via gstreamer
            self.handle = cv.VideoCapture(self.source, cv.CAP_GSTREAMER)
        else:  # otherwise n00b mode and just select by index
            self.handle = cv.VideoCapture(self.source)

    def handle_fetch(self) -> Tuple[float, Optional[Image]]:
        ret, image = self.handle.read()
        if ret:
            return time.time(), Image(image[..., ::-1].copy())
        else:
            return 0.0, None
