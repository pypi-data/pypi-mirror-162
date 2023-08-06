from io import BytesIO
from typing import Union, Tuple

import PIL.ImageFont

from scistag.imagestag import ImsFramework


class Font:
    """
    SDK independent font handle
    """

    def __init__(self, source: Union[str, bytes, BytesIO], size: int, framework: ImsFramework, index=0):
        """
        Initializer
        :param source: The font source. Either a file path, a bytes like object or a stream
        :param size: The font's size
        :param framework: The framework to be used
        :param index: The font face index
        """
        self.framework = framework
        if isinstance(source, bytes):
            source = BytesIO(source)
        if framework == ImsFramework.PIL:
            self._font_handle = PIL.ImageFont.truetype(source, size, index=index)
        else:
            self._font_handle = None
            raise NotImplementedError("At the moment only PIL fonts are supported.")

    def get_handle(self) -> PIL.ImageFont.FreeTypeFont:
        """
        Returns the low level font handle
        :return: The font handle
        """
        return self._font_handle

    def get_bbox(self, text: str) -> Tuple[int, int, int, int]:
        """
        Returns the bounding box of the text in pixels
        :param text: The text
        :return: The bbox (x,y,x2,y2)
        """
        if self.framework == ImsFramework.PIL:
            return self._font_handle.getbbox(text)
        else:
            raise NotImplementedError("At the moment only PIL fonts are supported.")
