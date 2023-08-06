from enum import Enum


class Alignment:
    """
    The alignment base class. The alignment defines how a widget shall be automatically resized and/or located.
    All base views support RegionAlignments (left, top, client etc.) and anchor based alignments. Some special parent
    views (still to be defined) may support advanced alignment types, such a grid layout, in the future.
    """

    def __init__(self):
        pass


class AlignmentSide(Enum):
    NONE = -1  # No special alignment
    LEFT = 0  # Dock to the left side, fill from top to bottom
    RIGHT = 1  # Dock to the right side, fill from top to bottom
    TOP = 2  # Dock to the top, fill from left to right
    BOTTOM = 3  # Dock to the bottom, fill from left to right
    CLIENT = 4  # Fill the remaining area. If there are multiple views of this type they are layered above each other


class RegionAlignment:
    """
    A regional alignment (as seen in many Windows classic applications) defines if a view shall fill a whole other
    view or visualizes for a example a side bar with a fixed width but always filling the side from top to bottom.
    """

    def __init__(self, alignment: AlignmentSide):
        """
        Initializer
        :param alignment: The alignment mode, e.g. AlignmentSide.LEFT
        """
        self.alignment = alignment
