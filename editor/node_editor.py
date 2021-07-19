import imp
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
import luna_builder.editor.graphics_scene as graphics_scene
import luna_builder.editor.graphics_view as graphics_view

imp.reload(graphics_scene)
imp.reload(graphics_view)


class NodeEditor(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(NodeEditor, self).__init__(parent)
        self.init_ui()
        self.add_debug_content()

    def init_ui(self):
        self.setMinimumSize(200, 500)
        self.create_widgets()
        self.create_layouts()
        self.create_conections()

    def create_widgets(self):
        # Graphics scene
        self.gr_scene = graphics_scene.QLGraphicsScene()

        # Graphics view
        self.gr_view = graphics_view.QLGraphicsView(self.gr_scene, self)

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.gr_view)

    def create_conections(self):
        pass

    def add_debug_content(self):
        brush_green = QtGui.QBrush(QtCore.Qt.green)
        outline_pen = QtGui.QPen(QtCore.Qt.black)
        outline_pen.setWidth(2)

        rect = self.gr_scene.addRect(-100, -100, 80, 100, outline_pen, brush_green)  # type: QtWidgets.QGraphicsRectItem
        rect.setFlag(rect.ItemIsMovable)
        text = self.gr_scene.addText('Debug text')  # type: QtWidgets.QGraphicsTextItem
        text.setFlag(text.ItemIsMovable)
        widget1 = QtWidgets.QPushButton('Debug button')
        proxy1 = self.gr_scene.addWidget(widget1)  # type: QtWidgets.QGraphicsProxyWidget
        proxy1.setPos(0, 40)
        line = self.gr_scene.addLine(-200, -100, 400, 200, outline_pen)  # type: QtWidgets.QGraphicsLineItem
        line.setFlag(line.ItemIsMovable)
