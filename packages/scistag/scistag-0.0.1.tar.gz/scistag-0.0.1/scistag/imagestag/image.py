from enum import Enum
from typing import Union, Tuple, Optional

import PIL.Image
import numpy as np

from .color import Color
from .bounding import Size2D
from .definitions import *
import io


class InterpolationMethod(Enum):
    """
    Enumeration of image interpolation methods
    """

    NEAREST = 0
    "The pixel will be kept intact, the upscaled image has quite hard pixel edges and the downscaled image is noisy"
    LINEAR = 1
    "Linear interpolation. Mixes up to four colors based upon subpixel position."
    CUBIC = 2
    "Cubic interpolation. Matches the pixels of the source region to the image region and tries to preserve contours"
    LANCZOS = 3
    "The highest image rescaling quality available in cv2/PIL. Use this if performance is not the most important"

    def to_cv(self):
        """
        Maps the enum to the corresponding OpenCV type
        :return: The OpenCV constant
        """
        cv2_mapping = {
            self.NEAREST: 6,  # cv2.INTER_NEAREST_EXACT,
            self.LINEAR: 1,  # cv2.INTER_LINEAR,
            self.CUBIC: 2,  # cv2.INTER_CUBIC
            self.LANCZOS: 4  # cv2.INTER_LANCZOS4
        }
        "Definition of mappings from SciStag.Image to OpenCV"
        return cv2_mapping[self]

    def to_pil(self):
        """
        Maps the enum to the corresponding PIL type
        :return: The PIL constant
        """
        pil_mapping = {
            self.NEAREST: PIL.Image.NEAREST,
            self.LINEAR: PIL.Image.BILINEAR,
            self.CUBIC: PIL.Image.BICUBIC,
            self.LANCZOS: PIL.Image.LANCZOS
        }
        "Definition of mappings from SciStag.Image to PIL"
        return pil_mapping[self]


class PixelFormat(Enum):
    """
    Enumeration of different pixel formats
    """
    RGB = 0
    "Red Green Blue"
    RGBA = 1
    "Red Green Blue Alpha"
    BGR = 5
    "Blue Green Red"
    BGRA = 6
    "Blue Green Red Alpha"
    GRAY = 10
    "Grayscale"


IMAGE_SOURCE_TYPES = Union[str, np.ndarray, bytes, PIL.Image.Image, "Image"]
"The valid source type for loading an image"


