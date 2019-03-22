import pathlib
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from gui.views.py_files.mainwindow import *
from gui.calls.callsimulationtree import LoadSimulationTreeDialog


class MainWindow(QMainWindow):

    def __init__(self):
        # initialization
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # internal variables initialization
        self.sim_filename = ""

        # signal/socket connections
        self.ui.buttonOpenSimFile.clicked.connect(self.openSimFileDialog)
        # self.ui.buttonLoadVariables.clicked.connect()

    # open simulation file
    def openSimFileDialog(self):
        homedir = str(pathlib.Path.home())  # home directory (platform independent)
        sim_filename, sim_filetype = QFileDialog.getOpenFileName(self, "Select .bkp simulation file", homedir,
                                                                 "BKP files (*.bkp);; Input files (*.inp)")

        if sim_filename == "" or (sim_filetype != "BKP files (*.bkp)" and sim_filetype != "Input files (*.inp)"):
            # user canceled the file dialog or selected invalid file
            if self.ui.textBrowserSimFile.styleSheet() != "color: blue":  # if there isn't an invalid path already
                self.ui.textBrowserSimFile.setText("Invalid or no file selected.")
                self.ui.textBrowserSimFile.setStyleSheet("color: red")
                self.ui.buttonLoadVariables.setEnabled(False)  # deactivate load button

        else:
            # it's a valid file. Set its path as string and color. Also make its filepath available to the ui
            self.sim_filename = sim_filename
            self.ui.textBrowserSimFile.setText(sim_filename)
            self.ui.textBrowserSimFile.setStyleSheet("color: blue")
            self.ui.buttonLoadVariables.setEnabled(True)  # deactivate load button

    # open simulationtree dialog
    def openSimTreeDialog(self):
        if self.sim_filename != "":
            dialog = LoadSimulationTreeDialog()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()

    sys.exit(app.exec_())
