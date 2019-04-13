from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt

from gui.views.py_files.mainwindow import *
from gui.models.data_storage import DataStorage
from gui.calls.callloadsimtab import LoadSimTab


class MainWindow(QMainWindow):
    def __init__(self):
        # AbstractItem rows database initialization for tree view in load simulation variables dialog
        self.application_database = DataStorage()

        # --------------------------------- UI Initialization ---------------------------------
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowState(Qt.WindowMaximized)

        self.ui.tabMainWidget.setTabEnabled(1, False)
        # --------------------------------- load the tab widgets ---------------------------------
        self.loadsimtab = LoadSimTab(self.application_database, self.ui.simulationTab, self.ui.tabMainWidget)



if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()

    sys.exit(app.exec_())
