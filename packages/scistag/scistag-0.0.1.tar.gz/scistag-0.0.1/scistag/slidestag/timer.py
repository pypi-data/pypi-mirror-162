from typing import Optional
from .event import WidgetEvent


class TimerEvent(WidgetEvent):
    """
    A timer event
    """
    def __init__(self, timer: 'Timer', prev_time: float, new_time: float):
        """
        Initializer
        :param timer: The timer which triggered the event
        :param prev_time: The previous execution time
        :param new_time: This execution time
        """
        super().__init__()
        self.timer = timer
        self.prev_time: Optional[float] = prev_time
        self.new_time = new_time


class Timer:
    """
    Defines a timer instance which is triggered in definable intervals
    """

    def __init__(self, widget: 'Widget', interval_s: float = 1.0, repeat: bool = True, pause_on_unload=True):
        self._widget = widget
        "The owning widget"

        self._interval_s = interval_s
        "The execution interval in seconds"

        self._prev_time: float = 0.0
        """
        The previous execution time
        """

        self._pause_on_unload = True
        "Timer pauses when the owning widget is unloaded"

        self.next_turn: float = 0.0
        "Time when the next event shall be triggered"

        self._repeat = False
        "Defines if the event shall be repeated"

        self._paused = False
        "Defines if the timer is currently paused, e.g. because a parent view did unload"

    def pause(self):
        """
        Pauses the timer
        """
        self._paused = True

    def unpause(self):
        """
        Unpauses the timer
        """
        self._paused = False

    def callback(self, timer):
        """
        The callback function executed

        :apram timer: The timer which was the target of this event call (matches self)
        """
        prev_time = self._prev_time
        self._widget.handle_timer()