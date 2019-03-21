import pathlib
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from gui.views.py_files.mainwindow import *


class MyForm(QMainWindow):

    def __init__(self):
        # initialization
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # internal variables initialization
        self.sim_filename = ""

        # signal/socket connections
        self.ui.buttonOpenSimFile.clicked.connect(self.openSimFileDialog)

    # open simulation file
    def openSimFileDialog(self):
        homedir = str(pathlib.Path.home())  # home directory (platform independent)
        sim_filename, sim_filetype = QFileDialog.getOpenFileName(self, "Select .bkp simulation file", homedir,
                                                                 "BKP files (*.bkp);; Text files (*.txt)")

        if sim_filename == "" or sim_filetype != "BKP files (*.bkp)":
            # user canceled the file dialog or selected invalid file
            self.ui.textBrowserSimFile.setText("Invalid or no file selected.")
            self.ui.textBrowserSimFile.setStyleSheet("color: red")

        else:
            # it's a valid file. Set its path as string and color. Also make its filepath available to the ui
            self.sim_filename = sim_filename
            self.ui.textBrowserSimFile.setText(sim_filename)
            self.ui.textBrowserSimFile.setStyleSheet("color: blue")


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = MyForm()
    w.show()

    sys.exit(app.exec_())
