import imp
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

import luna_builder.editor.node_scene as node_scene
import luna_builder.editor.node_node as node_node
import luna_builder.editor.node_socket as node_socket
import luna_builder.editor.node_edge as node_edge
import luna_builder.editor.graphics_view as graphics_view
imp.reload(node_scene)
imp.reload(node_node)
imp.reload(node_socket)
imp.reload(node_edge)
imp.reload(graphics_view)


class NodeEditor(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(NodeEditor, self).__init__(parent)
        self.init_ui()
        self.add_debug_nodes()

    def init_ui(self):
        self.setMinimumSize(200, 500)
        self.create_widgets()
        self.create_layouts()
        self.create_conections()

    def create_widgets(self):
        # Graphics scene
        self.scene = node_scene.Scene()

        # Graphics view
        self.gr_view = graphics_view.QLGraphicsView(self.scene.gr_scene, self)

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.gr_view)

    def create_conections(self):
        pass

    def add_debug_nodes(self):
        # Test nodes
        node1 = node_node.Node(self.scene, inputs=[1, 1, 1], outputs=[2, 2, 2])
        node2 = node_node.Node(self.scene, inputs=[2, 2, 2], outputs=[3, 3, 3])
        node3 = node_node.Node(self.scene, inputs=[3, 3, 3], outputs=[1, 1, 1])
        node1.set_position(-350, -250)
        node2.set_position(-75, 0)
        node3.set_position(200, -150)

        edge1 = node_edge.Edge(self.scene, node1.outputs[0], node2.inputs[0])
        edge2 = node_edge.Edge(self.scene, node2.outputs[0], node3.inputs[0])
