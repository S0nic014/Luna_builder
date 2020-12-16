import os
from functools import partial

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
import pymel.api as pma
import pymel.core as pm
from shiboken2 import getCppPointer
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from Luna import Logger
from Luna import Config
from Luna import ProjectVars
from Luna.utils import pysideFn
from Luna.workspace import project

from Luna_rig.functions import asset_files

from Luna_builder.tabs import tab_workspace
reload(tab_workspace)
reload(asset_files)


class MainDialog(MayaQWidgetDockableMixin, QtWidgets.QWidget):

    WINDOW_TITLE = "Luna build manager"
    UI_NAME = "LunaBuildManager"
    UI_SCRIPT = "from Luna.tools import buildManager\nbuildManager.MainDialog()"
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
        self.file_model_reference_action = QtWidgets.QAction("Reference asset model", self)
        self.file_model_reference_action.setIcon(pysideFn.get_QIcon("reference.svg", maya_icon=True))
        self.clear_all_referances_action = QtWidgets.QAction("Clear all referances", self)
        self.clear_all_referances_action.setIcon(pysideFn.get_QIcon("unloadedReference.png", maya_icon=True))
        self.help_docs_action = QtWidgets.QAction("Documentation", self)
        self.help_docs_action.setIcon(QtGui.QIcon(":help.png"))

    def create_menu_bar(self):
        # #File menu
        self.file_menu = QtWidgets.QMenu("File")
        self.file_menu.addSection("Project")
        self.file_menu.addMenu("Recent projects")
        self.file_menu.addSection("Asset")
        self.file_menu.addAction(self.file_model_reference_action)
        self.file_menu.addAction(self.clear_all_referances_action)

        # Help menu
        help_menu = QtWidgets.QMenu("Help")
        help_menu.addAction(self.help_docs_action)
        # Menubar
        self.menu_bar = QtWidgets.QMenuBar()
        self.menu_bar.addMenu(self.file_menu)
        self.menu_bar.addMenu(help_menu)

    def create_widgets(self):
        self.tab_widget = QtWidgets.QTabWidget()
        self.workspace_wgt = tab_workspace.WorkspaceWidget()
        self.tab_widget.addTab(self.workspace_wgt, self.workspace_wgt.label)

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setMenuBar(self.menu_bar)
        self.main_layout.addWidget(self.tab_widget)

    def create_connections(self):
        self.file_menu.aboutToShow.connect(self.update_recent_projects)
        self.file_model_reference_action.triggered.connect(asset_files.reference_latest_model)
        self.clear_all_referances_action.triggered.connect(asset_files.clear_all_references)

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
            project_action.triggered.connect(partial(project.Project.set, prj[1]))
            project_action.triggered.connect(self.workspace_wgt.project_grp.update_project)
            recent_projects_menu.addAction(project_action)


if __name__ == "__main__":
    try:
        if testTool and testTool.parent():  # noqa: F821
            workspaceControlName = testTool.parent().objectName()  # noqa: F821

            if pm.window(workspaceControlName, ex=1, q=1):
                pm.deleteUI(workspaceControlName)
    except Exception:
        pass

    testTool = MainDialog()
    testTool.show(dockable=0, uiScript="")
