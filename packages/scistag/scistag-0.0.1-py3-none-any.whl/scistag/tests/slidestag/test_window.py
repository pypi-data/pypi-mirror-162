from scistag.tests.slidestag.test_common import slide_session, log_image_data
from scistag.slidestag.slide_session import SlideSession
import os


def test_window(slide_session: SlideSession):
    config = {}
    view_data = slide_session.render_and_compress(config=config)
    log_image_data("test_window.jpg", view_data)