class Image:
    """
    SDK independent image handle
    """

    def __init__(self, source: IMAGE_SOURCE_TYPES, framework: ImsFramework = None,
                 source_pixel_format=None):
        """
        Creates an image from a set of various sources
        :param source: The image source. Either a file name, an url, numpy array or one of the supported low level types
        :param framework: The framework to be used if the file is loaded from disk
        :param source_pixel_format: The pixel format (if passed as np.array). Auto detect by efault

        Raises a ValueError if the image could not be loaded
        """
        if source_pixel_format is None:
            source_pixel_format = PixelFormat.RGB
        self.width = 1
        "Image width"
        self.height = 1
        "Image height"
        self.framework = framework if framework is not None else ImsFramework.PIL
        "The framework being used"
        self._pil_handle: Optional[PIL.Image.Image] = None
        "The pillow handle (if available)"
        self._pixel_data: Optional[np.ndarray] = None
        "The pixel data (if available)"
        self.pixel_format = source_pixel_format
        "Base format (rgb / bgr)"
        # ------- preparation of source data -------
        if isinstance(source, type(self)):
            source = source.to_pil()
        if isinstance(source, np.ndarray) and self.pixel_format == PixelFormat.BGR and framework != ImsFramework.CV2:
            source = self.normalize_to_rgb(source, keep_gray=True, input_format=self.pixel_format)
            self.pixel_format = self.detect_format(source)
        # fetch from web if desired
        if isinstance(source, str) and (source.startswith("http:") or source.startswith("https:")):
            from scistag.webstag import web_fetch
            source = web_fetch(source)
            if source is None:
                raise ValueError("Image data could not be received")
        # ------------------------------------------
        if framework is None:
            framework = ImsFramework.PIL
        if framework == ImsFramework.PIL:
            if isinstance(source, str):
                self._pil_handle = PIL.Image.open(source)
            elif isinstance(source, bytes):
                data = io.BytesIO(source)
                self._pil_handle = PIL.Image.open(data)
            elif isinstance(source, np.ndarray):
                self._pil_handle = PIL.Image.fromarray(source)
            elif isinstance(source, PIL.Image.Image):
                self._pil_handle = source
            else:
                raise NotImplemented
            self.width = self._pil_handle.width
            self.height = self._pil_handle.height
            self.pixel_format = self._pil_handle.mode.lower()
        elif framework == ImsFramework.RAW:
            self._pixel_data = self._pixel_data_from_source(source)
            self.height, self.width = self._pixel_data.shape[0:2]
            self.pixel_format = self.detect_format(self._pixel_data)
        elif framework == ImsFramework.CV2:
            if isinstance(source, np.ndarray):
                self._pixel_data = self.normalize_to_bgr(source, input_format=self.pixel_format, keep_gray=True)
                self.pixel_format = self.detect_format(self._pixel_data, is_cv2=True)
            else:
                self._pixel_data = Image(source).get_pixels(desired_format=self.pixel_format)
                self.pixel_format = self.detect_format(self._pixel_data, is_cv2=True)
            self.height, self.width = self._pixel_data.shape[0:2]
        else:
            raise NotImplemented

    def is_bgr(self) -> bool:
        """
        Returns if the current format is bgr or bgra
        :return: True if it is
        """
        return self.pixel_format == PixelFormat.BGR or self.pixel_format == PixelFormat.BGRA

    @classmethod
    def detect_format(cls, pixels: np.ndarray, is_cv2=False):
        """
        Detects the format
        :param pixels: The pixels
        :param is_cv2: Defines if the source was OpenCV
        :return: The pixel format. See PixelFormat
        """
        if len(pixels.shape) == 2:
            return PixelFormat.GRAY
        if is_cv2:
            return PixelFormat.BGR if pixels.shape[2] == 3 else PixelFormat.BGRA
        else:
            return PixelFormat.RGB if pixels.shape[2] == 3 else PixelFormat.RGBA

    @classmethod
    def _pixel_data_from_source(cls, source: Union[str, np.ndarray, bytes, PIL.Image.Image],
                                allow_cv2=False) -> np.ndarray:
        """
        Loads an arbitrary source and returns it as pixel data
        :param source: The data source. A filename, an url, numpy array or a PIL image
        :param allow_cv2: Defines if using OpenCV is allowed
        :return: The pixel data
        """
        if isinstance(source, np.ndarray):
            return source
        elif isinstance(source, PIL.Image.Image):
            # noinspection PyTypeChecker
            return np.array(source)
        elif isinstance(source, str) or isinstance(source, bytes):
            if CV2_AVAILABLE and allow_cv2:
                if isinstance(source, str):
                    pixel_data = cv.imread(source, cv.IMREAD_UNCHANGED)
                else:
                    pixel_data = cv.imdecode(np.frombuffer(source, dtype=np.uint8), cv.IMREAD_UNCHANGED)
                if len(pixel_data.shape) == 3:
                    return cls.normalize_to_rgb(pixel_data)
                else:
                    return pixel_data
            else:
                return Image(source, framework=ImsFramework.PIL).get_pixels()
        else:
            raise NotImplemented

    def get_size(self) -> Tuple[int, int]:
        """
        Returns the image's size
        :return: The size as tuple
        """
        if self.framework == ImsFramework.PIL:
            return self._pil_handle.size
        elif self._pixel_data is not None:
            return self._pixel_data.shape[0:2][::-1]
        else:
            raise NotImplemented

    def get_size_as_size(self) -> Size2D:
        """
        Returns the image's size
        :return: The size
        """
        if self.framework == ImsFramework.PIL:
            return Size2D(self.get_size())
        else:
            raise NotImplemented

    def crop(self, box: Tuple[int, int, int, int]) -> "Image":
        """
        Crops a region of the image and returns it
        :param box: The box in the form x, y, x2, y2
        :return: The image of the defined sub region
        """
        if box[2] < box[0] or box[3] < box[1]:
            raise ValueError("X2 or Y2 are not allowed to be smaller than X or Y")
        if box[0] < 0 or box[1] < 0 or box[2] >= self.width or box[3] >= self.height:
            raise ValueError("Box region out of image bounds")
        if self._pil_handle:
            return Image(self._pil_handle.crop(box=box))
        elif self._pixel_data:
            cropped = self._pixel_data[box[1]:box[3] + 1, box[0]:box[2] + 1, :] if len(self._pixel_data.shape) == 3 \
                else self._pixel_data[box[1]:box[3] + 1, box[0]:box[2] + 1]
            return Image(cropped, framework=self.framework, source_pixel_format=self.pixel_format)
        else:
            raise NotImplementedError("Crop not implemented for the sdk type")

    def resize(self, size: tuple):
        """
        Resizes the image to given resolution (modifying this image directly)
        :param size: The new size
        """
        if self.framework == ImsFramework.PIL:
            self._pil_handle = self._pil_handle.resize(size, PIL.Image.LANCZOS)
        elif self._pixel_data is not None:
            if CV2_AVAILABLE:
                self._pixel_data = cv.resize(self._pixel_data, dsize=size, interpolation=cv.INTER_LANCZOS4)
            else:
                image = Image(self._pixel_data, framework=ImsFramework.PIL)
                image.resize(size)
                self._pixel_data = image.get_pixels(desired_format=self.pixel_format)
        else:
            raise NotImplemented

    def resized(self, size: tuple) -> "Image":
        """
        Returns an image resized to to given resolution
        :param size: The new size
        """
        if self.framework == ImsFramework.PIL:
            return Image(self._pil_handle.resize(size, PIL.Image.LANCZOS), framework=ImsFramework.PIL)
        elif self._pixel_data is not None:
            if CV2_AVAILABLE:
                return Image(cv.resize(self._pixel_data, dsize=size, interpolation=cv.INTER_LANCZOS4),
                             source_pixel_format=self.pixel_format)
            else:
                return Image(self.to_pil().resize(size, PIL.Image.LANCZOS))
        else:
            raise NotImplemented

    def resized_ext(self, size: Optional[Tuple[int, int]] = None, keep_aspect: bool = False,
                    target_aspect: Optional[float] = None,
                    fill_area: bool = False, factor: Optional[float] = None,
                    interpolation: InterpolationMethod = InterpolationMethod.LANCZOS,
                    background_color=Color(0.0, 0.0, 0.0, 1.0)) -> "Image":
        """
        Returns a resized variant of the image with several different configuration possibilities.

        :param size: The target size as tuple (in pixels) (optional)
        :param keep_aspect: Defines if the aspect ratio shall be kept. if set to true the image
        will be zoomed or shrinked equally on both axis so it fits the target size. False by default.
        :param target_aspect: If defined the image will be forced into given aspect ratio by adding "black bars"
        (or the color you defined in "background_color"). Common values are for example 4/3, 16/9 or 21/9.
        Note that this does NOT change the aspect ratio of the real image itself. If you want to change this just
        call this function with the desired "size" parameter.
        It will always preserve the size of the axis to which no black bares are added, so e.g. converting an image
        from 4:3 to 16:9 resulting in black bars on left and right side the original height will be kept. Converting
        an image from 16:9 to 4:3 on the other hand where black bars are added on top and bottom the width will be kept.
        Overrides "size".
        :param fill_area: Defines if the whole area shall be filled with the original image. False by default. Only
        evaluated if keep_aspect is True as well as otherwise a simple definition of "size" would anyway do the job.
        :param factor: Scales the image by given factor. Overwrites size. Can be combined with target_aspect.
        None by default. Overrides "size".
        :param interpolation: The interpolation method.
        :param background_color: The color which shall be used to fill the empty area, e.g. when a certain aspect ratio
        is enforced.
        """
        handle = self.to_pil()
        resample_method = interpolation.to_pil()
        int_color = background_color.int_rgba()
        bordered_image_size = None  # target image size (including black borders)
        if keep_aspect and size is not None:
            if fill_area:
                factor = max([size[0] / self.width, size[1] / self.height])
                virtual_size = int(round(factor * self.width)), int(round(factor * self.height))
                ratio = size[0] / virtual_size[0], size[1] / virtual_size[1]
                used_pixels = int(round(self.width * ratio[0])), int(round(self.height * ratio[1]))
                offset = self.width // 2 - used_pixels[0] // 2, self.height // 2 - used_pixels[1] // 2,
                return Image(handle.resize(size, resample=resample_method,
                                           box=[offset[0], offset[1], offset[0] + used_pixels[0] - 1,
                                                offset[1] + used_pixels[1] - 1]))
            else:
                bordered_image_size = size
                factor = min([size[0] / self.width, size[1] / self.height])
        if fill_area:
            raise ValueError('fill_area==True without keep_aspect==True has no effect. If you anyway just want to ' +
                             'fill the whole area with the image just provide "size" and set "fill_area" to False')
        if target_aspect is not None:
            if size is not None:
                raise ValueError('"target_aspect" can not be combined with "size" but just with factor. ' +
                                 'Use "size" + "keep_aspect" instead if you know the desired target size already.')
            factor = 1.0 if factor is None else factor
            if factor != 1.0:  # if the image shall also be resized
                size = int(round(self.width * factor)), int(round(self.height * factor))
            else:
                size = self.width, self.height
        if factor is not None:
            size = int(round(self.width * factor)), int(round(self.height * factor))
        assert size is not None and size[0] > 0 and size[1] > 0
        if size != (self.width, self.height):
            handle = handle.resize(size, resample=resample_method)
        if target_aspect is not None:
            rs = 1.0 / target_aspect
            cur_aspect = self.width / self.height
            if cur_aspect < target_aspect:  # if cur_aspect is smaller we need to add black bars to the sides
                bordered_image_size = (
                    int(round(self.height * target_aspect * factor)), int(round(self.height * factor)))
            else:  # otherwise to top and bottom
                bordered_image_size = (int(round(self.width * factor)), int(round(self.width * rs ** factor)))
        if bordered_image_size is not None:
            new_image = PIL.Image.new(handle.mode, bordered_image_size, int_color)
            position = (new_image.width // 2 - handle.width // 2, new_image.height // 2 - handle.height // 2)
            new_image.paste(handle, position)
            return Image(new_image)
        return Image(handle)

    def get_handle(self) -> Union[np.ndarray, PIL.Image.Image]:
        """
        Returns the low level handle
        :return: The handle
        """
        return self._pil_handle if self.framework == ImsFramework.PIL else self._pixel_data

    @staticmethod
    def bgr_to_rgb(pixel_data: np.ndarray) -> np.ndarray:
        """
        Converts BGR to RGB or the otherwise round
        :param pixel_data: The input pixel data
        :return: The output pixel data
        """
        if len(pixel_data.shape) == 3 and pixel_data.shape[2] == 3:
            return pixel_data[..., ::-1].copy()
        elif len(pixel_data.shape) == 3 and pixel_data.shape[2] == 4:
            return pixel_data[..., [2, 1, 0, 3]].copy()

    @classmethod
    def normalize_to_rgb(cls, pixels: np.ndarray, input_format: str = "rgb", keep_gray=False) -> np.ndarray:
        """
        Guarantees that the output will be in the RGB or RGBA format
        :param pixels: The pixel data
        :param input_format: The input format, e.g. "rgb" See Image.__init__
        :param keep_gray: Defines if single channel formats shall be kept intact. False by default.
        :return: The RGB image as numpy array. If keep_gray was set and the input was single channeled the original.
        """
        if len(pixels.shape) == 2:  # grayscale?
            if keep_gray:
                return pixels
            return np.stack((pixels,) * 3, axis=-1)
        if input_format == PixelFormat.BGR or input_format == PixelFormat.BGRA:
            return cls.bgr_to_rgb(pixels)
        else:
            return pixels

    @classmethod
    def normalize_to_bgr(cls, pixels: np.ndarray, input_format: PixelFormat = PixelFormat.RGB,
                         keep_gray=False) -> np.ndarray:
        """
        Guarantees that the output will be in the BGR or BGRA format
        :param pixels: The pixel data
        :param input_format: The input format, e.g. "rgb" See Image.__init__
        :param keep_gray: Defines if single channel formats shall be kept intact. False by default.
        :return: The BGR image as numpy array. If keep_gray was set and the input was single channeled the original.
        """
        if len(pixels.shape) == 2:  # grayscale?
            if keep_gray:
                return pixels
            return np.stack((pixels,) * 3, axis=-1)
        if input_format == PixelFormat.BGR or input_format == PixelFormat.BGRA:
            return pixels
        else:
            return cls.bgr_to_rgb(pixels)

    @classmethod
    def normalize_to_gray(cls, pixels: np.ndarray, input_format: PixelFormat = PixelFormat.RGB) -> np.ndarray:
        """
        Guarantees that the output will be grayscale
        :param pixels: The pixel data
        :param input_format: The input format, e.g. "rgb" See Image.__init__
        :return: The grayscale image
        """
        if len(pixels.shape) == 2:  # grayscale?
            return pixels
        if input_format == PixelFormat.BGR or input_format == PixelFormat.BGRA:
            b, g, r = pixels[:, :, 0], pixels[:, :, 1], pixels[:, :, 2]
        else:
            r, g, b = pixels[:, :, 0], pixels[:, :, 1], pixels[:, :, 2]
        return (0.2989 * r + 0.5870 * g + 0.1140 * b).round().astype(np.uint8)

    def get_pixels(self, desired_format: PixelFormat = PixelFormat.RGB) -> np.ndarray:
        """
        Returns the image's pixel data
        :param desired_format: Defines the desired format. "rgb" or "bgr"
        :return: The numpy array containing the pixels
        """
        bgr = desired_format == PixelFormat.BGR or desired_format == PixelFormat.BGRA
        gray = desired_format == PixelFormat.GRAY
        if self.framework != ImsFramework.PIL:  # not PIL
            if self._pixel_data is not None:
                if gray:
                    return self.normalize_to_gray(self._pixel_data)
                if not self.is_bgr() and not bgr:
                    return self._pixel_data
                if self.is_bgr():
                    if bgr:
                        return self._pixel_data
                    else:
                        if len(self._pixel_data.shape) == 2:
                            return self._pixel_data
                        else:
                            return self.bgr_to_rgb(self._pixel_data)
                return self._pixel_data if not bgr else self.normalize_to_bgr(self._pixel_data)
            else:
                raise NotImplementedError
        # PIL
        image: PIL.Image.Image = self._pil_handle
        # noinspection PyTypeChecker
        pixel_data = np.array(image)
        if gray:
            return self.normalize_to_gray(pixel_data)
        if bgr:
            pixel_data = self.normalize_to_bgr(pixel_data)
        return pixel_data

    def get_pixels_rgb(self) -> np.ndarray:
        """
        Returns the pixels and ensures they are either rgb or rgba
        """
        pixels = self.get_pixels()
        if len(pixels.shape) == 2:  # gray scale? stack it
            return np.stack((pixels,) * 3, axis=-1)
        else:
            return pixels if self.pixel_format == PixelFormat.RGB or self.pixel_format == PixelFormat.RGBA else \
                self.get_pixels(PixelFormat.RGB)

    def get_pixels_bgr(self) -> np.ndarray:
        """
        Returns the pixels and ensures they are either bgr or bgra
        """
        pixels = self.get_pixels(desired_format=PixelFormat.BGR)
        if len(pixels.shape) == 2:  # gray scale? stack it
            return np.stack((pixels,) * 3, axis=-1)
        else:
            return pixels if self.pixel_format == PixelFormat.BGR or self.pixel_format == PixelFormat.BGRA else \
                self.get_pixels(PixelFormat.BGR)

    def get_pixels_gray(self) -> np.ndarray:
        """
        Returns the pixels and ensures they are gray scale
        """
        if self._pixel_data is not None:
            return self.normalize_to_gray(self._pixel_data, input_format=self.pixel_format)
        pixels = self.get_pixels(desired_format=PixelFormat.GRAY)
        return pixels

    def to_pil(self) -> PIL.Image.Image:
        """
        Converts the image to a PIL image object
        :return: The PIL image
        """
        if self._pil_handle is not None:
            return self._pil_handle
        else:
            pixel_data = self.get_pixels()  # guarantee RGB
            return PIL.Image.fromarray(pixel_data)


__all__ = ["Image", "IMAGE_SOURCE_TYPES", "PixelFormat", "InterpolationMethod"]
