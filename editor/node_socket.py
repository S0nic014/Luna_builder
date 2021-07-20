import imp
from PySide2 import QtGui
import luna.utils.enumFn as enumFn
import luna_builder.editor.graphics_socket as graphics_socket
imp.reload(graphics_socket)


class Socket():

    class Position(enumFn.Enum):
        LEFT_TOP = 1
        LEFT_BOTTOM = 2
        RIGHT_TOP = 3
        RIGHT_BOTTOM = 4

    # TODO: Class per socket type
    class DataType(enumFn.Enum):
        NUMERIC = 1
        STRING = 2
        COMPONENT = 3

    DATA_COLORS = {DataType.NUMERIC: QtGui.QColor("#FFFF7700"),
                   DataType.STRING: QtGui.QColor("#FF52e220"),
                   DataType.COMPONENT: QtGui.QColor("#FF0056a6")}

    def __init__(self, node, index=0, position=Position.LEFT_TOP, data_type=DataType.NUMERIC):
        self.node = node
        self.index = index
        self.posistion = position if isinstance(position, Socket.Position) else Socket.Position(position)
        self.data_type = data_type if isinstance(data_type, Socket.DataType) else Socket.DataType(data_type)

        # Graphics
        self.gr_socket = graphics_socket.QLGraphicsSocket(self.node.gr_node, color=self.DATA_COLORS.get(self.data_type))
        self.gr_socket.setPos(*self.node.get_socket_position(self.index, self.posistion))

        # Edge
        self.edge = None

    def has_edge(self):
        return self.edge is not None

    def get_position(self):
        return self.node.get_socket_position(self.index, self.posistion)

    def set_connected_edge(self, edge=None):
        self.edge = edge
