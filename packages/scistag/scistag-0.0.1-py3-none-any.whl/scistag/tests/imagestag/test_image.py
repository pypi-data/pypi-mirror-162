import numpy as np
from scistag.imagestag import Image, ImsFramework
from image_tests_common import stag_image_data
import pytest


def test_load(stag_image_data):
    image = Image(stag_image_data)
    assert image.get_size() == (665, 525)
    assert image.to_pil() is not None
    pixels = image.get_pixels()
    assert pixels.shape == (525, 665, 3)


def test_resize(stag_image_data):
    image = Image(stag_image_data)
    image.resize((100, 120))
    assert image.get_pixels().shape == (120, 100, 3)


def test_raw(stag_image_data):
    image = Image(stag_image_data)
    image_raw = Image(stag_image_data, framework=ImsFramework.RAW)
    data = image_raw.get_handle()
    assert isinstance(data, np.ndarray)


def test_image_color_conversion(stag_image_data):
    """
    Tests the color conversion functions of Image
    :param stag_image_data: The image data in bytes
    :return:
    """
    image = Image(stag_image_data)
    pixel_data = image.get_pixels()
    bgr_pixel_data = image.get_pixels_bgr()
    gray_pixel_data = image.get_pixels_gray()
    rgb_pixel = (144, 140, 137)
    assert tuple(pixel_data[50, 50, :]) == rgb_pixel
    assert tuple(bgr_pixel_data[50, 50, :]) == (137, 140, 144)
    assert gray_pixel_data[50, 50] == round((np.array(rgb_pixel) * (0.2989, 0.5870, 0.1140)).sum())


def test_resize_ext(stag_image_data):
    """
    Tests Image.resize_ext
    :param stag_image_data: The image data in bytes
    """
    image = Image(stag_image_data)
    # to widescreen
    rescaled = image.resized_ext(target_aspect=16 / 9)  # aspect ratio resizing
    rescaled_pixels = rescaled.get_pixels()
    black_bar_mean = rescaled_pixels[0:, 0:100].mean() + rescaled_pixels[0:, -100:].mean()
    assert black_bar_mean == 0.0
    mean_rescaled = np.mean(rescaled_pixels)
    assert mean_rescaled == pytest.approx(87.5, 0.5)
    # to portrait mode
    rescaled = image.resized_ext(target_aspect=9 / 16)  # aspect ratio resizing
    rescaled_pixels = rescaled.get_pixels()
    black_bar_mean = rescaled_pixels[0:100, 0:].mean() + rescaled_pixels[-100:, 0:].mean()
    assert black_bar_mean == 0.0
    assert rescaled.width < rescaled.height
    # fill widescreen
    filled = image.resized_ext(size=(1920, 1080), fill_area=True, keep_aspect=True)
    filled_pixels = filled.get_pixels()
    mean_filled = np.mean(filled_pixels)
    assert mean_filled == pytest.approx(120.6, 0.05)
    assert filled.width == 1920
    # filled portrait
    filled = image.resized_ext(size=(1080, 1920), fill_area=True, keep_aspect=True)
    filled_pixels = filled.get_pixels()
    mean_filled = np.mean(filled_pixels)
    assert mean_filled == pytest.approx(120.6, 0.05)
    assert filled.width == 1080
    just_scaled = image.resized_ext(size=(600, 600))
    just_scaled_pixels = just_scaled.get_pixels()
    just_scaled_mean = np.mean(just_scaled_pixels)
    assert just_scaled_mean == pytest.approx(120, 0.05)
    scaled_aspect = image.resized_ext(target_aspect=16 / 9, factor=2.0)
    scaled_aspect = scaled_aspect.get_pixels()
    scaled_aspect_mean = np.mean(scaled_aspect)
    assert scaled_aspect_mean == pytest.approx(87.5, 0.05)
    # test exceptions
    try:
        image.resized_ext(size=(1080, 1920), fill_area=True, keep_aspect=False)
        assert False  # shouldn't be reached
    except ValueError:
        pass
    try:
        image.resized_ext(size=(1080, 1920), target_aspect=16 / 9)
        assert False  # shouldn't be reached
    except ValueError:
        pass
