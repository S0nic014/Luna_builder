import imp
import luna_builder.editor.graphics_node as graphics_node
import luna_builder.editor.node_content as node_content
import luna_builder.editor.node_socket as node_socket
imp.reload(graphics_node)
imp.reload(node_content)
imp.reload(node_socket)


class Node(object):
    def __init__(self, scene, title="Custom node", inputs=[], outputs=[]):
        self.scene = scene
        self.title = title

        self.content = node_content.QLNodeContentWidget()
        self.gr_node = graphics_node.QLGraphicsNode(self)

        self.scene.add_node(self)
        self.scene.gr_scene.addItem(self.gr_node)

        # Create sockets
        self.socket_spacing = 22
        self.inputs = []
        self.outputs = []
        for index, item in enumerate(inputs):
            socket = node_socket.Socket(node=self, index=index, position=node_socket.Socket.Position.LEFT_TOP, data_type=item)
            self.inputs.append(socket)

        for index, item in enumerate(outputs):
            socket = node_socket.Socket(node=self, index=index, position=node_socket.Socket.Position.RIGHT_TOP, data_type=item)
            self.outputs.append(socket)

    @property
    def position(self):
        return self.gr_node.pos()

    def set_position(self, x, y):
        self.gr_node.setPos(x, y)

    def get_socket_position(self, index, position):
        if position in (node_socket.Socket.Position.LEFT_TOP, node_socket.Socket.Position.LEFT_BOTTOM):
            x = 0
        else:
            x = self.gr_node.width

        if position in (node_socket.Socket.Position.LEFT_BOTTOM, node_socket.Socket.Position.RIGHT_BOTTOM):
            # start from top
            y = self.gr_node.height - self.gr_node.edge_size - self.gr_node._padding - index * self.socket_spacing
        else:
            # start from bottom
            y = self.gr_node.title_height + self.gr_node._padding + self.gr_node.edge_size + index * self.socket_spacing

        return [x, y]

    def update_connected_edges(self):
        for socket in self.inputs + self.outputs:
            if socket.has_edge():
                socket.edge.update_positions()
