import os

from PySide2 import QtWidgets
from PySide2 import QtCore

from functools import partial
import pymel.core as pm

from Luna import Config
from Luna import Logger
from Luna import ProjectVars
from Luna.utils import pysideFn
from Luna.utils import environFn
from Luna.utils import fileFn
from Luna.interface import shared_widgets
from Luna.workspace import project
from Luna.workspace.asset import Asset
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
        self.project_grp = ProjectGroup()
        self.asset_grp = AssetGroup()
        self.scroll_wgt.add_widget(self.project_grp)
        self.scroll_wgt.add_widget(self.asset_grp)
        self.scroll_wgt.content_layout.addStretch()

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.scroll_wgt)
        self.setLayout(self.main_layout)

    def create_connections(self):
        self.project_grp.name_lineedit.textChanged.connect(self.asset_grp.update_asset_data)
        self.project_grp.name_lineedit.textChanged.connect(self.asset_grp.update_asset_completion)
        self.project_grp.name_lineedit.textChanged.connect(lambda text: self.asset_grp.asset_set_button.setEnabled(bool(text)))
        self.project_grp.exit_btn.clicked.connect(self.asset_grp.update_asset_data)
        self.project_grp.exit_btn.clicked.connect(self.asset_grp.reset_asset_data)


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


