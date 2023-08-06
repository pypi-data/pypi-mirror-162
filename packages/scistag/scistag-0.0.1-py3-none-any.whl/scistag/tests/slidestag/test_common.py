import pytest
from scistag.slidestag.slide_application_manager import SlideAppManager
from scistag.slidestag.slide_application import SlideApp
from scistag.slidestag.slide_session import SlideSession
import os


class TestSession(SlideSession):
    def __init__(self, config: dict):
        super().__init__(config)


class TestApp(SlideApp):
    app_instance = None
    APP_NAME = "TestApp"

    def __init__(self):
        super().__init__(self.APP_NAME, TestSession)


def log_image_data(name: str, data: bytes):
    """
    Logs an image to disk for manual review if $module_path/temp_test exists.
    :param name: The log filename
    :param data: The data
    """
    base_dir = os.path.normpath(os.path.dirname(__file__) + "/../../../temp_test")
    if os.path.exists(base_dir):
        with open(base_dir + "/" + name, "wb") as out_file:
            out_file.write(data)


@pytest.fixture(scope="module")
def slide_session():
    if not SlideAppManager.shared_app_manager.app_is_valid(TestApp.APP_NAME):
        TestApp.app_instance = TestApp()
        SlideAppManager.shared_app_manager.register_application(TestApp.app_instance)
    config = {
        SlideSession.SESSION_ID: None,
        SlideSession.REMOTE_SESSION: False
    }
    session = SlideAppManager.shared_app_manager.create_session(TestApp.APP_NAME, config)
    yield session


def test_application(slide_session):
    app: SlideApp = slide_session.app
    assert len(app.get_media_paths()) != 0
    assert app.session_class == TestSession
