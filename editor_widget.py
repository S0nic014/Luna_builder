from PySide2 import QtWidgets
from PySide2 import QtGui

# from luna_builder.rig_editor.node_scene import Scene
import luna_builder.graphics_view as graphics_view
import luna_builder.node_scene as node_scene
import luna_builder.attribs_widget as attribs_widget


class RigEditorWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(RigEditorWidget, self).__init__(parent)

        self.init_ui()

    def init_ui(self):
        # self.setGeometry(200, 200, 800, 600)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.attribs_wgt = None  # type: attribs_widget.AttributesWidget

        # Creation
        self._create_actions()
        self._create_widgets()
        self._create_layouts()
        self._create_connections()

        # Display
        self.setWindowTitle("Node editor")
        self.show()

        # self.add_nodes()

    def _create_actions(self):
        pass

    def _create_widgets(self):
        self.scene = node_scene.Scene()
        self.gr_scene = self.scene.gr_scene

        self.view = graphics_view.QDGraphicsView(self.gr_scene, self)
        self.view.setScene(self.gr_scene)

    def _create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.view)

    def _create_connections(self):
        pass
