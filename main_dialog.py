from luna_builder.tabs import tab_workspace
import os

from PySide2 import QtCore
from PySide2 import QtWidgets
import pymel.api as pma
import pymel.core as pm
from shiboken2 import getCppPointer
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from luna import __version__
from luna import Logger
from luna import Config
from luna import ProjectVars
from luna import static
from luna.utils import pysideFn
from luna.utils import environFn

import luna.tools
import luna_rig.functions.jointFn as jointFn
from luna_rig.functions import asset_files
from luna_rig.core import shape_manager
from luna_rig import importexport
reload(tab_workspace)


class MainDialog(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    WINDOW_TITLE = "Luna builder - " + __version__
    DOCKED_TITLE = "Luna builder"
    UI_NAME = "lunaBuildManager"
    UI_SCRIPT = "import luna_builder\nluna_builder.MainDialog()"
    INSTANCE = None
    MINIMUM_SIZE = [400, 500]

    DEFAULT_SETTINGS = {}

    @classmethod
    def display(cls):
        if not cls.INSTANCE:
            cls.INSTANCE = MainDialog()

        if cls.INSTANCE.isHidden():
            cls.INSTANCE.show(dockable=1, uiScript=cls.UI_SCRIPT)
        else:
            cls.INSTANCE.raise_()
            cls.INSTANCE.activateWindow()

    @classmethod
    def hide_and_delete(cls):
        if not cls.INSTANCE:
            return
        cls.INSTANCE.hide()
        cls.INSTANCE.deleteLater()

    def showEvent(self, event):
        if self.isFloating():
            self.setWindowTitle(self.WINDOW_TITLE)
        else:
            self.setWindowTitle(self.DOCKED_TITLE)
        super(MainDialog, self).showEvent(event)

    def __init__(self):
        super(MainDialog, self).__init__()

        # Window adjustments
        self.__class__.INSTANCE = self
        self.setObjectName(self.__class__.UI_NAME)
        self.setWindowIcon(pysideFn.get_QIcon("builder.svg"))
        self.setMinimumSize(*self.MINIMUM_SIZE)
        self.setProperty("saveWindowPref", True)

        # Workspace control
        self.workspaceControlName = "{0}WorkspaceControl".format(self.UI_NAME)
        if pm.workspaceControl(self.workspaceControlName, q=1, ex=1):
            workspaceControlPtr = long(pma.MQtUtil.findControl(self.workspaceControlName))
            widgetPtr = long(getCppPointer(self)[0])
            pma.MQtUtil.addWidgetToMayaLayout(widgetPtr, workspaceControlPtr)

        # UI setup
        self.create_actions()
        self.create_menu_bar()
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_actions(self):
        # File
        self.file_model_reference_action = QtWidgets.QAction(pysideFn.get_QIcon("reference.svg", maya_icon=True), "Reference model", self)
        self.file_clear_referances_action = QtWidgets.QAction(pysideFn.get_QIcon("unloadedReference.png", maya_icon=True), "Clear all references", self)
        self.file_save_new_skeleton_action = QtWidgets.QAction("Increment and save", self)
        self.file_save_skeleton_as_action = QtWidgets.QAction("Save skeleton as...", self)
        self.file_save_rig_as_action = QtWidgets.QAction("Save rig as...", self)
        # Controls
        self.controls_export_all_action = QtWidgets.QAction(pysideFn.get_QIcon("save.png", maya_icon=True), "Export asset shapes", self)
        self.controls_import_all_action = QtWidgets.QAction("Import asset shapes", self)
        self.controls_load_shape_action = QtWidgets.QAction(pysideFn.get_QIcon("library.png"), "Load shape from library", self)
        self.controls_save_shape_action = QtWidgets.QAction("Save as new shape", self)
        self.controls_copy_shape_action = QtWidgets.QAction(pysideFn.get_QIcon("copyCurve.png"), "Copy shape", self)
        self.controls_mirror_shape_action = QtWidgets.QAction(pysideFn.get_QIcon("mirrorCurve.png"), "Mirror shape in place", self)
        self.controls_mirror_shape_ops_action = QtWidgets.QAction(pysideFn.get_QIcon("mirrorCurve.png"), "Mirror shape to opposite", self)
        self.controls_paste_shape_action = QtWidgets.QAction(pysideFn.get_QIcon("pasteCurve.png"), "Paste shape", self)
        self.controls_copy_color_action = QtWidgets.QAction(pysideFn.get_QIcon("copyColor.png"), "Copy color", self)
        self.controls_paste_color_action = QtWidgets.QAction(pysideFn.get_QIcon("pasteColor.png"), "Paste color", self)
        # Joints
        self.joints_mirror_action = QtWidgets.QAction(pysideFn.get_QIcon("mirrorJoint.png"), "Mirror", self)
        self.joints_sel_to_chain_action = QtWidgets.QAction(pysideFn.get_QIcon("kinJoint.png", maya_icon=True), "Chain from selection", self)
        # Skin
        self.skin_bind_skin_action = QtWidgets.QAction(pysideFn.get_QIcon("smoothSkin.png", maya_icon=True), "Bind skin", self)
        self.skin_detach_skin_action = QtWidgets.QAction(pysideFn.get_QIcon("detachSkin.png", maya_icon=True), "Detach skin", self)
        self.skin_mirror_skin_action = QtWidgets.QAction(pysideFn.get_QIcon("mirrorSkinWeight.png", maya_icon=True), "Mirror weights", self)
        self.skin_copy_skin_action = QtWidgets.QAction(pysideFn.get_QIcon("copySkinWeight.png", maya_icon=True), "Copy weights", self)
        self.skin_export_all_action = QtWidgets.QAction(pysideFn.get_QIcon("save.png", maya_icon=True), "Export asset weights", self)
        self.skin_import_all_action = QtWidgets.QAction("Import asset weights", self)
        self.skin_export_selected_action = QtWidgets.QAction("Export selection weights", self)
        self.skin_import_selected_action = QtWidgets.QAction("Import selection weights", self)
        self.skin_ngtools_export_all_action = QtWidgets.QAction("Export asset layers", self)
        self.skin_ngtools_import_all_action = QtWidgets.QAction("Import asset layers", self)
        self.skin_ngtools_export_selected_action = QtWidgets.QAction("Export selection layers", self)
        self.skin_ngtools_import_selected_action = QtWidgets.QAction("Import selection layers", self)
        self.skin_ngtools2_export_all_action = QtWidgets.QAction("Export asset layers", self)
        self.skin_ngtools2_import_all_action = QtWidgets.QAction("Import asset layers", self)
        self.skin_ngtools2_export_selected_action = QtWidgets.QAction("Export selection layers", self)
        self.skin_ngtools2_import_selected_action = QtWidgets.QAction("Import selection layers", self)
        # Blendshapes
        self.blendshapes_shape_editor_action = QtWidgets.QAction(pysideFn.get_QIcon("blendShapeEditor.png", maya_icon=True), "Shape editor", self)
        self.psd_maya_pose_manager_action = QtWidgets.QAction(pysideFn.get_QIcon("poseEditor.png", maya_icon=True), "Pose manager", self)
        self.blendshapes_export_all_action = QtWidgets.QAction("Export asset blendshapes", self)
        self.blendshapes_import_all_action = QtWidgets.QAction("Import asset blendshapes", self)
        self.blednshapes_export_selected_action = QtWidgets.QAction("Exported selected blendshapes", self)
        self.blendshapes_import_selected_action = QtWidgets.QAction("Import selected blendshapes", self)
        self.psd_export_interpolators_action = QtWidgets.QAction("Export interpolators", self)
        self.psd_import_interpolators_action = QtWidgets.QAction("Import interpolators", self)

        # Rig
        self.rig_driven_pose_exporter = QtWidgets.QAction("Export driven pose", self)

        # Help
        self.help_docs_action = QtWidgets.QAction(pysideFn.get_QIcon("help.png", maya_icon=True), "Documentation", self)

    def create_menu_bar(self):
        # File menu
        self.file_menu = QtWidgets.QMenu("File")
        self.file_menu.setTearOffEnabled(True)
        self.file_menu.addSection("Project")
        self.file_menu.addMenu("Recent projects")
        self.file_menu.addSection("Skeleton")
        self.file_menu.addAction(self.file_save_skeleton_as_action)
        self.file_menu.addAction(self.file_save_new_skeleton_action)
        self.file_menu.addSection("Rig")
        self.file_menu.addAction(self.file_save_rig_as_action)
        self.file_menu.addSection("Asset")
        self.file_menu.addAction(self.file_model_reference_action)
        self.file_menu.addAction(self.file_clear_referances_action)
        # Controls menu
        self.controls_menu = QtWidgets.QMenu("Controls")
        self.controls_menu.setTearOffEnabled(True)
        self.controls_menu.addSection("Asset")
        self.controls_menu.addAction(self.controls_import_all_action)
        self.controls_menu.addAction(self.controls_export_all_action)
        self.controls_menu.addSection("Shape")
        self.controls_menu.addAction(self.controls_save_shape_action)
        self.controls_menu.addAction(self.controls_load_shape_action)
        self.controls_menu.addAction(self.controls_copy_shape_action)
        self.controls_menu.addAction(self.controls_paste_shape_action)
        self.controls_menu.addAction(self.controls_mirror_shape_action)
        self.controls_menu.addAction(self.controls_mirror_shape_ops_action)
        self.controls_menu.addSection("Color")
        color_index_menu = self.controls_menu.addMenu("Set color")
        color_index_menu.setTearOffEnabled(True)
        self.add_color_actions(color_index_menu)
        self.controls_menu.addAction(self.controls_copy_color_action)
        self.controls_menu.addAction(self.controls_paste_color_action)
        self.controls_menu.addSection("Pose")
        # Joints menu
        self.joints_menu = QtWidgets.QMenu("Joints")
        self.joints_menu.setTearOffEnabled(True)
        self.joints_menu.addAction(self.joints_sel_to_chain_action)
        self.joints_menu.addAction(self.joints_mirror_action)
        # Skin menu
        self.skin_menu = QtWidgets.QMenu("Skin")
        self.skin_menu.setTearOffEnabled(True)
        self.skin_menu.addAction(self.skin_bind_skin_action)
        self.skin_menu.addAction(self.skin_detach_skin_action)
        self.skin_menu.addSection("Weight maps")
        self.skin_menu.addAction(self.skin_mirror_skin_action)
        self.skin_menu.addAction(self.skin_copy_skin_action)
        self.skin_menu.addSection("Asset")
        self.skin_menu.addAction(self.skin_export_all_action)
        self.skin_menu.addAction(self.skin_import_all_action)
        self.skin_menu.addAction(self.skin_export_selected_action)
        self.skin_menu.addAction(self.skin_import_selected_action)
        if "ngSkinTools" in pm.moduleInfo(lm=1):
            self.skin_menu.addSection("ngSkinTools")
            ng_asset_menu = self.skin_menu.addMenu("Asset")  # type: QtWidgets.QMenu
            ng_asset_menu.setTearOffEnabled(True)
            ng_asset_menu.addAction(self.skin_ngtools_export_all_action)
            ng_asset_menu.addAction(self.skin_ngtools_import_all_action)
            ng_selection_menu = self.skin_menu.addMenu("Selection")  # type: QtWidgets.QMenu
            ng_selection_menu.setTearOffEnabled(True)
            ng_selection_menu.addAction(self.skin_ngtools_export_selected_action)
            ng_selection_menu.addAction(self.skin_ngtools_import_selected_action)
        if "ngskintools2" in pm.moduleInfo(lm=1):
            self.skin_menu.addSection("ngSkinTools2")
            ng2_asset_menu = self.skin_menu.addMenu("Asset")  # type: QtWidgets.QMenu
            ng2_asset_menu.setTearOffEnabled(True)
            ng2_asset_menu.addAction(self.skin_ngtools2_export_all_action)
            ng2_asset_menu.addAction(self.skin_ngtools2_import_all_action)
            ng2_selection_menu = self.skin_menu.addMenu("Selection")  # type: QtWidgets.QMenu
            ng2_selection_menu.setTearOffEnabled(True)
            ng2_selection_menu.addAction(self.skin_ngtools2_export_selected_action)
            ng2_selection_menu.addAction(self.skin_ngtools2_import_selected_action)
        # Blendshapes
        self.blendshapes_menu = QtWidgets.QMenu("Shapes")
        self.blendshapes_menu.addAction(self.blendshapes_shape_editor_action)
        self.blendshapes_menu.addAction(self.psd_maya_pose_manager_action)
        self.blendshapes_menu.addSection("Asset blendshapes")
        self.blendshapes_menu.addAction(self.blendshapes_import_all_action)
        self.blendshapes_menu.addAction(self.blendshapes_export_all_action)
        self.blendshapes_menu.addSection("Selection")
        self.blendshapes_menu.addAction(self.blendshapes_import_selected_action)
        self.blendshapes_menu.addAction(self.blednshapes_export_selected_action)
        self.blendshapes_menu.addSection("Correctives")
        self.blendshapes_menu.addAction(self.psd_import_interpolators_action)
        self.blendshapes_menu.addAction(self.psd_export_interpolators_action)

        # Rig menu
        self.rig_menu = QtWidgets.QMenu("Rig")
        self.rig_menu.addAction(self.rig_driven_pose_exporter)

        # Help menu
        help_menu = QtWidgets.QMenu("Help")
        help_menu.setTearOffEnabled(True)
        help_menu.addAction(self.help_docs_action)
        # Menubar
        self.menu_bar = QtWidgets.QMenuBar()
        self.menu_bar.addMenu(self.file_menu)
        self.menu_bar.addMenu(self.controls_menu)
        self.menu_bar.addMenu(self.joints_menu)
        self.menu_bar.addMenu(self.skin_menu)
        self.menu_bar.addMenu(self.blendshapes_menu)
        self.menu_bar.addMenu(self.rig_menu)
        self.menu_bar.addMenu(help_menu)

    def create_widgets(self):
        self.update_tab_btn = QtWidgets.QPushButton()
        self.update_tab_btn.setFlat(True)
        self.update_tab_btn.setIcon(pysideFn.get_QIcon("refresh.png"))
        self.menu_bar.setCornerWidget(self.update_tab_btn, QtCore.Qt.TopRightCorner)

        self.tab_widget = QtWidgets.QTabWidget()
        self.workspace_wgt = tab_workspace.WorkspaceWidget()
        self.tab_widget.addTab(self.workspace_wgt, self.workspace_wgt.label)

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setMenuBar(self.menu_bar)
        self.main_layout.addWidget(self.tab_widget)

    def create_connections(self):
        # File
        self.file_menu.aboutToShow.connect(self.update_recent_projects)
        self.file_menu.aboutToShow.connect(self.update_file_actions_state)
        self.file_model_reference_action.triggered.connect(asset_files.reference_model)
        self.file_clear_referances_action.triggered.connect(asset_files.clear_all_references)
        self.file_save_new_skeleton_action.triggered.connect(lambda: asset_files.increment_save_file(typ="skeleton"))
        self.file_save_skeleton_as_action.triggered.connect(lambda: asset_files.save_file_as(typ="skeleton"))
        self.file_save_rig_as_action.triggered.connect(lambda: asset_files.save_file_as(typ="rig"))
        self.file_save_new_skeleton_action.triggered.connect(self.workspace_wgt.update_data)
        # Controls
        self.controls_menu.aboutToShow.connect(self.update_controls_actions_state)
        self.controls_export_all_action.triggered.connect(lambda: importexport.CtlShapeManager().export_asset_shapes())
        self.controls_import_all_action.triggered.connect(lambda: importexport.CtlShapeManager().import_asset_shapes())
        self.controls_save_shape_action.triggered.connect(importexport.CtlShapeManager.save_selection_to_lib)
        self.controls_load_shape_action.triggered.connect(importexport.CtlShapeManager.load_shape_from_lib)
        self.controls_copy_shape_action.triggered.connect(shape_manager.ShapeManager.copy_shape)
        self.controls_paste_shape_action.triggered.connect(shape_manager.ShapeManager.paste_shape)
        self.controls_copy_color_action.triggered.connect(shape_manager.ShapeManager.copy_color)
        self.controls_paste_color_action.triggered.connect(shape_manager.ShapeManager.paste_color)
        # Joints
        self.joints_mirror_action.triggered.connect(lambda *args: jointFn.mirror_chain())
        self.joints_sel_to_chain_action.triggered.connect(lambda *args: jointFn.create_chain(joint_list=pm.selected(type="joint")))
        # Skin
        self.skin_bind_skin_action.triggered.connect(lambda: pm.mel.eval("SmoothBindSkinOptions;"))
        self.skin_detach_skin_action.triggered.connect(lambda: pm.mel.eval("DetachSkinOptions;"))
        self.skin_mirror_skin_action.triggered.connect(lambda: pm.mel.eval("MirrorSkinWeightsOptions;"))
        self.skin_copy_skin_action.triggered.connect(lambda: pm.mel.eval("CopySkinWeightsOptions;"))
        self.skin_export_all_action.triggered.connect(lambda: importexport.SkinManager().export_all())
        self.skin_import_all_action.triggered.connect(lambda: importexport.SkinManager().import_all())
        self.skin_export_selected_action.triggered.connect(lambda: importexport.SkinManager.export_selected())
        self.skin_import_selected_action.triggered.connect(lambda: importexport.SkinManager.import_selected())
        # Ng layers
        self.skin_ngtools_export_all_action.triggered.connect(lambda: importexport.NgLayersManager().export_all())
        self.skin_ngtools_import_all_action.triggered.connect(lambda: importexport.NgLayersManager().import_all())
        self.skin_ngtools_export_selected_action.triggered.connect(importexport.NgLayersManager.export_selected)
        self.skin_ngtools_import_selected_action.triggered.connect(importexport.NgLayersManager.import_selected)
        # Blendshapes
        self.blendshapes_shape_editor_action.triggered.connect(lambda: pm.mel.eval("ShapeEditor;"))
        self.psd_maya_pose_manager_action.triggered.connect(lambda: pm.mel.eval("PoseEditor;"))
        self.blendshapes_import_all_action.triggered.connect(lambda: importexport.BlendShapeManager().import_all())
        self.blendshapes_export_all_action.triggered.connect(lambda: importexport.BlendShapeManager().export_all())
        self.blendshapes_import_selected_action.triggered.connect(importexport.BlendShapeManager.import_selected)
        self.blendshapes_import_selected_action.triggered.connect(importexport.BlendShapeManager.export_selected)
        self.psd_import_interpolators_action.triggered.connect(lambda: importexport.PsdManager().import_all())
        self.psd_export_interpolators_action.triggered.connect(lambda: importexport.PsdManager().export_all())

        # Rig
        self.rig_driven_pose_exporter.triggered.connect(lambda: luna.tools.DrivenPoseExporter.display())

        # Other
        self.update_tab_btn.clicked.connect(lambda: self.tab_widget.currentWidget().update_data())

    def update_recent_projects(self):
        projects_data = Config.get(ProjectVars.recent_projects)
        recent_projects_menu = [child for child in self.file_menu.findChildren(QtWidgets.QMenu) if child.title() == "Recent projects"]
        try:
            recent_projects_menu = recent_projects_menu[0]
        except IndexError:
            Logger.exception("Failed to find Recent projects QMenu")
            return

        recent_projects_menu.clear()
        for prj in projects_data:
            if not os.path.isdir(prj[1]):
                continue
            project_action = QtWidgets.QAction(prj[0], self)
            project_action.setToolTip(prj[1])
            project_action.triggered.connect(lambda path=prj[1], *args: self.workspace_wgt.project_grp.set_project(path))
            recent_projects_menu.addAction(project_action)

    def update_file_actions_state(self):
        asset_set = True if environFn.get_asset_var() else False
        self.file_model_reference_action.setEnabled(asset_set)
        self.file_save_skeleton_as_action.setEnabled(asset_set)
        self.file_save_new_skeleton_action.setEnabled(asset_set)
        self.file_save_rig_as_action.setEnabled(asset_set)

    def update_controls_actions_state(self):
        asset_set = True if environFn.get_asset_var() else False
        self.controls_export_all_action.setEnabled(asset_set)
        self.controls_import_all_action.setEnabled(asset_set)

    def add_color_actions(self, menu):
        for color_index in range(1, 32):
            icon_name = "colorIndex{}.png".format(static.ColorIndex(color_index).value)
            label = static.ColorIndex(color_index).name  # type: str
            label = label.title().replace("_", " ")
            action = QtWidgets.QAction(pysideFn.get_QIcon(icon_name), label, self)
            menu.addAction(action)
            action.triggered.connect(lambda nodes=None, index=color_index, *args: shape_manager.ShapeManager.set_color(nodes, index))


if __name__ == "__main__":
    try:
        if testTool and testTool.parent():  # noqa: F821
            workspaceControlName = testTool.parent().objectName()  # noqa: F821

            if pm.window(workspaceControlName, ex=1, q=1):
                pm.deleteUI(workspaceControlName)
    except Exception:
        pass

    testTool = MainDialog()
    testTool.show(dockable=1, uiScript="")
