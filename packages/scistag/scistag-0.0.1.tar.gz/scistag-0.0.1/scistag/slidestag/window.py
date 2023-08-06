from .widget import Widget
from typing import Optional


class Window(Widget):
    """
    Defines a base window. In browser mode this window just exists virtually. In difference to all other Widgets
    the parent does not have usually any parent elements but defines the root of this tree.
    """

    def __init__(self, session: 'SlideSession', parameters: dict, parent: Optional[Widget] = None):
        """
        Initializer
        :param session: The window's session
        :param parameters: The creation parameters
        :param parent: The parent element. Can be
        """
        super().__init__(parent=parent, parameters=parameters)
        self._session = session
