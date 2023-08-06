from typing import Optional, Union, Tuple
from dataclasses import dataclass


@dataclass
class Color:
    _r: float = 1.0
    "The red color component. 0 .. 1.0"
    _g: float = 1.0
    "The green color component. 0 .. 1.0"
    _b: float = 1.0
    "The blue color component. 0 .. 1.0"
    _a: float = 1.0
    "The alpha color component. (0=completely transparent, 1.0 = 100% opaque)"

    _float_tuple: tuple = ()
    "Cached float tuple"
    _int_tuple: tuple = ()
    "Cached, rounded int tuple"

    def __init__(self, r=1.0, g=1.0, b=1.0, a=1.0, value: Optional[tuple] = None):
        """
        Initializer

        :param r: Red (0.0 .. 1.0)
        :param g: Green (0.0 .. 1.0)
        :param b: Blue (0.0 .. 1.0)
        :param a: Alpha (0.0 .. 1.0)
        :param value: A tuple of 3 or 4 floats or integers defining the color. Float values are assumed to be in range
        0 .. 1.0. Int value in range 0 .. 255
        """
        if value is not None:
            if len(value) < 2 or len(value) > 4:
                raise ValueError("Invalid color structure. 3 or 4 values assumed.")
            if isinstance(value[0], float):
                if len(value) == 3:
                    self._r, self._b, self._g = value
                    self._a = 1.0
                else:
                    self._r, self._b, self._g, self._a = value
            else:
                if len(value) == 3:
                    self._r, self._b, self._g = value[0] / 255.0, value[1] / 255.0, value[2] / 255.0
                    self._a = 1.0
                else:
                    self._r, self._b, self._g, self._a = value[0] / 255.0, value[1] / 255.0, value[2] / 255.0, value[
                        3] / 255.0,
        else:
            self._r = r
            self._g = g
            self._b = b
            self._a = a
        self._float_tuple = (self._r, self._g, self._b, self._a)
        self._int_tuple = tuple([int(round(element * 255.0)) for element in self._float_tuple])

    def to_rgb(self) -> (float, float, float):
        """
        Returns the color as rgb tuple (values from 0.0 .. 1.0)
        :return: The RGB values
        """
        return tuple(self._float_tuple[0:3])

    def to_rgba(self) -> (float, float, float, float):
        """
        Returns the color as rgba tuple (values from 0.0 .. 1.0)
        :return: The RGBA values
        """
        return self._float_tuple

    def int_rgb(self) -> (int, int, int):
        """
        Returns the color as rgb int tuple (values from 0 .. 255)
        :return: The RGB values
        """
        return self._int_tuple[0:3]

    def int_rgba(self) -> (int, int, int, int):
        """
        Returns the color as rgba int tuple (values from 0 .. 255)
        :return: The RGBA values
        """
        return self._int_tuple


ColorTypes = Union[Color, Tuple[int, int, int], Tuple[int, int, int, int],
                   Tuple[float, float, float], Tuple[float, float, float, float]]
"The supported color type. Either a Color or a tuple of 3 or 4 ints or floats (RGB/RGBA)"

__all__ = ["Color", "ColorTypes"]
