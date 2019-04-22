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
        self.setWindowTitle('Metacontrol - untitled.mtc')

        self.ui.tabMainWidget.setTabEnabled(1, False)  # disable the sampling tab

        self.save_file_name = ""

        # --------------------------------- load the tab widgets ---------------------------------
        self.loadsimtab = LoadSimTab(self.application_database, parent_tab=self.ui.simulationTab,
                                     parent_tab_widget=self.ui.tabMainWidget)
        self.doeTab = DoeTab(self.application_database, parent_widget=self.ui.samplingTab)

        # --------------------------------- Connections ---------------------------------
        self.ui.actionOpen.triggered.connect(self.openFile)
        self.ui.actionSave.triggered.connect(self.saveFile)
        self.ui.actionSave_As.triggered.connect(self.saveFileAs)

    def openFile(self):
        # Prompt the user to select the .mtc file
        homedir = str(pathlib.Path.home())
        mtc_filename, _ = QFileDialog.getOpenFileName(self, "Select the .mtc simulation file", homedir,
                                                      "Metacontrol files (*.mtc)")
        if mtc_filename != "":  # user did not click cancel on the dialog
            self.save_file_name = mtc_filename
            self.setWindowTitle("Metacontrol - " + mtc_filename)
            sim_file_name = read_data(mtc_filename, self.application_database)

            if pathlib.Path(sim_file_name).is_file():
                # file exists, place it
                self.loadsimtab.sim_filename = sim_file_name
                self.application_database.setSimulationFilePath(sim_file_name)
                self.loadsimtab.ui.textBrowserSimFile.setText(sim_file_name)
                self.loadsimtab.ui.textBrowserSimFile.setStyleSheet("")
                self.loadsimtab.ui.buttonLoadVariables.setEnabled(True)  # activate load button
            else:
                if sim_file_name == "":
                    self.loadsimtab.ui.textBrowserSimFile.setText("Select a simulation file.")
                self.loadsimtab.sim_filename = ""
                self.loadsimtab.ui.textBrowserSimFile.setStyleSheet("color: red")
                self.loadsimtab.ui.buttonLoadVariables.setEnabled(False)  # deactivate load button

            # clear the tables and place the data
            self.loadsimtab.ui.tableWidgetAliasDisplay.setRowCount(0)
            self.loadsimtab.ui.tableWidgetExpressions.setRowCount(0)
            self.loadsimtab.loadDataIntoAliasTables()
            self.loadsimtab.loadDataIntoExpressionTables()

    def saveFile(self):
        # get the current file name
        current_mtc_name = self.windowTitle().split(' - ')[1]

        if pathlib.Path(current_mtc_name).is_file():
            # current file does exists
            write_data(current_mtc_name, self.loadsimtab.sim_filename, self.application_database)
        else:
            # file doesn't exist, prompt the user
            self.saveFileAs()

    def saveFileAs(self):
        # prompt the user to choose file location and name to save
        mtc_file_name, _ = QFileDialog.getSaveFileName(self, "Select where to save the .mtc file",
                                                             str(pathlib.Path.home()), "Metacontrol files (*.mtc)")
        if mtc_file_name == '':
            # user canceled the dialog
            pass
        else:
            self.save_file_name = mtc_file_name
            # change the window title
            self.setWindowTitle("Metacontrol - " + mtc_file_name)

            # write the data
            write_data(mtc_file_name, self.loadsimtab.sim_filename, self.application_database)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()

    sys.exit(app.exec_())
