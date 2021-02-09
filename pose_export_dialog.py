import pymel.core as pm
from PySide2 import QtWidgets
from luna import Logger
import luna_rig
import luna.interface.shared_widgets as shared_widgets
from luna_rig.importexport import key_pose
from luna.utils import pysideFn


class PoseExportDialog(QtWidgets.QDialog):
    def __init__(self, parent=pysideFn.maya_main_window()):
        super(PoseExportDialog, self).__init__(parent)
        self.setWindowTitle("Export key pose")

        self.create_widgets()
        self.create_layous()
        self.create_connections()
        self.update_component_list()

    def create_widgets(self):
        self.options_widget = QtWidgets.QWidget()
        self.components_list = QtWidgets.QListWidget()
        self.pose_name_field = shared_widgets.LineFieldWidget("Pose name:", "Export")
        self.driver_field = shared_widgets.LineFieldWidget("Driver:", "Set")
        self.controls_list = QtWidgets.QListWidget()
        self.controls_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.splitter = QtWidgets.QSplitter()
        self.splitter.addWidget(self.options_widget)
        self.splitter.addWidget(self.controls_list)

    def create_layous(self):
        options_layout = QtWidgets.QVBoxLayout()
        options_layout.addWidget(self.components_list)
        options_layout.addWidget(self.driver_field)
        options_layout.addWidget(self.pose_name_field)
        options_layout.addStretch()
        self.options_widget.setLayout(options_layout)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.splitter)
        self.setLayout(self.main_layout)

    def create_connections(self):
        self.components_list.currentItemChanged.connect(self.update_controls_list)
        self.driver_field.button.clicked.connect(self.set_driver)
        self.pose_name_field.button.clicked.connect(self.export_pose)

    def set_driver(self):
        selection = pm.selected()
        if not selection:
            return
        selection = selection[-1]
        if luna_rig.Control.is_control(selection):
            self.driver_field.line_edit.setText(selection.name())

    def update_component_list(self):
        self.components_list.clear()
        for component in luna_rig.MetaRigNode.list_nodes(of_type=luna_rig.AnimComponent):
            list_item = QtWidgets.QListWidgetItem(str(component))
            list_item.setData(1, component)
            self.components_list.addItem(list_item)

    def update_controls_list(self, item):
        component = item.data(1)
        self.controls_list.clear()
        for control in component.controls:
            list_item = QtWidgets.QListWidgetItem(control.transform.name())
            list_item.setData(1, control)
            self.controls_list.addItem(list_item)

    def export_pose(self):
        pose_manager = key_pose.KeyPoseManager()
        current_component = self.components_list.currentItem().data(1)
        if not self.controls_list.selectedItems():
            export_controls = current_component.controls
        else:
            export_controls = [item.data(1) for item in self.controls_list.selectedItems()]
        pose_manager.export_pose(current_component,
                                 export_controls,
                                 driver_ctl=self.driver_field.line_edit.text(),
                                 pose_name=self.pose_name_field.line_edit.text())


if __name__ == "__main__":
    testTool = PoseExportDialog()
    testTool.show()
