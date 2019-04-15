import pathlib
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.QtCore import Qt

from gui.views.py_files.mainwindow import *
from gui.models.data_storage import DataStorage, read_data, write_data
from gui.calls.callloadsimtab import LoadSimTab
from gui.calls.calldoetab import DoeTab


class MainWindow(QMainWindow):
    def __init__(self):
        # AbstractItem rows database initialization for tree view in load simulation variables dialog
        self.application_database = DataStorage()

        # --------------------------------- UI Initialization ---------------------------------
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowState(Qt.WindowMaximized)

        self.ui.tabMainWidget.setTabEnabled(1, False)  # disable the sampling tab

        # --------------------------------- Connections ---------------------------------
        self.ui.actionOpen.triggered.connect(self.openFile)
        self.ui.actionSave.triggered.connect(self.saveFile)

        # --------------------------------- load the tab widgets ---------------------------------
        self.loadsimtab = LoadSimTab(self.application_database, parent_tab=self.ui.simulationTab,
                                     parent_tab_widget=self.ui.tabMainWidget)
        self.doeTab = DoeTab(self.application_database, parent_widget=self.ui.samplingTab)

    def openFile(self):
        # Prompt the user to select the .mtc file
        homedir = str(pathlib.Path.home())
        mtc_filename, _ = QFileDialog.getOpenFileName(self, "Select the .mtc simulation file", homedir,
                                                      "Metacontrol files (*.mtc)")
        sim_file_name = read_data(mtc_filename, self.application_database)

        if pathlib.Path(sim_file_name).is_file():
            # file exists, place it
            self.loadsimtab.sim_filename = sim_file_name
            self.loadsimtab.ui.textBrowserSimFile.setText(sim_file_name)
            self.loadsimtab.ui.textBrowserSimFile.setStyleSheet("")
            self.loadsimtab.ui.buttonLoadVariables.setEnabled(True)  # activate load button
        else:
            self.loadsimtab.sim_filename = ""
            self.loadsimtab.ui.textBrowserSimFile.setText(sim_file_name)
            self.loadsimtab.ui.textBrowserSimFile.setStyleSheet("color: red")
            self.loadsimtab.ui.buttonLoadVariables.setEnabled(False)  # deactivate load button
            self.loadsimtab.ui.setToolTip("This file is not valid. Check if it exists in the specified directory.")

        # clear the tables and place the data
        self.loadsimtab.ui.tableWidgetAliasDisplay.setRowCount(0)
        self.loadsimtab.ui.tableWidgetExpressions.setRowCount(0)
        self.loadsimtab.loadDataIntoAliasTables()
        self.loadsimtab.loadDataIntoExpressionTables()

    def saveFile(self):
        pass


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()

    sys.exit(app.exec_())
