
from PySide2 import QtCore
from PySide2 import QtWidgets
import pymel.core as pm
import imp
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from luna import Logger
from luna import __version__
from luna.utils import pysideFn

from luna_builder.tabs import tab_workspace
import luna_builder.menus as menus
import luna_builder.editor.node_editor as node_editor
imp.reload(node_editor)


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
    def close_and_delete(cls):
        if not cls.INSTANCE:
            return
        cls.INSTANCE.close()
        cls.INSTANCE.deleteLater()
        cls.INSTANCE = None

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
        pysideFn.add_widget_to_layout(self, self.workspaceControlName)

        # UI setup
        self.create_actions()
        self.create_widgets()
        self.create_menu_bar()
        self.create_layouts()
        self.create_connections()

    def create_actions(self):
        pass

    def create_menu_bar(self):
        self.menu_bar = QtWidgets.QMenuBar()
        # Corner button
        self.update_tab_btn = QtWidgets.QPushButton()
        self.update_tab_btn.setFlat(True)
        self.update_tab_btn.setIcon(pysideFn.get_QIcon("refresh.png"))
        self.menu_bar.setCornerWidget(self.update_tab_btn, QtCore.Qt.TopRightCorner)

        # Menus
        self.file_menu = menus.FileMenu(self.workspace_wgt)
        self.controls_menu = menus.ControlsMenu()
        self.joints_menu = menus.JointsMenu()
        self.skin_menu = menus.SkinMenu()
        self.blendshapes_menu = menus.BlendshapesMenu()
        self.rig_menu = menus.RigMenu()
        self.help_menu = menus.HelpMenu()

        # Populate menu bar
        self.menu_bar.addMenu(self.file_menu)
        self.menu_bar.addMenu(self.controls_menu)
        self.menu_bar.addMenu(self.joints_menu)
        self.menu_bar.addMenu(self.skin_menu)
        self.menu_bar.addMenu(self.blendshapes_menu)
        self.menu_bar.addMenu(self.rig_menu)
        self.menu_bar.addMenu(self.help_menu)

    def create_widgets(self):
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setTabPosition(self.tab_widget.East)
        self.tab_widget.setMaximumWidth(500)
        self.workspace_wgt = tab_workspace.WorkspaceWidget()
        self.tab_widget.addTab(self.workspace_wgt, self.workspace_wgt.label)

        self.node_editor = node_editor.NodeEditor()

    def create_layouts(self):
        self.hor_layout = QtWidgets.QHBoxLayout()
        self.hor_layout.setContentsMargins(0, 0, 0, 0)
        self.hor_layout.addWidget(self.node_editor)
        self.hor_layout.addWidget(self.tab_widget)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setMenuBar(self.menu_bar)
        self.main_layout.addLayout(self.hor_layout)

    def create_connections(self):
        # Other
        self.update_tab_btn.clicked.connect(lambda: self.tab_widget.currentWidget().update_data())


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
