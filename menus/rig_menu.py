from PySide2 import QtWidgets
import luna
import luna.utils.pysideFn as pysideFn
import luna.utils.environFn as environFn


class RigMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super(RigMenu, self).__init__("Rig", parent)
        self.setTearOffEnabled(True)
        self.create_actions()
        self.create_sub_menus()
        self.populate()
        self.create_connections()

    def create_sub_menus(self):
        pass

    def create_actions(self):
        self.driven_pose_exporter = QtWidgets.QAction("Export driven pose", self)

    def create_connections(self):
        self.driven_pose_exporter.triggered.connect(lambda: luna.tools.DrivenPoseExporter.display())

    def populate(self):
        self.addAction(self.driven_pose_exporter)

    def update_actions_state(self):
        is_asset_set = True if environFn.get_asset_var() else False
        self.driven_pose_exporter.setEnabled(is_asset_set)