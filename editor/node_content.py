from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets


class QLNodeContentWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(QLNodeContentWidget, self).__init__(parent)

        self.create_widgets()
        self.create_layouts()

    def create_widgets(self):
        self.label_wgt = QtWidgets.QLabel("Some title")

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.label_wgt)
        self.main_layout.addWidget(QtWidgets.QTextEdit("foo"))
        self.setLayout(self.main_layout)
