import imp
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from luna import Logger
import luna.utils.enumFn as enumFn
import luna_builder.editor.graphics_socket as graphics_socket
imp.reload(graphics_socket)


class QLGraphicsView(QtWidgets.QGraphicsView):

    # Constant settings
    EDGE_DRAG_START_THRESHOLD = 10

    class EdgeMode(enumFn.Enum):
        NOOP = 1
        DRAG = 2

    def __init__(self, gr_scene, parent=None):
        super(QLGraphicsView, self).__init__(parent)

        self.gr_scene = gr_scene
        self.zoom_in_factor = 1.25
        self.zoom_clamp = False
        self.zoom = 10
        self.zoom_step = 1
        self.zoom_range = [0, 10]

        self.edge_mode = QLGraphicsView.EdgeMode.NOOP
        self.last_lmb_click_pos = None

        self.init_ui()
        self.setScene(self.gr_scene)

    def init_ui(self):
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.HighQualityAntialiasing | QtGui.QPainter.TextAntialiasing | QtGui.QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.middle_mouse_press(event)
        elif event.button() == QtCore.Qt.LeftButton:
            self.left_mouse_press(event)
        elif event.button() == QtCore.Qt.RightButton:
            self.right_mouse_press(event)
        else:
            super(QLGraphicsView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.middle_mouse_release(event)
        elif event.button() == QtCore.Qt.LeftButton:
            self.left_mouse_release(event)
        elif event.button() == QtCore.Qt.RightButton:
            self.right_mouse_release(event)
        else:
            super(QLGraphicsView, self).mouseReleaseEvent(event)

    def middle_mouse_press(self, event):
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        releaseEvent = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                         QtCore.Qt.LeftButton, QtCore.Qt.NoButton, event.modifiers())
        super(QLGraphicsView, self).mouseReleaseEvent(releaseEvent)
        fake_event = QtGui.QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                       QtCore.Qt.LeftButton, event.buttons() | QtCore.Qt.LeftButton, event.modifiers())
        super(QLGraphicsView, self).mousePressEvent(fake_event)

    def middle_mouse_release(self, event):
        fake_event = QtGui.QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                       QtCore.Qt.LeftButton, event.buttons() & ~QtCore.Qt.LeftButton, event.modifiers())
        super(QLGraphicsView, self).mouseReleaseEvent(fake_event)
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

    def left_mouse_press(self, event):

        item = self.get_item_at_click(event)
        # Store click position for future use
        self.last_lmb_click_pos = self.mapToScene(event.pos())

        # Handle socket click
        if isinstance(item, graphics_socket.QLGraphicsSocket):
            if self.edge_mode == QLGraphicsView.EdgeMode.NOOP:
                self.start_edge_drag(item)
                return

        if self.edge_mode == QLGraphicsView.EdgeMode.DRAG:
            result = self.end_edge_drag(item)
            if result:
                return

        super(QLGraphicsView, self).mousePressEvent(event)

    def left_mouse_release(self, event):
        item = self.get_item_at_click(event)

        if self.edge_mode == QLGraphicsView.EdgeMode.DRAG:
            if self.check_lmb_release_delta(event):
                result = self.end_edge_drag(item)
                if result:
                    return

        super(QLGraphicsView, self).mouseReleaseEvent(event)

    def right_mouse_press(self, event):
        super(QLGraphicsView, self).mousePressEvent(event)

    def right_mouse_release(self, event):
        super(QLGraphicsView, self).mouseReleaseEvent(event)

    def wheelEvent(self, event):
        # Calculate zoom vector
        zoom_out_factor = 1 / self.zoom_in_factor

        # Calculate zoom
        if event.angleDelta().y() > 0:
            zoom_factor = self.zoom_in_factor
            self.zoom += self.zoom_step
        else:
            zoom_factor = zoom_out_factor
            self.zoom -= self.zoom_step

        clamped = False
        if self.zoom < self.zoom_range[0]:
            self.zoom = self.zoom_range[0]
            clamped = True
        elif self.zoom > self.zoom_range[1]:
            self.zoom = self.zoom_range[1]
            clamped = True

        # Set scene scale
        if not clamped or self.zoom_clamp is False:
            self.scale(zoom_factor, zoom_factor)

    def get_item_at_click(self, event):
        """Object at click event position

        :param event: Mouse click event
        :type event: QMouseEvent
        :return: Item clicked
        :rtype: QtWidgets.QGraphicsItem
        """
        item = self.itemAt(event.pos())  # type: QtWidgets.QGraphicsItem
        return item

    def check_lmb_release_delta(self, event):
        """Measures if LMB release position is greater then distance threshold.

        :param event: Left mouse click event
        :type event: QMouseEvent
        :return: Distance between clicked release positions is greater than threshold
        :rtype: bool
        """
        # Check if mouse was moved far enough from start socket and handle release if true
        new_lmb_releas_scene_pos = self.mapToScene(event.pos())
        click_release_delta = new_lmb_releas_scene_pos - self.last_lmb_click_pos
        return (click_release_delta.x() ** 2 + click_release_delta.y() ** 2) > QLGraphicsView.EDGE_DRAG_START_THRESHOLD ** 2

    def start_edge_drag(self, clicked_item):
        self.edge_mode = QLGraphicsView.EdgeMode.DRAG
        Logger.debug('Start dragging edge: {}'.format(self.edge_mode))
        Logger.debug('Assign socket')

    def end_edge_drag(self, clicked_item):
        self.edge_mode = QLGraphicsView.EdgeMode.NOOP
        Logger.debug('End dragging edge')
        # Another socket clicked while dragging edge
        if isinstance(clicked_item, graphics_socket.QLGraphicsSocket):
            Logger.debug('Assign end socket')
            return True

        return False
