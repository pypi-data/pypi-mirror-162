from typing import Tuple, Optional, Union, List, Callable, Any
from .alignment import Alignment, RegionAlignment, AlignmentSide
from scistag.imagestag.canvas import *
from scistag.imagestag.canvas import __all__ as all_canvas
from .slide_theme import Theme
from .base_events import *
from .animation import Animation
from ..common.local_var_cache import LocalVariableCache

# Widget creation parameters
WIDGET_X = "x"
"X position"
WIDGET_Y = "y"
"Y position"
WIDGET_WIDTH = "width"
"Initial width"
WIDGET_HEIGHT = "height"
"Initial height"
WIDGET_VISIBLE = "visible"
"Visibility"
WIDGET_ALIGNMENT = "alignment"
"Alignment"


class Widget:
    """
    Widget is the base class for visual controls.
    """

    def __init__(self, parent: Optional['Widget'], parameters: dict):
        """
        Initializer
        :param parent: The parent widget
        :param parameters: The creation parameters
        """
        # the widget's precise bounding, for sub pixel precise rendering
        pos = Pos2D(parameters.get(WIDGET_X, 0.0), parameters.get(WIDGET_Y, 0.0))
        self._bounding = Bounding2D(ul=pos,
                                    lr=Pos2D(parameters.get("width", 100.0) + pos.x,
                                             parameters.get("height", 100.0) + pos.y))
        self._parent: Optional['Widget'] = None
        "The widget's parent"
        self.temp_cache = LocalVariableCache()
        "A temporary cache. It will be cleared upon unloading of the widget (after the execution of handle_unload).\
        Usage: slide.cache('myData', lambda: pd.read_csv('myData.csv'))"
        self.int_bounding: List[int] = []
        "The views bounding in integer coordinates"
        self._dpi_scaling = 1.0
        self._session = parent.get_session() if parent is not None else None
        self._theme = Theme(scaling=self._dpi_scaling)
        self._loaded = False
        "The scaling factor which should be applied to all painting operations. See scale function"
        self._visible: bool = parameters.get(WIDGET_VISIBLE, True)
        "Defines if the view is visible"
        self.sensitive = True
        "Defines if this element can catch clicks or is just an overlay"
        self._alpha: float = 1.0
        "The view's alpha value (1.0 = 100% opaque)"
        self.animations: List[Animation] = []
        "Animations currently in progress"
        self._children = []
        "List of all children"
        self._visible_children = []
        "List of all visible children"
        self._auto_unload = False
        "Defines if the item shall automatically be unloaded"
        if parent is not None:
            parent.add_widget(self)
        self._layout_update_required = True
        "FLag is an internal relayouting is required"
        self._alignment: Optional[Alignment] = parameters.get(WIDGET_ALIGNMENT, None)
        "The view's alignment, e.g. RegionAlignment or AnchorAlignment"
        self.on_paint = WidgetEventHandler(event_class=PaintEvent)
        "The paint event is triggered when ever the view shall be visualized"
        self.on_click = WidgetEventHandler(event_class=TapEvent)
        self._update_int_bounding()

    def get_theme(self) -> 'Theme':
        """
        Returns the theme
        :return: The theme
        """
        return self._theme

    def get_session(self) -> 'SlideSession':
        """
        Returns the session handle
        :return: The session
        """
        return self._session

    def auto_unload(self) -> "Widget":
        """
        Flags the widget that it shall be auto destructed when it's parents handle_unload is called and that
        it's parents member variable pointing to it shall get set to None.
        :return: The widget
        """
        self._auto_unload = True
        return self

    def handle_paint(self, event: PaintEvent) -> bool:
        """
        Is called when ever the view shall be painted
        :param event: The event
        :return: True if the execution shall continue
        """
        if not self.on_paint.execute(event):
            return False
        return True

    def handle_click(self, event: TapEvent) -> bool:
        """
        Is called when a mouse click or touch is executed
        :param event: The event
        :return: True if the execution shall continue
        """
        if not self.on_click.execute(event):
            return False
        return True

    def handle_load(self) -> bool:
        """
        Called when the widget becomes visible and shall be loaded

        :return: If it's true the view shall be loaded
        """
        prev = self._loaded
        if prev:
            return False
        self._loaded = True
        for element in self._visible_children:  # reload all now visible children
            element: 'Widget'
            element.handle_load()

    def handle_unload(self) -> bool:
        """
        Called when the widget becomes invisible and shall be unloaded

        :return: The previous state. If it's fall the unload can be skipped
        """
        prev = self._loaded
        self._loaded = False
        widgets_to_remove = []
        for key, item in self.__dict__.items():
            if item is not None and isinstance(item, Widget):
                item: Widget
                if item._auto_unload:
                    widgets_to_remove.append(item)
        for rem_element in widgets_to_remove:
            self.__dict__[rem_element[0]] = None  # remove link
            self.remove_widget(rem_element[1])  # remove widget

        for element in self._visible_children:  # reload all now visible children
            element: 'Widget'
            element.handle_unload()
        return prev

    def add_widget(self, child: 'Widget'):
        """
        Registers a child widget
        :param child: The new child
        """
        self.repaint()
        if child._parent is not None:
            raise Exception("The widget already has a parent")
        child._dpi_scaling = self._dpi_scaling
        child._theme = self._theme
        child._session = self._session
        child._parent = self
        self._children.append(child)
        if child._visible:
            self._visible_children.append(child)
            self._layout_update_required = True
            child.handle_load()

    def remove_widget(self, child: 'Widget') -> bool:
        """
        Removes a child widget
        :param child: The child to be removed
        :return: True if the child was found
        """
        self.repaint()
        self._layout_update_required = True
        found = False
        if child in self._children:
            found = True
            self._children.remove(child)
        if child in self._visible_children:
            self._visible_children.remove(child)
            child.handle_unload()
        child._parent = None
        return found

    def set_bounding(self, bounding: Bounding2D, _from_animation: bool = False):
        """
        Upates the widget's bounding in float (precise) coordinates
        :param bounding: The new bounding
        """
        if not _from_animation and len(self.animations):
            self.cancel_animations(['x', 'y', 'x2', 'y2', 'width', 'height'])
        old_bounding = self._bounding
        self._bounding = bounding.copy()
        self._update_int_bounding()
        self._layout_update_required = old_bounding.size() != self._bounding.size()
        if old_bounding != self._bounding:
            self.repaint()

    def get_bounding(self) -> Bounding2D:
        """
        Returns the widget's precise bounding
        :return: The bounding with floating point precision
        """
        return self._bounding

    def set_size(self, size: Union[Size2D, tuple], _from_animation: bool = False):
        """
        Sets the view's size
        :param size: The new size in pixels
        :param _from_animation: True if called from an animation (and shall not cancel it)
        :return:
        """
        if not _from_animation and len(self.animations):
            self.cancel_animations(['x2', 'y2', 'width', 'height'])
        self.set_bounding(Bounding2D.from_pos_size(self.pos(), size), _from_animation=_from_animation)

    def set_alignment(self, alignment: Optional[Alignment]):
        """
        Modifies the child's alignment to enable to automatically adjust size and position when the parent or a
        neighbour widget is resized.
        :param alignment: The new alignment
        """
        self._alignment = alignment
        if self._parent is not None:
            self._parent.request_layout_update()

    def get_alignment(self) -> Optional[Alignment]:
        """
        Returns the child's alignment
        :return: See Alignment
        """
        return self._alignment

    def set_visible(self, state: bool = True, _from_animation: bool = False):
        """
        Defines the new visibility state
        :param state: The new state
        :param _from_animation: True if called from an animation (and shall not cancel it)
        """
        if not _from_animation and len(self.animations) != 0:
            self.cancel_animations(["alpha"])
        if self._visible == state:
            return
        self._visible = state
        self.repaint()
        if self._parent is not None:
            self._parent._handle_visibility_changed(self)

    def get_visible(self) -> bool:
        """
        Returns the visibility state
        :return: True if visible
        """
        return self._visible

    def set_alpha(self, alpha: float, _from_animation: bool = False):
        """
        Sets a new alpha value
        :param alpha: The new alpha value
        :param _from_animation: True if called from an animation (and shall not cancel it)
        """
        if not _from_animation and len(self.animations) != 0:
            self.cancel_animations(["alpha"])
        if self._alpha == 0.0 and self._visible:
            self.set_visible(False, _from_animation=_from_animation)
        if self._alpha > 0.0 and not self._visible:
            self.set_visible(True, _from_animation=_from_animation)
        if self._alpha == alpha:
            return
        self.repaint()
        self._alpha = alpha

    @property
    def alpha(self) -> float:
        """
        Returns the curent alpha value
        :return: The alpha value
        """
        return self._alpha

    def to_top(self, child: "Widget"):
        """
        Moves this view to the top of the view hierarchy
        :param child: The child to move to the top
        """
        if child in self._visible_children:
            self._visible_children.remove(child)
            self._visible_children.append(child)
        self._children.remove(child)
        self._children.append(child)

    def to_bottom(self, child: "Widget"):
        """
        Moves this view to the bottom of the view hierarchy
        :param child: The child to move to the bottom
        """
        if child in self._visible_children:
            self._visible_children.remove(child)
            self._visible_children.insert(0, child)
        self._children.remove(child)
        self._children.insert(0, child)

    def cancel_animations(self, names: List[str]):
        """
        Cancels all animations affecting given properties
        :param names: The list of names, e.g. "x" or "alpha"
        """
        remove_list: List[Animation] = []
        for anim in self.animations:
            if anim.name in names:
                remove_list.append(anim)
        for anim in remove_list:
            self.animations.remove(anim)

    def _handle_visibility_changed(self, child: 'SlideWidget'):
        """
        Called when a child's visibility state has changed
        :param child: The element
        """
        if not child.get_visible():
            if child in self._visible_children:
                self._visible_children.remove(child)
            child.handle_unload()
            child.temp_cache.clear()
        else:
            if child not in self._visible_children:
                self._visible_children.append(child)
            child.handle_load()
        if child.get_alignment() is not None:
            self._layout_update_required = True

    def request_layout_update(self):
        """
        Called when the layout shall be recalculated at the next painting cycle
        :param child: The element
        """
        self._layout_update_required = True

    def size(self) -> (int, int):
        """
        Return's the widget's size in pixels
        :return: The size in pixels
        """
        return tuple(self.int_bounding[2:])

    def width(self) -> int:
        """
        Return's the widget's width in pixels
        :return: The size in pixels
        """
        return self.int_bounding[2]

    def height(self) -> int:
        """
        Return's the widget's height in pixels
        :return: The size in pixels
        """
        return self.int_bounding[3]

    def pos_precise(self) -> Pos2D:
        """
        Return's the widget's position in pixels
        :return: The position
        """
        return self._bounding.pos()

    def pos(self) -> (int, int):
        """
        Return's the widget's position in pixels
        :return: The position
        """
        return tuple(self.int_bounding[0:2])

    def scale(self, value: Union[int, float, tuple]):
        """
        Computes the scaled base (point) size converted to effective pixel size for this element
        :param value: The size value, e.g. a base font size
        :return: The optimum size for this view
        """
        if isinstance(value, tuple):
            tuple([int(round(element * self._dpi_scaling)) for element in value])
        return int(round(value * self._dpi_scaling))

    def get_relative_coordinate(self, coordinate) -> Optional[Tuple["Widget", float, float]]:
        """
        Receives the widget hit and the coordinates within the widget
        :param coordinate: The relative coordinate
        :return: None if no widget was hit, otherwise Widget, RelativeX, Relative Y
        """
        coord = [coordinate[0], coordinate[1]]
        if coord[0] < 0 or coord[1] < 0 or coord[0] > self.width() or coord[1] > self.height():
            return None
        for child in reversed(self._visible_children):  # prefer child covering us
            child: Widget
            child_coord = child.get_bounding()
            relative_coordinate = [coord[0] - child_coord.ul.x, coord[1] - child_coord.ul.y]
            result = child.get_relative_coordinate(relative_coordinate)
            if result is not None:
                return result
        if not self.sensitive:  # skip if it can not be clicked itself
            return None
        return self, coord[0], coord[1]

    def repaint(self):
        """
        Flags the view that a repaint is required
        """
        pass

    def _invalidate_layout(self):
        """
        Flags the view that an update is required
        """
        self._layout_update_required = True

    @staticmethod
    def _chop_alignment(widget: 'Widget', alignment_type, client_region: Bounding2D) -> (
            Bounding2D, Bounding2D):
        """
        Helper function to subdivide the (initially) full client region of a view into slices defined by the
        children's RegionAlignemnt type. (LEFT, RIGHT, TOP etc.)
        :param widget: The widget
        :param alignment_type: The alignment type
        :param client_region: The remaining available client region
        :return: Widget's region, Remaining client region
        """
        size = widget.size()
        if alignment_type == AlignmentSide.LEFT:  # widget's width, client's height
            bounding = Bounding2D.from_pos_size(client_region.pos(), Size2D(size[0], client_region.size().height))
            client_region.ul.x = min(client_region.ul.x + size[0], client_region.lr.x)
        elif alignment_type == AlignmentSide.RIGHT:  # widget's width, client's height, starting from right
            bounding = Bounding2D.from_xy_wh(client_region.lr.x - size[0], client_region.ul.y,
                                             size[0], client_region.size().height)
            client_region.lr.x = max(client_region.lr.x - size[0], 0.0)
        elif alignment_type == AlignmentSide.TOP:  # widget's width, client's height
            bounding = Bounding2D.from_pos_size(client_region.pos(), Size2D(client_region.size().width, size[1]))
            client_region.ul.y = min(client_region.ul.y + size[1], client_region.lr.y)
        elif alignment_type == AlignmentSide.BOTTOM:  # widget's width, client's height, starting from right
            bounding = Bounding2D.from_xy_wh(client_region.ul.x, client_region.lr.y - size[1],
                                             client_region.size().width, size[1])
            client_region.lr.y = max(client_region.lr.y - size[1], 0.0)
        else:
            bounding = client_region.copy()

        return bounding, client_region

    def update_layout(self):
        """
        Updates the view's layout recursive
        """
        if self._layout_update_required:
            self._update_region_alignments()
        for child in self._children:
            child: Widget
            child.update_layout()

    def _update_region_alignments(self):
        """
        Updates the position of children using region alignments
        """
        self._layout_update_required = False
        size = self.size()
        client_area = Bounding2D.from_xy_wh(0.0, 0.0, size[0], size[1])  # The client (remaining) area
        for child in self._visible_children:
            child: Widget
            if child._alignment is not None and isinstance(child._alignment, RegionAlignment):
                alignment: RegionAlignment = child._alignment
                if alignment.alignment == AlignmentSide.CLIENT or alignment.alignment == AlignmentSide.NONE:
                    continue
                bounding, client_area = self._chop_alignment(child, alignment.alignment, client_area.copy())
                child.set_bounding(client_area)
        for child in self._visible_children:
            child: Widget
            if child._alignment is not None and isinstance(child._alignment, RegionAlignment):
                alignment: RegionAlignment = child._alignment
                if alignment.alignment == AlignmentSide.CLIENT:
                    child.set_bounding(client_area)

    def _update_int_bounding(self):
        """
        Update the widget's coarse bounding
        """
        size = self._bounding.size()
        self.int_bounding = [int(round(self._bounding.ul.x)),
                             int(round(self._bounding.ul.y)),
                             int(round(size.width)),
                             int(round(size.height))]

    def paint_recursive(self, paint_event: PaintEvent):
        """
        Paints the view hierarchy recursive
        :param paint_event: The repaint event
        """
        self.handle_paint(paint_event)
        canvas = paint_event.canvas
        for child in self._visible_children:
            child: Widget
            canvas.push_state()
            canvas.shift_offset(child.pos())
            child.paint_recursive(paint_event)
            canvas.pop_state()

    def paint_recursive_int(self, canvas: Canvas, config: dict):
        """
        Triggers an recursive repaint
        :param canvas: The target canvas
        :param config: Advanced rendering settings
        """
        paint_event = PaintEvent(widget=self, canvas=canvas, config=config)
        self.paint_recursive(paint_event)

    def cache_data(self, identifier: str, builder: Callable[[object], Any],
                   parameters: Optional[object] = None) -> Any:
        """
        Tries to retrieve given element from cache. If the element is not stored in the cache it will be created
        using the builder callback which should await a single parameter and return a single value.
        If parameters (optional) is passed it will be verified if the parameters were modified.
        :param identifier: The identifier. Either a string or a dictionary with a configuration.
        :param builder: The function to call if the value does not exist
        :param parameters: If the data may dynamically change using the same identifier, pass it too
        :return: The data
        """
        return self.temp_cache.cache(identifier=identifier, builder=builder, parameters=parameters)


__all__ = ["Widget", "PaintEvent", "WIDGET_X", "WIDGET_Y", "WIDGET_WIDTH", "WIDGET_HEIGHT", "WIDGET_ALIGNMENT",
           "WIDGET_VISIBLE"] + all_canvas
