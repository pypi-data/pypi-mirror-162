from widget import *


class Button(Widget):
    """
    A simple button control
    """

    def __init__(self, parent: Widget, parameters: dict):
        """
        Intitializer
        :param parent: The parent widget
        :param parameters: The creation parameters. See Widget. In addition:
        text: The button's text
        """
        super().__init__(parent, parameters)
        self.set_bounding(Bounding2D.from_pos_size(self.pos(), self.size()))

    def handle_paint(self, event: PaintEvent) -> bool:
        canvas = event.canvas
        canvas.rect(Bounding2D(pos_size=(0, 0, 0.0, self.width(), self.height())), color=Color(0, 0, 1.0))
        return super().handle_paint(event)
