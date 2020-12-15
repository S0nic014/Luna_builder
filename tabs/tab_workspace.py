import os

from PySide2 import QtWidgets
from PySide2 import QtGui

from Luna import Config
from Luna import Logger
from Luna import ProjectVars
from Luna.utils import pysideFn
from Luna.utils import environFn
from Luna.interface import shared_widgets
from Luna.workspace import project
reload(shared_widgets)
reload(pysideFn)


class WorkspaceWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(WorkspaceWidget, self).__init__(parent)

        self.label = "Workspace"
        # self.icon = pysideFn.get_QIcon("workspace.png")

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.scroll_wgt = shared_widgets.ScrollWidget()
        self.project_wgt = ProjectGroup()
        self.scroll_wgt.add_widget(self.project_wgt)
        self.scroll_wgt.content_layout.addStretch()

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.scroll_wgt)
        self.setLayout(self.main_layout)

    def create_connections(self):
        pass


class ProjectGroup(QtWidgets.QGroupBox):
    def __init__(self, title="Project", parent=None):
        super(ProjectGroup, self).__init__(title, parent)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.name_lineedit = QtWidgets.QLineEdit()
        self.name_lineedit.setReadOnly(True)
        self.set_btn = QtWidgets.QPushButton(pysideFn.get_QIcon("fileOpen", maya_icon=True), "")
        self.set_btn.setToolTip("Set existing project")
        self.create_btn = QtWidgets.QPushButton(pysideFn.get_QIcon("plus.png"), "")
        self.create_btn.setToolTip("Create new project")
        self.exit_btn = QtWidgets.QPushButton(pysideFn.get_QIcon("outArrow.png"), "")
        self.exit_btn.setToolTip("Exit Luna workspace")

    def create_layouts(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(QtWidgets.QLabel("Current:"))
        self.main_layout.addWidget(self.name_lineedit)
        self.main_layout.addWidget(self.create_btn)
        self.main_layout.addWidget(self.set_btn)
        self.main_layout.addWidget(self.exit_btn)
        self.setLayout(self.main_layout)

    def create_connections(self):
        self.create_btn.clicked.connect(self.create_project)
        self.set_btn.clicked.connect(self.set_project)
        self.exit_btn.clicked.connect(self.exit_project)

    def update_project(self):
        current_project = environFn.get_project_var()
        if not current_project:
            self.name_lineedit.setText("Not set")
            return

        self.name_lineedit.setText(current_project.name)
        self.name_lineedit.setToolTip(current_project.path)

    def create_project(self):
        prev_project_path = Config.get(ProjectVars.previous_project, default="")
        Logger.debug("Previous project: {0}".format(prev_project_path))
        if os.path.isdir(prev_project_path):
            root_dir = os.path.dirname(prev_project_path)
        else:
            root_dir = ""

        path = QtWidgets.QFileDialog.getExistingDirectory(None, "Create Luna project", root_dir)
        if path:
            project.Project.create(path)

        self.update_project()

    def set_project(self):
        prev_project_path = Config.get(ProjectVars.previous_project, default="")
        Logger.debug("Previous project: {0}".format(prev_project_path))
        if os.path.isdir(prev_project_path):
            root_dir = os.path.dirname(prev_project_path)
        else:
            root_dir = ""

        path = QtWidgets.QFileDialog.getExistingDirectory(None, "Set Luna project", root_dir)
        if path:
            project.Project.set(path)
        self.update_project()

    def exit_project(self):
        project.Project.exit()
        self.update_project()

    def showEvent(self, event):
        super(ProjectGroup, self).showEvent(event)
        self.update_project()
