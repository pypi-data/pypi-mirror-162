from typing import Optional, Union
from dataclasses import dataclass


@dataclass
class Size2D:
    """
    Defines the size of an element
    """
    width: float = 0.0
    "The width in pixels"
    height: float = 0.0
    "The height in pixels"

    def __init__(self, *args, **kwargs):
        """
        Initializer
        :param args: Either a set of two integer or float values, a 2-value tuple or a Size2D object to copy
        :param kwargs: width and height if provided.
        """
        if len(args) == 1:
            tuple_data = args[0]
            if isinstance(tuple_data, Size2D):
                self.width = tuple_data.width
                self.height = tuple_data.height
            else:
                self.width = float(tuple_data[0])
                self.height = float(tuple_data[1])
        elif len(args) == 2:
            self.width = float(args[0])
            self.height = float(args[1])
        else:
            if 'width' in kwargs and 'height' in kwargs:
                self.width = float(kwargs.get('width'))
                self.height = float(kwargs.get('height'))
            else:
                raise NotImplemented("Unsupported combination of parameters")

    def to_tuple(self) -> (float, float):
        """
        Returns the size as tuple
        :return: Width, Height
        """
        return self.width, self.height

    def to_int_tuple(self) -> (float, float):
        """
        Returns the size as int tuple
        :return: Width, Height
        """
        return int(round(self.width)), int(round(self.height))

    def __eq__(self, other: 'Size2D') -> bool:
        return self.width == other.width and self.height == other.height

    def __ne__(self, other: 'Size2D') -> bool:
        return self.width != other.width or self.height != other.height


@dataclass
class Pos2D:
    """
    Defines the position of an element
    """
    x: float = 0.0
    y: float = 0.0

    def __init__(self, *args, **kwargs):
        """
        Initializer
        :param args: Either a set of two integer or float values, a 2-value tuple or a Pos2D object to copy
        :param kwargs: x and y if provided.
        """
        if len(args) == 1:
            tuple_data = args[0]
            if isinstance(tuple_data, Pos2D):
                self.x = tuple_data.x
                self.y = tuple_data.y
            else:
                self.x = float(tuple_data[0])
                self.y = float(tuple_data[1])
        elif len(args) == 2:
            self.x = float(args[0])
            self.y = float(args[1])
        else:
            if 'x' in kwargs and 'y' in kwargs:
                self.x = float(kwargs.get('x'))
                self.y = float(kwargs.get('y'))
            else:
                raise NotImplemented("Unsupported combination of parameters")

    def to_tuple(self) -> (float, float):
        """
        Returns the position as tuple
        :return: X, Y
        """
        return self.x, self.y

    def to_tuple(self) -> (float, float):
        """
        Returns the position as tuple
        :return: X, Y
        """
        return self.x, self.y

    def __eq__(self, other: 'Pos2D') -> bool:
        return self.x == other.x and self.y == other.y

    def __ne__(self, other: 'Pos2D') -> bool:
        return self.x != other.x or self.y != other.y


