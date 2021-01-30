import os

from functools import partial
from PySide2 import QtCore
from PySide2 import QtWidgets
import pymel.api as pma
import pymel.core as pm
from shiboken2 import getCppPointer
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from luna import Logger
from luna import Config
from luna import ProjectVars
from luna import static
from luna.utils import pysideFn
from luna.utils import environFn

from luna_rig.functions import asset_files
from luna_rig.core import shape_manager
from luna_rig import importexport

from luna_builder.tabs import tab_workspace
reload(tab_workspace)


class MainDialog(MayaQWidgetDockableMixin, QtWidgets.QWidget):

    WINDOW_TITLE = "Luna build manager"
    UI_NAME = "lunaBuildManager"
    UI_SCRIPT = "import luna_builder\nluna_builder.MainDialog()"
    UI_INSTANCE = None
    MINIMUM_SIZE = [400, 500]

    DEFAULT_SETTINGS = {}

    @classmethod
    def display(cls):
        if not cls.UI_INSTANCE:
            cls.UI_INSTANCE = MainDialog()

        if cls.UI_INSTANCE.isHidden():
            cls.UI_INSTANCE.show(dockable=1, uiScript=cls.UI_SCRIPT)
        else:
            cls.UI_INSTANCE.raise_()
            cls.UI_INSTANCE.activateWindow()

    def __init__(self):
        super(MainDialog, self).__init__()

        # Window adjustments
        self.__class__.UI_INSTANCE = self
        self.setObjectName(self.__class__.UI_NAME)
        self.setWindowTitle(self.WINDOW_TITLE)
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
        self.file_clear_referances_action = QtWidgets.QAction(pysideFn.get_QIcon("unloadedReference.png", maya_icon=True), "Clear all referances", self)
        self.file_save_new_guides_action = QtWidgets.QAction("Increment and save", self)
        self.file_save_guide_as_action = QtWidgets.QAction("Save guides as...", self)
        self.file_save_new_rig_action = QtWidgets.QAction("Increment and save", self)
        self.file_save_rig_as_action = QtWidgets.QAction("Save rig as...", self)
        # Controls
        self.controls_export_all_action = QtWidgets.QAction(pysideFn.get_QIcon("save.png", maya_icon=True), "Export asset shapes", self)
        self.controls_import_all_action = QtWidgets.QAction("Import asset shapes", self)
        self.controls_load_shape_action = QtWidgets.QAction(pysideFn.get_QIcon("library.png"), "Load shape from library", self)
        self.controls_save_shape_action = QtWidgets.QAction("Save as new shape", self)
        self.controls_copy_shape_action = QtWidgets.QAction(pysideFn.get_QIcon("copyCurve.png"), "Copy shape", self)
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
        # Rig
        self.rig_datamanager_action = QtWidgets.QAction("Data manager", self)

        # Help
        self.help_docs_action = QtWidgets.QAction(pysideFn.get_QIcon("help.png", maya_icon=True), "Documentation", self)

    def create_menu_bar(self):
        # File menu
        self.file_menu = QtWidgets.QMenu("File")
        self.file_menu.setTearOffEnabled(True)
        self.file_menu.addSection("Project")
        self.file_menu.addMenu("Recent projects")
        self.file_menu.addSection("Guides")
        self.file_menu.addAction(self.file_save_guide_as_action)
        self.file_menu.addAction(self.file_save_new_guides_action)
        self.file_menu.addSection("Rig")
        self.file_menu.addAction(self.file_save_rig_as_action)
        self.file_menu.addAction(self.file_save_new_rig_action)
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
        self.controls_menu.addSection("Color")
        color_index_menu = self.controls_menu.addMenu("Set color")
        color_index_menu.setTearOffEnabled(True)
        self.add_color_actions(color_index_menu)
        self.controls_menu.addAction(self.controls_copy_color_action)
        self.controls_menu.addAction(self.controls_paste_color_action)
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
        # Rig menu
        self.rig_menu = QtWidgets.QMenu("Rig")
        self.rig_menu.addAction(self.rig_datamanager_action)

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
        self.file_save_new_guides_action.triggered.connect(lambda: asset_files.increment_save_file(typ="guides"))
        self.file_save_guide_as_action.triggered.connect(lambda: asset_files.save_file_as(typ="guides"))
        self.file_save_new_rig_action.triggered.connect(lambda: asset_files.increment_save_file(typ="rig"))
        self.file_save_rig_as_action.triggered.connect(lambda: asset_files.save_file_as(typ="rig"))
        self.file_save_new_guides_action.triggered.connect(self.workspace_wgt.update_data)
        self.file_save_new_rig_action.triggered.connect(self.workspace_wgt.update_data)
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
        # TODO: Add joint menu connections
        # Skin
        self.skin_bind_skin_action.triggered.connect(lambda: pm.mel.eval("SmoothBindSkinOptions;"))
        self.skin_detach_skin_action.triggered.connect(lambda: pm.mel.eval("DetachSkinOptions;"))
        self.skin_mirror_skin_action.triggered.connect(lambda: pm.mel.eval("MirrorSkinWeightsOptions;"))
        self.skin_copy_skin_action.triggered.connect(lambda: pm.mel.eval("CopySkinWeightsOptions;"))
        self.skin_export_all_action.triggered.connect(lambda: importexport.SkinClusterManager().export_all())
        self.skin_import_all_action.triggered.connect(lambda: importexport.SkinClusterManager().import_all())
        self.skin_export_selected_action.triggered.connect(lambda: importexport.SkinClusterManager.export_selected())
        self.skin_import_selected_action.triggered.connect(lambda: importexport.SkinClusterManager.import_selected())
        # TODO: add nglskintools connections

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
            project_action.triggered.connect(lambda: self.workspace_wgt.project_grp.set_project(prj[1]))
            recent_projects_menu.addAction(project_action)

    def update_file_actions_state(self):
        asset_set = True if environFn.get_asset_var() else False
        self.file_model_reference_action.setEnabled(asset_set)
        self.file_save_guide_as_action.setEnabled(asset_set)
        self.file_save_new_guides_action.setEnabled(asset_set)
        self.file_save_rig_as_action.setEnabled(asset_set)
        self.file_save_new_rig_action.setEnabled(asset_set)

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
            action.triggered.connect(partial(shape_manager.ShapeManager.set_color, None, color_index))


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