class AssetGroup(QtWidgets.QGroupBox):

    ASSET_TYPES = ["character", "prop", "vehicle", "enviroment", "other"]

    def __init__(self, title="Asset", parent=None):
        super(AssetGroup, self).__init__(title, parent)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.asset_type_cmbox = QtWidgets.QComboBox()
        self.asset_type_cmbox.addItems(AssetGroup.ASSET_TYPES)
        self.asset_name_lineedit = QtWidgets.QLineEdit()
        self.asset_name_lineedit.setPlaceholderText("Name")
        self.asset_set_button = QtWidgets.QPushButton("Set")
        self.asset_set_button.setMinimumWidth(50)

        self.tree_model = QtWidgets.QFileSystemModel()
        # self.tree_model.setNameFilters(["*.POSE"])
        self.tree_model.setNameFilterDisables(False)
        self.file_tree = QtWidgets.QTreeView()
        self.file_tree.setModel(self.tree_model)
        self.file_tree.hideColumn(1)
        self.file_tree.hideColumn(2)
        self.file_tree.setColumnWidth(0, 200)
        self.file_tree.setMinimumWidth(200)

        self.model_path_wgt = shared_widgets.PathWidget(mode=shared_widgets.PathWidget.Mode.EXISTING_FILE,
                                                        label_text="Model file: ",
                                                        dialog_label="Select model file")
        self.rig_path_wgt = shared_widgets.PathWidget(mode=shared_widgets.PathWidget.Mode.EXISTING_FILE,
                                                      label_text="Latest rig: ")
        self.model_open_btn = QtWidgets.QPushButton("open")
        self.model_reference_btn = QtWidgets.QPushButton(pysideFn.get_QIcon("reference.svg", maya_icon=True), "")
        self.rig_open_btn = QtWidgets.QPushButton("open")
        self.rig_reference_btn = QtWidgets.QPushButton(pysideFn.get_QIcon("reference.svg", maya_icon=True), "")
        self.model_path_wgt.add_widget(self.model_open_btn)
        self.model_path_wgt.add_widget(self.model_reference_btn)
        self.rig_path_wgt.add_widget(self.rig_open_btn)
        self.rig_path_wgt.add_widget(self.rig_reference_btn)
        self.rig_path_wgt.browse_button.hide()

    def create_layouts(self):
        self.basic_info_layout = QtWidgets.QHBoxLayout()
        self.basic_info_layout.setContentsMargins(0, 0, 0, 0)
        self.basic_info_layout.addWidget(QtWidgets.QLabel("Type:"))
        self.basic_info_layout.addWidget(self.asset_type_cmbox)
        self.basic_info_layout.addWidget(self.asset_name_lineedit)
        self.basic_info_layout.addWidget(self.asset_set_button)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.basic_info_layout)
        self.main_layout.addWidget(self.file_tree)
        self.main_layout.addWidget(self.model_path_wgt)
        self.main_layout.addWidget(self.rig_path_wgt)
        # self.main_layout.addWidget(self.frame_tree_wgt)
        self.setLayout(self.main_layout)

    def create_connections(self):
        self.asset_set_button.clicked.connect(self.set_asset)
        self.asset_type_cmbox.currentIndexChanged.connect(self.update_asset_completion)
        self.model_path_wgt.line_edit.textChanged.connect(self.save_model_path)
        self.model_open_btn.clicked.connect(partial(self.open_asset_file, "model"))
        self.model_reference_btn.clicked.connect(partial(self.open_asset_file, "model", True))
        self.rig_open_btn.clicked.connect(partial(self.open_asset_file, "rig"))
        self.rig_reference_btn.clicked.connect(partial(self.open_asset_file, "rig", True))

    @QtCore.Slot()
    def set_asset(self):
        current_project = environFn.get_project_var()
        asset_name = self.asset_name_lineedit.text()
        if not asset_name:
            QtWidgets.QMessageBox.warning(self, "Required field", "Asset name is required!")
            return
        asset_type = self.asset_type_cmbox.currentText().lower()
        asset_path = os.path.join(current_project.path, asset_type + "s", asset_name)
        asset_path = os.path.normpath(asset_path)
        if not os.path.isdir(asset_path):
            reply = QtWidgets.QMessageBox.question(self, "Missing asset", "Asset {0} doesn't exist. Create it?".format(asset_name))
            if not reply == QtWidgets.QMessageBox.Yes:
                return
        new_asset = Asset(asset_name, asset_type)
        self.update_asset_data()

    @QtCore.Slot()
    def update_asset_data(self):
        current_project = environFn.get_project_var()  # type: project.Project
        current_asset = environFn.get_asset_var()  # type: Asset
        if not current_project or not current_asset:
            self.reset_asset_data()
            return

        self.asset_name_lineedit.setText(current_asset.name)
        self.asset_type_cmbox.setCurrentText(current_asset.type)
        self.model_path_wgt.line_edit.setText(current_asset.model_path)
        self.rig_path_wgt.line_edit.setText(current_asset.latest_rig_path)
        self.tree_model.setRootPath(current_asset.path)
        self.file_tree.setRootIndex(self.tree_model.index(current_asset.path))

    def reset_asset_data(self):
        current_project = environFn.get_project_var()  # type: project.Project
        if not current_project:
            root_path = "~"
        else:
            root_path = current_project.path
        self.model_path_wgt.line_edit.clear()
        self.rig_path_wgt.line_edit.clear()
        self.tree_model.setRootPath(root_path)
        self.file_tree.setRootIndex(self.tree_model.index(root_path))

    @QtCore.Slot()
    def update_asset_completion(self):
        current_project = environFn.get_project_var()  # type: project.Project
        if not current_project:
            self.asset_name_lineedit.setCompleter(None)
            return
        project_meta = current_project.meta_data
        asset_list = project_meta.get(self.asset_type_cmbox.currentText() + "s", [])
        if not asset_list:
            self.asset_name_lineedit.setCompleter(None)
            return

        completer = QtWidgets.QCompleter(asset_list)
        self.asset_name_lineedit.setCompleter(completer)

    @QtCore.Slot()
    def open_asset_file(self, file_type, reference=False):
        if file_type == "model":
            file_path = self.model_path_wgt.line_edit.text()
        elif file_type == "rig":
            file_path = self.rig_path_wgt.line_edit.text()

        if not os.path.isfile(file_path):
            Logger.warning("Invalid file path: {0}".format(file_path))
            return

        if reference:
            pm.createReference(file_path)
        else:
            pm.openFile(file_path, f=1)

    @QtCore.Slot()
    def save_model_path(self):
        current_asset = environFn.get_asset_var()  # type: Asset
        if not current_asset:
            return
        if self.model_path_wgt.line_edit.text() == current_asset.model_path:
            return
        current_asset.set_data("model", self.model_path_wgt.line_edit.text())
        Logger.info("Set asset model to {0}".format(self.model_path_wgt.line_edit.text()))
