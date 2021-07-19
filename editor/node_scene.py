import imp
import luna_builder.editor.graphics_scene as graphics_scene
imp.reload(graphics_scene)


class Scene:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.gr_scene = None  # type: graphics_scene.QLGraphicsScene

        self.scene_width = 64000
        self.scene_height = 64000

        self.init_ui()

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def remove_node(self, node):
        self.nodes.remove(node)

    def remove_edge(self, edge):
        self.edges.remove(edge)

    def init_ui(self):
        self.gr_scene = graphics_scene.QLGraphicsScene(self)
        self.gr_scene.set_scene_size(self.scene_width, self.scene_height)
