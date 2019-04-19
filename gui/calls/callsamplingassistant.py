from PyQt5.QtWidgets import QApplication, QDialog

from gui.views.py_files.samplingassistant import Ui_Dialog
from gui.calls.calllhssettings import LhsSettingsDialog

# TODO: (19/04/2016) implement sampling procedure and visualization

class SamplingAssistantDialog(QDialog):
    def __init__(self, application_database):
        # ------------------------------ Form Initialization ----------------------------
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.application_database = application_database

        # ------------------------------ WidgetInitialization ------------------------------

        # ------------------------------ Signals/Slots ------------------------------
        self.ui.sampDataPushButton.clicked.connect(self.sampleData)
        self.ui.lhsSettingsPushButton.clicked.connect(self.openLhsSettingsDialog)
        self.ui.cancelPushButton.clicked.connect(self.reject)

    def openLhsSettingsDialog(self):
        dialog = LhsSettingsDialog(self.application_database)
        dialog.exec_()

    def sampleData(self):
        self.accept()


if __name__ == "__main__":
    import sys
    from gui.models.data_storage import DataStorage

    app = QApplication(sys.argv)

    doe_table_data = {'mv': [{'name': 'rr', 'lb': 7., 'ub': 25.0},
                             {'name': 'df', 'lb': 0.1, 'ub': 0.9}],
                      'lhs': {'n_samples': 50, 'n_iter': 10, 'inc_vertices': False},
                      'csv': {'active': False,
                              'filepath': r'C:\Users\Felipe\PycharmProjects\metacontrol\tests\gui\csv_editor\column.csv',
                              'check_flags': [False, False, True, True, True, True, True, True, True, True, True, True],
                              'alias_list': ['rr', 'df', 'd', 'xb', 'b', 'qr', 'l', 'v', 'f', 'xd']}}
    mock_storage = DataStorage()
    mock_storage.setDoeData(doe_table_data)
    w = SamplingAssistantDialog(mock_storage)
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
