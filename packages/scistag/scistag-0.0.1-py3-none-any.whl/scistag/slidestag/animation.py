from typing import Optional
import time


class Animation:
    """
    Defines a widget's animation from an initial to a target value
    """

    def __init__(self, name: str, start_value: float, target_value: float, duration_s: float,
                 start_time: Optional[float] = None):
        """
        Initializer
        :param name: The variable's name, e,g. "x", "y", "x2", "y2", "width", "height" or "alpha"
        :param start_value: The start value
        :param target_value: The target value
        :param duration_s: The duration in seconds
        :param start_time: The start time. If not defined the current time
        """
        self.name = name
        'The name of the variable to animate'
        self.start_value = start_value
        'The initial value'
        self.target_value = target_value
        'The target value'
        self.duration_s = duration_s
        'The duration'
        self.start_time = time.time() if start_time is None else start_time
