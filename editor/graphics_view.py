from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets


class QLGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, gr_scene, parent=None):
        super(QLGraphicsView, self).__init__(parent)

        self.gr_scene = gr_scene
        self.zoom_in_factor = 1.25
        self.zoom_clamp = False
        self.zoom = 10
        self.zoom_step = 1
        self.zoom_range = [0, 10]

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
        return super(QLGraphicsView, self).mousePressEvent(event)

    def left_mouse_release(self, event):
        return super(QLGraphicsView, self).mouseReleaseEvent(event)

    def right_mouse_press(self, event):
        return super(QLGraphicsView, self).mousePressEvent(event)

    def right_mouse_release(self, event):
        return super(QLGraphicsView, self).mouseReleaseEvent(event)

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
