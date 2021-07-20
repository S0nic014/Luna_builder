import imp
import luna.utils.enumFn as enumFn
import luna_builder.editor.graphics_edge as graphics_edge
imp.reload(graphics_edge)


class Edge(object):

    class Style(enumFn.Enum):
        DIRECT = graphics_edge.QLGraphicsEdgeDirect
        BEZIER = graphics_edge.QDGraphicsEdgeBezier

    def __init__(self, scene, start_socket, end_socket, typ=Style.BEZIER):
        self.scene = scene
        self.start_socket = start_socket
        self.end_socket = end_socket

        self.start_socket.edge = self
        if self.end_socket is not None:
            self.end_socket.edge = self

        self.gr_edge = typ.value(self)
        self.update_positions()
        self.scene.gr_scene.addItem(self.gr_edge)

    def update_positions(self):
        source_pos = self.start_socket.get_position()
        source_pos[0] += self.start_socket.node.gr_node.pos().x()
        source_pos[1] += self.start_socket.node.gr_node.pos().y()
        self.gr_edge.set_source(*source_pos)
        if self.end_socket is not None:
            end_pos = self.end_socket.get_position()
            end_pos[0] += self.end_socket.node.gr_node.pos().x()
            end_pos[1] += self.end_socket.node.gr_node.pos().y()
            self.gr_edge.set_destination(*end_pos)
        self.gr_edge.update()

    def remove_from_sockets(self):
        if self.start_socket is not None:
            self.start_socket.edge = None
        if self.end_socket is not None:
            self.end_socket.edge = None
        self.start_socket = None
        self.end_socket = None

    def remove(self):
        self.remove_from_sockets()
        self.scene.gr_scene.removeItem(self.gr_edge)
        self.gr_edge = None
        self.scene.remove_edge(self)
