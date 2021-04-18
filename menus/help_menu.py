from PySide2 import QtWidgets
import luna
import luna.utils.pysideFn as pysideFn


class HelpMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super(HelpMenu, self).__init__("Help", parent)
        self.setTearOffEnabled(True)
        self.create_actions()
        self.create_sub_menus()
        self.populate()
        self.create_connections()

    def create_sub_menus(self):
        pass

    def create_actions(self):
        self.docs_action = QtWidgets.QAction(pysideFn.get_QIcon("help.png", maya_icon=True), "Documentation", self)

    def create_connections(self):
        pass

    def populate(self):
        self.addAction(self.docs_action)

    def update_actions_state(self):
        pass
