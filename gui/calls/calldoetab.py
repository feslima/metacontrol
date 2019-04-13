import pathlib
from PyQt5.QtWidgets import QApplication, QWidget, QHeaderView, QFileDialog
from PyQt5.QtCore import Qt

from gui.views.py_files.doetab import Ui_Form


class DoeTab(QWidget):
    def __init__(self, application_database, parent_widget=None):
        # ------------------------------ Form Initialization ----------------------------
        super().__init__()
        self.ui = Ui_Form()
        parent_widget = parent_widget if parent_widget is not None else self
        self.ui.setupUi(parent_widget)

        # ------------------------------ WidgetInitialization ------------------------------
        self.ui.tableWidgetInputVariables.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tableWidgetResultsDoe.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # ------------------------------ Signals/Slots ------------------------------
        self.ui.openCsvFilePushButton.clicked.connect(self.openCsvFileDialog)

    def openCsvFileDialog(self):
        homedir = str(pathlib.Path.home())  # home directory (platform independent)
        sim_filename, _ = QFileDialog.getOpenFileName(self, "Select .csv containing DOE data", homedir,
                                                      "CSV files (*.csv)")
        if sim_filename != "":
            self.ui.lineEditCsvFilePath.setText(sim_filename)


if __name__ == "__main__":
    import sys
    from gui.models.data_storage import DataStorage

    app = QApplication(sys.argv)
    w = DoeTab(DataStorage())
    w.show()


    def my_exception_hook(exctype, value, tback):
        # Print the error and traceback
        print(exctype, value, tback)
        # Call the normal Exception hook after
        sys.__excepthook__(exctype, value, tback)
        sys.exit()


    sys._excepthook = sys.excepthook

    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
