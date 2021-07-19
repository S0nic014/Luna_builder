import imp
import luna_builder.editor.graphics_node as graphics_node
import luna_builder.editor.node_content as node_content
imp.reload(graphics_node)
imp.reload(node_content)


class Node(object):
    def __init__(self, scene, title="Custom node"):
        self.scene = scene
        self.title = title
        self.socket_spacing = 22

        self.content = node_content.QLNodeContentWidget()
        self.gr_node = graphics_node.QLGraphicsNode(self)

        self.scene.add_node(self)
        self.scene.gr_scene.addItem(self.gr_node)

        self.inputs = []
        self.outputs = []

    @property
    def position(self):
        return self.gr_node.pos()

    def set_position(self, x, y):
        self.gr_node.setPos(x, y)

    # def get_socket_position(self, index, position):
    #     if position in (Socket.Position.LEFT_TOP, Socket.Position.LEFT_BOTTOM):
    #         x = 0
    #     else:
    #         x = self.gr_node.width

    #     if position in (Socket.Position.LEFT_BOTTOM, Socket.Position.RIGHT_BOTTOM):
    #         # start from top
    #         y = self.gr_node.height - self.gr_node.edge_size - self.gr_node._padding - index * self.socket_spacing
    #     else:
    #         # start from bottom
    #         y = self.gr_node.title_height + self.gr_node._padding + self.gr_node.edge_size + index * self.socket_spacing

    #     return [x, y]

    # def update_connected_edges(self):
    #     for socket in self.inputs + self.outputs:
    #         if socket.has_edge():
    #             socket.edge.update_positions()
