import os
from functools import partial

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
import pymel.api as pma
import pymel.core as pm
from shiboken2 import getCppPointer
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from luna import Logger
from luna import Config
from luna import ProjectVars
from luna.utils import pysideFn
from luna.utils import environFn
from luna.workspace import project

from luna_rig.functions import asset_files
from luna_rig.core import shape_manager
from luna_rig import importexport

from luna_builder.tabs import tab_workspace
reload(asset_files)
reload(tab_workspace)


class MainDialog(MayaQWidgetDockableMixin, QtWidgets.QWidget):

    WINDOW_TITLE = "luna build manager"
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
        self.file_model_reference_action = QtWidgets.QAction("Reference model", self)
        self.file_clear_referances_action = QtWidgets.QAction("Clear all referances", self)
        self.file_save_new_guides_action = QtWidgets.QAction("Increment and save", self)
        self.file_save_guide_as_action = QtWidgets.QAction("Save guides as...", self)
        self.file_save_new_rig_action = QtWidgets.QAction("Increment and save", self)
        self.file_save_rig_as_action = QtWidgets.QAction("Save rig as...", self)
        self.file_model_reference_action.setIcon(pysideFn.get_QIcon("reference.svg", maya_icon=True))
        self.file_clear_referances_action.setIcon(pysideFn.get_QIcon("unloadedReference.png", maya_icon=True))
        # Controls
        self.controls_export_all_action = QtWidgets.QAction("Export asset shapes", self)
        self.controls_import_all_action = QtWidgets.QAction("Import asset shapes", self)
        self.controls_load_shape_action = QtWidgets.QAction("Load shape from library", self)
        self.controls_save_shape_action = QtWidgets.QAction("Save as new shape", self)
        self.controls_copy_shape_action = QtWidgets.QAction("Copy shape", self)
        self.controls_paste_shape_action = QtWidgets.QAction("Paste shape", self)
        self.controls_copy_color_action = QtWidgets.QAction("Copy color", self)
        self.controls_paste_color_action = QtWidgets.QAction("Paste color", self)
        self.controls_export_all_action.setIcon(pysideFn.get_QIcon("save.png", maya_icon=True))
        # Help
        self.help_docs_action = QtWidgets.QAction("Documentation", self)
        self.help_docs_action.setIcon(QtGui.QIcon(":help.png"))

    def create_menu_bar(self):
        # #File menu
        self.file_menu = QtWidgets.QMenu("File")
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

        self.controls_menu = QtWidgets.QMenu("Controls")
        self.controls_menu.addSection("Asset")
        self.controls_menu.addAction(self.controls_import_all_action)
        self.controls_menu.addAction(self.controls_export_all_action)
        self.controls_menu.addSection("Shape")
        self.controls_menu.addAction(self.controls_save_shape_action)
        self.controls_menu.addAction(self.controls_load_shape_action)
        self.controls_menu.addAction(self.controls_copy_shape_action)
        self.controls_menu.addAction(self.controls_paste_shape_action)
        self.controls_menu.addAction(self.controls_copy_color_action)
        self.controls_menu.addAction(self.controls_paste_color_action)

        # Help menu
        help_menu = QtWidgets.QMenu("Help")
        help_menu.addAction(self.help_docs_action)
        # Menubar
        self.menu_bar = QtWidgets.QMenuBar()
        self.menu_bar.addMenu(self.file_menu)
        self.menu_bar.addMenu(self.controls_menu)
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
