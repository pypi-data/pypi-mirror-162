import json
import os.path
import time

from typing import Optional, List, Callable, Dict, Union
import io
from scistag.imagestag.canvas import *
from scistag.remotestag import Session
from .window import Window
from .slide_manager import SlideManager
from .alignment import RegionAlignment, AlignmentSide
from .event_router import EventRouter

MainLoopHookCallback = Callable[['Timer'], None]
"Type definitions for functions which can register as callback"

SLIDE_BASE_DPI = 96.0
"The base DPI value for a 1.0 size scaling"


class SlideSession(Session):
    """
    Represents a single user slide ui session
    """

    USER_DATA_CAMERA_BASE_NAME = "camera_"
    "User data providing a new camera image. The assumed data type is a compressed image."
    USER_DATA_CLIENT_EVENTS = "clientEvents"
    "A list of user events either as bytes or list of dicts. See EventRouter for supported events."

    PERMISSION_INPUT = "userInput"
    "Permission config field for user input (bool)"
    PERMISSION_WEBCAM = "webcam"
    "Permission config field for webcam access (bool)"

    def __init__(self, config: dict) -> None:
        """
        Initializer

        :param config: The session's configuration
        """
        super().__init__(config)
        self.title = ""
        "The session's title"
        self.resolution = (1920, 1080)
        "The window's resolution (including additional controls)"
        self.slide_resolution = (1920, 1080)
        "The presentation's resolution"
        self.dpi = SLIDE_BASE_DPI
        "The slide sessions DPI."
        self.is_remote_session = config.get(Session.REMOTE_SESSION, False)
        "Defines if this is a remote session and streaming the data, e.g. to a browser and from a remote input and cam"
        self.background_color = (255, 255, 255)  # The default background color
        "The default background fill color"
        self.stream_compression = 80
        "Image quality of the stream. Only effects remote clients, e.g. via browser or tablet"
        self.max_camera_index = 10
        "The maximum count of user cameras"
        self.camera_timeout = 0.25
        "The time when the last user image was requested"
        self.session_timeout = 30.0
        "Let the camera timeout after 30 seconds without communication"
        self.stream_filetype = ".jpg"
        "The image compression for remote streams"
        self.stream_mimetype = "image/jpeg"
        "The mime type  for remote streams"
        self.input_support = True
        "Defines if the session shall support user input"
        self.camera_support = False
        "Defines if the session shall support the camera"
        self.media_paths: List[str] = []
        "List of user specific media paths in which e.g. images and fonts shall be searched"
        self._root_window: Optional[Window] = None
        "The root window"
        self._slide_manager: Optional[SlideManager] = None
        "The slide manager (screen manager)"
        self.last_main_loop_time = time.time()
        "Time of the last main loop execution"
        self._main_loop_hooks: Dict['Timer', MainLoopHookCallback] = {}
        "Main loop hooks"
        self._event_router = EventRouter(self)
        "The event handler"

    def get_slide_manager(self) -> Optional[SlideManager]:
        """
        The slide manager
        :return: The instace
        """
        return self._slide_manager

    def get_root_window(self) -> Optional[Window]:
        """
        Returns the route window
        :return: The root window once it was created
        """
        return self._root_window

    def build(self):
        """
        Builds this session's UI, by default consisting of a window and a slide manager
        """
        self.update_config()
        window_parameters = {'width': self.resolution[0], 'height': self.resolution[1]}
        self._root_window = Window(session=self, parameters=window_parameters)
        slider_parameters = {'width': self.resolution[0], 'height': self.resolution[1],
                             'alignment': RegionAlignment(AlignmentSide.CLIENT)}
        self._slide_manager = SlideManager(parent=self._root_window, parameters=slider_parameters)

    def run(self):
        """
        Is called once the UI is constructed and the interaction which the user starts
        """
        pass

    def update_config(self) -> dict:
        """
        Returns the current configuration
        :return: The configuration
        """
        self._config = super().update_config()
        self._config[SlideSession.PERMISSIONS][SlideSession.PERMISSION_WEBCAM] = self.camera_support
        self._config[SlideSession.PERMISSIONS][SlideSession.PERMISSION_INPUT] = self.input_support
        return self._config

    def add_media_path(self, path: str):
        """
        Adds a new media path
        :param path: The path in which to search for images and fonts
        """
        self.media_paths.append(path)

    def get_media_paths(self) -> []:
        """
        Returns a list of all media paths
        :return: A list of all registered media directories
        """
        paths = []
        if self.app is not None:
            paths += self.app.get_media_paths()
        paths += self.media_paths
        return paths

    def find_file(self, filename: str) -> Optional[str]:
        """
        Tries to find a file in the registered media paths
        :param filename: The relative filename
        :return: The absolute file name if the file was found, otherwise None
        """
        for path in reversed(self.media_paths):
            cur_fn = os.path.normpath(path + "/" + filename)
            if os.path.exists(cur_fn):
                return cur_fn
        return None

    def add_guest_session(self):
        """
        Adds a guest session so a link for a guest can be shared
        """
        if self.guest_id is not None:
            return
        from scistag.remotestag.session_handler import SessionHandler
        self.guest_id = SessionHandler.create_session_id()

    def handle_main_loop(self):
        """
        Execute all main loop hooks
        :return:
        """
        for key, value in self._main_loop_hooks.items():  # TODO Missing timer implementation
            value(key)

    def handle_user_data(self, user_data_name: str, data: Union[bytes, list]):
        """
        Handle the user's data received from a remote source such as the browser.
        :param user_data_name: The data's identifier
        :param data: The data to be set or handled.
        :return: True if the data shall not be stored in the vault
        """
        handled = super().handle_user_data(user_data_name, data)
        if handled:
            return
        if user_data_name == self.USER_DATA_CLIENT_EVENTS:
            events = json.load(io.BytesIO(data)) if isinstance(data, bytes) else data
            self._event_router.handle_raw_events(events)
            return True
        return False

    def render_and_compress(self, config):
        """
        Renders the current session's views and returns a byte stream to their data

        :param config: The rendering configuration
        :return: Byte object containing the scene image's data
        """
        canvas = self._render_int(config)
        data = self.compress(canvas)
        return data

    def render_to_pil(self, config):
        """
        Renders the current session's views and returns a byte stream to their data

        :param config: The rendering configuration
        :return: The pillow image handle
        """
        canvas = self._render_int(config)
        data = canvas.get_image_handle()
        return data

    def _render_int(self, config) -> Canvas:
        """
        Creates a canvas with the current target resolution and renders all content to it via render

        :param config: The rendering configuration
        :return: An image of the current scene
        """
        width, height = self.resolution
        canvas = Canvas(width, height, media_paths=self.get_media_paths(), framework=ImsFramework.PIL,
                        default_color=self.background_color)
        self._root_window.update_layout()
        self.render(canvas, config)
        return canvas

    def get_user_camera_name(self, index: int) -> Optional[str]:
        """
        Returns the user camera's name at given index
        :param index: The camera index
        :return: The camera's identifier if a camera is available or was at least request (in case of a remote session)
        """
        if self.is_remote_session:
            if self.camera_support:
                return self.user_data_root_path + self.USER_DATA_CAMERA_BASE_NAME + f"{index:02d}"
            else:
                return None
        else:
            from scistag.mediastag import VideoSourceCamera
            return VideoSourceCamera.get_local_camera(index)

    def get_needs_camera(self) -> bool:
        """
        Returns if the user's camera is currently being used
        :return: True if the camera data is used
        """
        from scistag.slidestag.slide import Slide
        if self._slide_manager.get_current() is not None:
            return self._slide_manager.get_current().slide_flags.get(Slide.SLIDE_FLAG_NEEDS_USER_CAMERA, False)
        return False

    def render(self, canvas: Canvas, config: dict):
        """
        Returns the sessions data to the target canvas and returns it as np array

        :param canvas: The target canvas
        :param config: The rendering config
        """
        self._root_window.paint_recursive_int(canvas, config)

    def compress(self, canvas: Canvas) -> bytes:
        """
        Compresses the image using the defined streaming file type and compression grade

        :param canvas: The canvas' to convert to an image
        :return The byte stream of the image in the target format
        """
        ret = canvas.compress(self.stream_filetype, self.stream_compression)
        return ret

    def handle_load(self):
        """
        Is called right after the constructor and before the build call
        :return:
        """
        super().handle_load()

    def handle_unload(self):
        """
        Called when the application shall unload it's data
        """
        self._root_window.set_visible(False)
        self._root_window.remove_widget(self._slide_manager)
        super().handle_unload()
