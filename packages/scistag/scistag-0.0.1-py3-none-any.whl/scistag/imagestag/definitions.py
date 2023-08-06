import enum

try:
    import PIL

    PIL_AVAILABLE = True
except ModuleNotFoundError:
    PIL_AVAILABLE = False

try:
    import cv2 as cv

    CV2_AVAILABLE = True
except ModuleNotFoundError:
    CV2_AVAILABLE = False


class ImsFramework(enum.Enum):
    """
    Definition of available frameworks
    """
    PIL = "PIL"  # Pillow (RGB / RGBA)
    RAW = "NP"   # Keep the numpy image as it is (RGB/RGBA)
    CV2 = "CV2"  # CV2 BGR/BGRA


__all__ = ["ImsFramework", "CV2_AVAILABLE", "PIL_AVAILABLE"]
if PIL_AVAILABLE:
    __all__ += ["PIL"]
if CV2_AVAILABLE:
    __all__ += ["cv"]
