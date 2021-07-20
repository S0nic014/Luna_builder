from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2 import QtCore


class QLGraphicsSocket(QtWidgets.QGraphicsItem):
    def __init__(self, parent=None, color=QtGui.QColor("#FFFF7700")):
        super(QLGraphicsSocket, self).__init__(parent)

        self.radius = 6.0
        self.outline_width = 1.0
        self._color_background = color if isinstance(color, QtGui.QColor) else QtGui.QColor(color)
        self._color_outline = QtGui.QColor("#FF000000")

        # Pen, brush
        self._pen = QtGui.QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        self._brush = QtGui.QBrush(self._color_background)

    def paint(self, painter, option=None, widget=None):
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def boundingRect(self):
        return QtCore.QRectF(
            -self.radius - self.outline_width,
            -self.radius - self.outline_width,
            2 * (self.radius + self.outline_width),
            2 * (self.radius + self.outline_width)
        )
