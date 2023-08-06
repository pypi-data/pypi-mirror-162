from scistag.imagestag.image_filter import *
import numpy as np

COLOR_MAP_VIRIDIS = "viridis"
"The default pyplot map"
COLOR_MAP_INFERNO = "inferno"
"Inferno sequential map"

# Definition of color maps. For maps have a look at https://matplotlib.org/stable/tutorials/colors/colormaps.html
COLOR_MAPS_P_U_SEQUENTIAL = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']
"Perceptually Uniform Sequential color maps"

COLOR_MAPS_SEQUENTIAL = ['Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
                         'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                         'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']
"Sequential color maps"
COLOR_MAPS_SEQUENTIAL2 = ['binary', 'gist_yarg', 'gist_gray', 'gray', 'bone',
                          'pink', 'spring', 'summer', 'autumn', 'winter', 'cool',
                          'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper']
"Additional sequential color maps"
COLOR_MAPS_DIVERGING = ['PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu',
                        'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']
"Diverging color maps"
COLOR_MAPS_CYCLIC = ['twilight', 'twilight_shifted', 'hsv']
"Cyclic color maps"
COLOR_MAPS_QUALITATIVE = ['Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2',
                          'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b',
                          'tab20c']
"Qualitative color maps"
COLOR_MAPS_MISC = ['flag', 'prism', 'ocean', 'gist_earth', 'terrain',
                   'gist_stern', 'gnuplot', 'gnuplot2', 'CMRmap',
                   'cubehelix', 'brg', 'gist_rainbow', 'rainbow', 'jet',
                   'turbo', 'nipy_spectral', 'gist_ncar']
"Miscellaneous color maps"


class ColorMapFilter(ImageFilter):
    """
    Applies a color map to a grayscale image to maximize the image's contrast or make the color ranges easier
    to interprete. ... and of course also to just make it look cooler ;-)
    """

    def __init__(self, normalize=True, color_map: str = COLOR_MAP_VIRIDIS):
        """
        Initializer

        :param normalize: Defines if the grayscale image gets normalized to a range from 0..255 before applying the
        :param color_map: The color map to be used. Use one of the provided COLOR_MAPS constants or have a look
        at https://matplotlib.org/stable/tutorials/colors/colormaps.html.
        """
        super(ColorMapFilter, self).__init__()
        self.requires_format = PixelFormat.GRAY
        self.normalize = normalize
        self._color_map_name = ""
        self.precise = False
        self._set_color_map(color_map)
        "Defines if the grayscale image gets normalized to a range from 0..255 before applying the filter"
        self.name = f"colorMap_{self._color_map_name}"

    def _set_color_map(self, color_map_name: str):
        import matplotlib.pyplot as plt
        self.color_map = plt.get_cmap(color_map_name)
        self._color_map_name = color_map_name
        if not self.precise:
            range_table = np.array([[index / 255.0 for index in range(256)]])
            mapped_colors = self.color_map(range_table)
            self.table = (mapped_colors * 255).astype(np.uint8).reshape((256, 4))
        else:
            self.table = None

    def _apply_filter(self, input_data: dict) -> dict:
        org_image = image = input_data[IMAGE_FILTER_IMAGE]
        image: Image
        gray_image = image.get_pixels_gray()
        if self.normalize:
            min_v = np.min(gray_image)
            max_v = np.max(gray_image[gray_image.shape[0] // 3:, :])
            diff = max_v - min_v
            if diff > 0:
                scaling = 255.0 / diff
                gray_image = np.clip(((gray_image - min_v) * scaling), 0, 255).astype(np.uint8)
        if self.table is not None:
            result: np.ndarray = np.dstack([self.table[:, i][gray_image] for i in range(3)])
        else:
            norm_gray_image = gray_image / 255.0
            result: np.ndarray = (self.color_map(norm_gray_image) * 255).astype(np.uint8)
        return {IMAGE_FILTER_IMAGE: Image(result, framework=org_image.framework)}


__all__ = ["ColorMapFilter", "COLOR_MAPS_P_U_SEQUENTIAL", "COLOR_MAPS_SEQUENTIAL2", "COLOR_MAPS_QUALITATIVE",
           "COLOR_MAPS_DIVERGING", "COLOR_MAPS_CYCLIC", "COLOR_MAPS_MISC", "COLOR_MAP_VIRIDIS", "COLOR_MAP_INFERNO"]
