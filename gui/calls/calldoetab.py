import pathlib
from PyQt5.QtWidgets import QApplication, QWidget, QHeaderView, QFileDialog, QTableWidgetItem
from PyQt5.QtCore import Qt

from gui.views.py_files.doetab import Ui_Form


class DoeTab(QWidget):
    def __init__(self, application_database, parent_widget=None):
        # ------------------------------ Form Initialization ----------------------------
        super().__init__()
        self.ui = Ui_Form()
        parent_widget = parent_widget if parent_widget is not None else self
        self.ui.setupUi(parent_widget)

        self.application_database = application_database

        # ------------------------------ WidgetInitialization ------------------------------
        self.ui.tableWidgetInputVariables.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tableWidgetResultsDoe.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # input vars
        # self.loadInputVariables()

        # ------------------------------ Signals/Slots ------------------------------
        self.ui.openCsvFilePushButton.clicked.connect(self.openCsvFileDialog)

    def openCsvFileDialog(self):
        homedir = str(pathlib.Path.home())  # home directory (platform independent)
        sim_filename, _ = QFileDialog.getOpenFileName(self, "Select .csv containing DOE data", homedir,
                                                      "CSV files (*.csv)")
        if sim_filename != "":
            self.ui.lineEditCsvFilePath.setText(sim_filename)

    def loadInputVariables(self):
        # load the MV aliases in the variable table
        input_alias_data = self.application_database.getInputTableData()

        mv_alias_list = [row['Alias'] for row in input_alias_data if row['Type'] == 'Manipulated (MV)']

        table_view = self.ui.tableWidgetInputVariables

        # clear the table rows
        table_view.setRowCount(0)

        # insert the aliases
        for row in range(len(mv_alias_list)):
            table_view.insertRow(row)
            alias_item = QTableWidgetItem(mv_alias_list[row])
            alias_item.setTextAlignment(Qt.AlignCenter)
            alias_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # disable the edit

            table_view.setItem(row, 0, alias_item)


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
