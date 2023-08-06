from threading import RLock
from typing import List, Optional, Union, Tuple, Set
import numpy as np
import PIL.Image
import PIL.ImageFont
import PIL.ImageDraw
import os
import io

from . import Font
from .definitions import *
from .image import Image
from .bounding import *
from .color import *
from .definitions import __all__ as all_definitions
from .bounding import __all__ as all_sb
from .color import __all__ as all_sc

PositionTypes = Union[Pos2D, Tuple[int, int], Tuple[float, float]]
"The supported position types. Either a Pos2D or a tuple of two integers or floats"
BoundingTypes = Union[Bounding2D, Tuple[int, int, int, int], Tuple[float, float, float, float]]
"The supported bounding types. Either a Bounding2D or a 4-tuple of either integers or floats"


class Canvas:
    """
    Defines the base class for drawing targets in SlideStag
    """

    global_lock = RLock()  # Global access locks
    font_cache = {}  # Global font cache
    max_font_cache_size = 20  # Maximum count of cached font handles
    image_cache = {}  # Shared image resources, e.g. for UI components

    def __init__(self, width: int = 0, height: int = 0, default_color=(0, 0, 0), media_paths: Optional[List] = None,
                 framework: Optional[ImsFramework] = None, use_opencv_compression=False):
        """
        Initializer
        :param width: The canvas' width in pixels
        :param height: The canvas' height in pixels
        :param media_paths: The media paths to search fonts and images in
        :param framework: The framework to be used
        """
        self.width = width
        self.height = height
        self.size = (self.width, self.height)
        "The canvas' size in pixels"
        self.offset = (0, 0)
        """The current painting offset in pixels"""
        self.clip_region = (0, 0, width, height)
        """The min and max x y position valid for painting. Note that this is not respected by many paint
        commands but shall just help skipping irrelevant geometries completely."""
        self.media_paths = list(media_paths) if media_paths is not None else []
        "The list of paths to search fonts and graphics within when they are loaded with e.g. load_image"
        self.framework = ImsFramework.PIL if framework is None else framework
        "The rendering framework being used"
        self.use_opencv_compression = use_opencv_compression
        "Try using OpenCV for the compression where possible"
        self.stat_stack = []
        "Buffer to backup and restore the current painting state such as offset and clipping bounding"
        if self.framework == ImsFramework.PIL:
            self._image_data = PIL.Image.new('RGB', (self.width, self.height), color=default_color)
            self._image_draw = PIL.ImageDraw.ImageDraw(self._image_data)
        else:
            raise NotImplemented

    def push_state(self):
        """
        Backups the current state
        """
        self.stat_stack.append({'offset': self.offset, "clip": self.clip_region})

    def pop_state(self):
        """
        Restores the previous state
        """
        prev_state = self.stat_stack.pop()
        self.offset = prev_state['offset']
        self.clip_region = prev_state['clip']

    def shift_offset(self, offset: tuple):
        """
        Shifts the painting offset by given x, y distance
        :param offset: The distance of movement in pixels
        """
        self.offset = (self.offset[0] + offset[0], self.offset[1] + offset[1])

    def clip(self, offset: (float, float), size: (float, float)):
        """
        Clips the current painting region, relative to the current one
        :param offset: The distance of movement in pixels
        :param size: The width and height of the painting region
        """
        self.offset = (self.offset[0] + offset[0], self.offset[1] + offset[1])
        self.clip_region = (max(self.offset[0], self.clip_region[0]),
                            max(self.offset[1], self.clip_region[1]),
                            min(self.offset[0] + size[0], self.clip_region[2]),
                            min(self.offset[1] + size[1], self.clip_region[3]))
        self.clip_region = (min(self.clip_region[0], self.clip_region[2]),  # x/y should be <= x2/y2
                            min(self.clip_region[1], self.clip_region[3]),
                            max(self.clip_region[0], self.clip_region[2]),  # x2/y2 should be >= x/y
                            max(self.clip_region[1], self.clip_region[3]))

    def load_image(self, source: Union[str, bytes, np.ndarray], size: Optional[tuple] = None,
                   cache=False) -> Optional[Image]:
        """
        Loads an image from file or from a numpy array
        :param source: The image source
        :param size: If specified the image will be reduced to the size provided
        :param cache: Defines if the image can be cached. Do not set this flag for images use e.g. on slides but use
        cache there instead.
        :return: The image handle
        """
        if isinstance(source, np.ndarray) or isinstance(source, bytes):
            image = Image(source=source, framework=self.framework)
            if size is not None:
                image.resize(size)
            return image
        cur_fn = None
        found = False
        with self.global_lock:
            for path in reversed(self.media_paths):
                cur_fn = path + "/" + source
                if os.path.exists(cur_fn):
                    found = True
                    break
        cache_fn = cur_fn + "" if size is None else f"__{size[0]}x{size[1]}"
        if found:
            if cache:
                with self.global_lock:
                    if cur_fn in self.image_cache:
                        return self.image_cache[cache_fn]
            image = Image(cur_fn, framework=self.framework)
            if size is not None:
                image.resize(size)
            if cache:
                with self.global_lock:
                    self.image_cache[cache_fn] = image
            return image
        else:
            return None

    def get_drawer_handle(self) -> PIL.ImageDraw.ImageDraw:
        """
        Returns the low level drawer handle
        :return: The handle
        """
        return self._image_draw

    def get_image_handle(self) -> PIL.Image.Image:
        """
        Returns the low level image handle
        :return: The handle
        """
        return self._image_data

    def compress(self, filetype: str, compression: int):
        """
        Compresses the image data and returns it
        :param filetype: The filetype, e.g. "png" or "jpg"
        :param compression: The compression grade (0..100, 100 = best quality)
        :return: The bytes data
        """
        output = io.BytesIO()
        if self.framework == ImsFramework.PIL:
            if filetype.startswith("."):
                filetype = filetype[1:]
            if filetype.upper() == "JPG":
                filetype = "JPEG"
        try:
            if self.use_opencv_compression:
                import cv2 as cv
                open_cv_image = np.array(output)
                # Convert RGB to BGR
                open_cv_image = open_cv_image[:, :, ::-1].copy()
                encode_param = [int(cv.IMWRITE_JPEG_QUALITY), compression]
                _, result = cv.imencode("." + filetype, open_cv_image, encode_param)
                return result.tobytes()
        except:
            pass

        self._image_data.save(output, format=filetype, quality=compression)
        return output.getvalue()

    def draw_image(self, image: Image, position: tuple, auto_blend=True):
        """
        Draws given image into the canvas
        :param image: The source image
        :param position: The target position
        :param auto_blend: Defines if the image shall automatically alpha blend if it contains an alpha channel
        :return:
        """
        position = self.shift_position_by_offset(position)
        if self.framework == ImsFramework.PIL:
            pil_image: Image.Image = image.get_handle()
            if pil_image.mode == "RGBA" and auto_blend:
                self._image_data.paste(pil_image, position, pil_image)
            else:
                self._image_data.paste(pil_image, position)
        else:
            raise NotImplemented

    def rect(self,
             bounding: BoundingTypes,
             color: Optional[ColorTypes] = None,
             outline: Optional[ColorTypes] = None,
             outline_width: int = 1):
        """
        Draws a rectangle
        :param bounding: The rectangles bouding (x,y,x2,y2)
        :param color: The inner color
        :param outline: The outline color
        :param outline_width: The outline's width
        :return:
        """
        if isinstance(bounding, tuple):
            bounding = Bounding2D(bnd=bounding)
        if color is not None and isinstance(color, tuple):
            color = Color(value=color)
        if outline is not None and isinstance(outline, tuple):
            outline = Color(value=outline)
        xy, x2y2 = self.shift_position_by_offset(bounding.ul), self.shift_position_by_offset(bounding.lr)
        if self.framework == ImsFramework.PIL:
            self._image_draw.rectangle(xy=(xy, x2y2), fill=color.int_rgba() if color is not None else None,
                                       outline=outline.int_rgba() if outline is not None else None,
                                       width=outline_width)
        else:
            raise NotImplementedError

    def get_font(self, font_face: str, size: int, flags: Optional[Set[str]] = None) -> Optional[Font]:
        """
        Tries to create a font handle for given font
        :param font_face: The font's face
        :param size: The font's size
        :param flags: The flags such as {'Bold'} or {'Bold', 'Italic'}
        :return: On success the handle of the font
        """
        with self.global_lock:
            identifier = (font_face, size, flags)
            if identifier in self.font_cache:
                return self.font_cache[identifier]
            if len(self.font_cache) >= self.max_font_cache_size:
                del self.font_cache[next(iter(self.font_cache.keys()))]
        from scistag.imagestag.font_registry import FontRegistry
        new_font = FontRegistry.get_font(font_face=font_face, size=size, flags=flags)
        with self.global_lock:
            self.font_cache[identifier] = new_font
        return new_font

    def text(self, pos: PositionTypes, text: str, color: ColorTypes = None,
             font: Font = None, line_spacing: int = 4, align: str = "left", language: Optional[str] = None,
             stroke_width: int = 0, stroke_color: Optional[ColorTypes] = None):
        """
        :param pos: The text's position in x, y coordinates
        :param text: The text to be drawn
        :param color: The text's color
        :param font: The font to be used.
        :param line_spacing: The spacing between each line in pixels
        :param align: The text's alignment ("left", "center", or "right")
        :param language: The language code. See https://www.w3.org/International/articles/language-tags/
        :param stroke_width: The stroke width in pixels. Only has effect if stroke_color is not None
        :param stroke_color: The stroke color
        """
        if self.framework == ImsFramework.PIL:
            xy = Pos2D(pos) if not isinstance(pos, Pos2D) else pos
            xy = self.shift_position_by_offset(xy)
            color = Color(value=color).int_rgba() if not isinstance(color, Color) else color
            stroke_color = Color(value=stroke_color).int_rgba() if stroke_color is not None else None
            pil_font = font.get_handle()
            self._image_draw.text(xy=xy, text=text, font=pil_font, spacing=line_spacing, align=align, fill=color,
                                  language=language, stroke_width=stroke_width, stroke_fill=stroke_color)
        else:
            raise NotImplementedError

    def shift_position_by_offset(self, position: Union[tuple, Pos2D]) -> tuple:
        """
        Shifts given coordinates by this canvas' current offset
        :param position: The position
        :return: The new position as tuple
        """
        if isinstance(position, Pos2D):
            return self.offset[0] + position.x, self.offset[1] + position.y
        return self.offset[0] + position[0], self.offset[1] + position[1]


__all__ = ["Canvas"] + all_sb + all_sc + all_definitions
