from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtGui import QIntValidator

from gui.views.py_files.lhssettings import Ui_Dialog


class LhsSettingsDialog(QDialog):
    def __init__(self, application_database):
        # ------------------------------ Form Initialization ----------------------------
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.application_database = application_database

        # ------------------------------ WidgetInitialization ------------------------------
        self.current_doe_data = self.application_database.doe_data
        self.lhs_data = self.current_doe_data['lhs']
        self.ui.lineEditNSamples.setText(str(self.lhs_data['n_samples']))
        self.ui.lineEditNIter.setText(str(self.lhs_data['n_iter']))
        self.ui.checkBoxIncVertices.setChecked(self.lhs_data['inc_vertices'])

        # validators
        n_samp_validator = QIntValidator(self.ui.lineEditNSamples)
        self.ui.lineEditNSamples.setValidator(n_samp_validator)
        n_iter_validator = QIntValidator(self.ui.lineEditNIter)
        self.ui.lineEditNIter.setValidator(n_iter_validator)

        # ------------------------------ Signals/Slots ------------------------------
        self.ui.buttonBox.accepted.connect(self.setLhsData)

    def setLhsData(self):
        self.lhs_data['n_samples'] = int(self.ui.lineEditNSamples.text())
        self.lhs_data['n_iter'] = int(self.ui.lineEditNIter.text())
        self.lhs_data['inc_vertices'] = self.ui.checkBoxIncVertices.isChecked()
        self.application_database.doe_data = self.current_doe_data


if __name__ == "__main__":
    import sys
    from gui.models.data_storage import DataStorage

    from tests_.gui.mock_data import doe_table_data

    app = QApplication(sys.argv)

    mock_storage = DataStorage()
    mock_storage.doe_data = doe_table_data
    w = LhsSettingsDialog(mock_storage)
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

    if w.exec_():
        print(mock_storage.doe_data['lhs'])

    sys.exit(app.exec_())
