import pymel.core as pm
from PySide2 import QtWidgets
import luna
import luna.utils.pysideFn as pysideFn
import luna_rig.importexport as importexport


class BlendshapesMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super(BlendshapesMenu, self).__init__("Shapes", parent)
        self.setTearOffEnabled(True)
        self.create_actions()
        self.create_sub_menus()
        self.populate()
        self.create_connections()

    def create_sub_menus(self):
        pass

    def create_actions(self):
        self.shape_editor_action = QtWidgets.QAction(pysideFn.get_QIcon("blendShapeEditor.png", maya_icon=True), "Shape editor", self)
        self.pose_manager_action = QtWidgets.QAction(pysideFn.get_QIcon("poseEditor.png", maya_icon=True), "Pose manager", self)
        self.export_all_action = QtWidgets.QAction("Export asset blendshapes", self)
        self.import_all_action = QtWidgets.QAction("Import asset blendshapes", self)
        self.export_selected_action = QtWidgets.QAction("Exported selected blendshapes", self)
        self.import_selected_action = QtWidgets.QAction("Import selected blendshapes", self)
        self.export_interpolators_action = QtWidgets.QAction("Export interpolators", self)
        self.import_interpolators_action = QtWidgets.QAction("Import interpolators", self)

    def create_connections(self):
        self.aboutToShow.connect(self.update_actions_state)
        # Blendshapes
        self.shape_editor_action.triggered.connect(lambda: pm.mel.eval("ShapeEditor;"))
        self.pose_manager_action.triggered.connect(lambda: pm.mel.eval("PoseEditor;"))
        self.import_all_action.triggered.connect(importexport.BlendShapeManager.import_all)
        self.export_all_action.triggered.connect(importexport.BlendShapeManager.export_all)
        self.import_selected_action.triggered.connect(importexport.BlendShapeManager.import_selected)
        self.export_selected_action.triggered.connect(importexport.BlendShapeManager.export_selected)
        self.import_interpolators_action.triggered.connect(importexport.PsdManager.import_all)
        self.export_interpolators_action.triggered.connect(importexport.PsdManager.export_all)

    def populate(self):
        self.addAction(self.shape_editor_action)
        self.addAction(self.pose_manager_action)
        self.addSection("Asset blendshapes")
        self.addAction(self.import_all_action)
        self.addAction(self.export_all_action)
        self.addSection("Selection")
        self.addAction(self.import_selected_action)
        self.addAction(self.export_selected_action)
        self.addSection("Correctives")
        self.addAction(self.import_interpolators_action)
        self.addAction(self.export_interpolators_action)

    def update_actions_state(self):
        is_asset_set = True if luna.workspace.Asset.get() else False
        self.export_all_action.setEnabled(is_asset_set)
        self.import_all_action.setEnabled(is_asset_set)
        self.export_selected_action.setEnabled(is_asset_set)
        self.import_selected_action.setEnabled(is_asset_set)
        self.import_interpolators_action.setEnabled(is_asset_set)
        self.export_interpolators_action.setEnabled(is_asset_set)
