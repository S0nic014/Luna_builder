from PySide2 import QtWidgets
import luna_builder.editor.node_graphics_scene as node_graphics_scene


class NodeEditor(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(NodeEditor, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setMinimumSize(200, 500)
        self.create_widgets()
        self.create_layouts()
        self.create_conections()

    def create_widgets(self):
        # Graphics scene
        self.gr_scene = node_graphics_scene.QLGraphicsScene()

        # Graphics view
        self.gr_view = QtWidgets.QGraphicsView()
        self.gr_view.setScene(self.gr_scene)

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.gr_view)

    def create_conections(self):
        pass
