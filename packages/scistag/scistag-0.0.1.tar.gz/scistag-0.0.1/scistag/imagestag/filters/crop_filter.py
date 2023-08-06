from typing import Tuple

from scistag.imagestag.image_filter import *


class CropFilter(ImageFilter):
    """
    Crops a selected region out of an image
    """

    def __init__(self, box: Tuple[int, int, int, int]):
        """
        Initializer

        :param box: The region to crop (x, y, x2, y2)
        """
        super(CropFilter, self).__init__()
        self.name = "crop"
        self.box = box

    def _apply_filter(self, input_data: dict) -> dict:
        image: Image = input_data[IMAGE_FILTER_IMAGE]
        return {IMAGE_FILTER_IMAGE: image.crop(self.box)}
