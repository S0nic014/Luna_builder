from PySide2 import QtWidgets


class QLGraphicsScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent=None):
        super(QLGraphicsScene, self).__init__(parent)