@dataclass
class Bounding2D:
    """
    Defines the bounding of an element
    """
    ul: Pos2D = Pos2D(0.0, 0.0)
    lr: Pos2D = Pos2D(0.0, 0.0)

    def __init__(self, ul: Optional[Pos2D] = None,
                 lr: Optional[Pos2D] = None, pos_size: Optional[tuple] = None,
                 bnd: Optional[Union[tuple, "Bounding2D"]] = None):
        """
        Initializer
        :param ul: Upper left coordinate
        :param lr: Lower right coordinate
        :param pos_size: 1d tuple x y w h or (Pos2D, Size2D)
        :param bnd: 1d tuple x y x2 y2
        """
        if bnd is not None and isinstance(bnd, Bounding2D):
            self.ul = bnd.ul
            self.lr = bnd.lr
            return

        if pos_size is not None:
            if isinstance(pos_size[0], Pos2D):
                pos: Pos2D = pos_size[0]
                size: Size2D = pos_size[1]
                self.ul = Pos2D(pos.x, pos.y)
                self.lr = Pos2D(pos.x + size.width, pos.y + size.height)
            else:
                self.ul = Pos2D(pos_size[0], pos_size[1])
                self.lr = Pos2D(pos_size[0] + pos_size[2], pos_size[1] + pos_size[3])
        elif bnd is not None:
            self.ul = Pos2D(bnd[0], bnd[1])
            self.lr = Pos2D(bnd[2], bnd[3])
        else:
            self.ul = ul
            self.lr = lr

    def copy(self) -> 'Bounding2D':
        """
        Creates a copy of the bounding
        :return: The copy
        """
        return Bounding2D(ul=Pos2D(self.ul.x, self.ul.y), lr=Pos2D(self.lr.x, self.lr.y))

    @classmethod
    def from_pos_size(cls, pos: Union[Pos2D, tuple], size: Union[Size2D, tuple]) -> 'Bounding2D':
        """
        Creates the bounding from x, y and width and height values
        :param pos: The coordinate of the upper left edge
        :param size: The size
        :return: The instance
        """
        if isinstance(pos, tuple):
            pos = Pos2D(*pos)
        if isinstance(size, tuple):
            size = Size2D(*size)
        return Bounding2D(ul=pos,
                          lr=Pos2D(pos.y + size.width, pos.y + size.height))

    @classmethod
    def from_xy_wh(cls, x, y, width, height) -> 'Bounding2D':
        """
        Creates the bounding from x, y and width and height values
        :param x: X coordinate
        :param y: Y coordinate
        :param width: Width in pixels
        :param height: Height in pixels
        :return: The instance
        """
        return Bounding2D(ul=Pos2D(x, y),
                          lr=Pos2D(x + width, y + height))

    @classmethod
    def from_xy_x2y2(cls, x, y, x2, y2) -> 'Bounding2D':
        """
        Creates the bounding from x, y and width and height values
        :param x: X coordinate
        :param y: Y coordinate
        :param x2: The lower right x coordinate. Note that this should point to the right edge of a pixel
        :param y2: The lower right y coordinate. Note that this should point to the bottom edge of a pixel,
        e.g. a full hd image of the size 1920x1080 would require a bounding of 0.0, 0.0, 1920.0, 1080.0.
        :return: The instance
        """
        return Bounding2D(Pos2D(x, y),
                          Pos2D(x2, y2))

    def pos(self) -> Pos2D:
        """
        Returns the element's position
        :return: The position
        """
        return self.ul

    def size(self) -> Size2D:
        """
        Returns the element's size
        :return: The size
        """
        return Size2D(width=self.lr.x - self.ul.x, height=self.lr.y - self.ul.y)

    def width(self) -> float:
        """
        Returns the element's width
        :return: The size
        """
        return self.lr.x - self.ul.x

    def height(self) -> float:
        """
        Returns the element's height
        :return: The size
        """
        return self.lr.y - self.ul.y

    def xy_x2y2(self) -> (float, float, float, float):
        """
        Returns the bounding as 1D coordinate tuple
        :return: x, y, x2, y2
        """
        return self.ul.x, self.ul.y, self.lr.x, self.lr.y

    def xy_wh(self) -> (float, float, float, float):
        """
        Returns the bounding as 1D coordinate, width, height tuple
        :return: x, y, w, h
        """
        return self.ul.x, self.ul.y, self.lr.x - self.ul.x, self.lr.y - self.ul.y

    def __eq__(self, other: 'Bounding2D') -> bool:
        return self.ul == other.ul and self.lr == other.lr

    def __ne__(self, other: 'Bounding2D') -> bool:
        return self.ul != other.ul or self.lr != other.lr


__all__ = ["Pos2D", "Size2D", "Bounding2D"]
