from typing import Optional
from .widget import *
from .slide_manager import SlideManager
from .base_events import TapEvent
import random

from ..common.local_var_cache import LocalVariableCache


class Slide(Widget):
    """
    Represents a slide (or a screen) currently being visualized
    """

    SLIDE_NAME = "slideName"
    BACKGROUND_IMAGE = "backgroundImage"

    SLIDE_FLAG_NEEDS_USER_CAMERA = "NeedsCamera"
    "Defines in the slide_flags if access to the user camera is desired"

    def __init__(self, slide_manager: SlideManager, parameters: dict = None) -> None:
        """
        Initializes
        :param slide_manager: The parent view managing this slide
        :param parameters:
            "slideName" The slide's name
            "backgroundImage" The slide's background image
        """
        parameters = {} if parameters is None else parameters
        parameters['visible'] = False
        super().__init__(slide_manager, parameters)
        self._slide_name = parameters.get(self.SLIDE_NAME, str(random.randint(0, 2 ** 32)))
        self._ui_loaded = False
        self.background_image_name = parameters.get(self.BACKGROUND_IMAGE, "")
        self.background_image = None  # The background image
        self.breakpoints = []  # List of breakpoints in this slide
        self.slide_flags = {}
        "Defines the requirements of the current slide"
        self.auto_repaint_frequency = 0.0
        "Defines the frequency with which this slide automatically repaints itself, e.g if you have an animated" \
        "presentation."

    def get_manager(self) -> Optional[SlideManager]:
        """
        Returns this slide's manager if we are attached ot one
        :return: The manager
        """
        if self._parent is not None and isinstance(self._parent, SlideManager):
            return self._parent
        return None

    def add_breakpoint(self):
        """
        Adds a breakpoint to this slide (work in progress). When no start slide is explicitly defined the first slide
        with a breakpoint will be selected.
        """
        self.breakpoints.append("breakpoint")

    def get_name(self) -> str:
        """
        The slide's name
        """
        return self._slide_name

    def handle_load(self) -> bool:
        """
        Is called when the slide is loaded
        """
        return True

    def handle_load_ui(self, canvas: Canvas) -> bool:
        """
        Is called when the UI becomes visible the first time after an unload
        :return:
        """
        self._ui_loaded = True
        if self.background_image_name != "":
            self.background_image = canvas.load_image(self.background_image_name, cache=False)
        return True

    def handle_unload(self) -> bool:
        """
        Is called when the slide is unloaded
        """
        self._ui_loaded = False
        self.background_image = None
        return True

    def handle_click(self, event: TapEvent) -> bool:
        if not super().handle_click(event):
            return False
        if event.coordinate[0] >= self.width() - self.width() // 4:
            self.get_manager().go_next(current=self)
        elif event.coordinate[0] <= self.width() // 4:
            self.get_manager().go_last(current=self)
        return True

    def handle_paint(self, event: PaintEvent) -> bool:
        if not self._ui_loaded:
            self.handle_load_ui(event.canvas)
        canvas = event.canvas
        theme = self.get_theme()
        if self.background_image is None:
            canvas.rect(Bounding2D(pos_size=(0.0, 0.0, self.width(), self.height())), color=theme.slide_background,
                        outline=Color(0, 0, 0), outline_width=0)
        else:
            canvas.draw_image(self.background_image, (0, 0))
        return super().handle_paint(event)
