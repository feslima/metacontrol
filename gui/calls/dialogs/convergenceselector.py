from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt

from gui.views.py_files.convergenceselector import Ui_Dialog
from gui.models.data_storage import DataStorage


class ConvergenceSelectorDialog(QDialog):
    def __init__(self, headers_list: list, application_data: DataStorage,
                 mode: str = 'original'):
        """`mode` may assume two values: 'original' (default) or 'reduced'.
        """
        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # ------------------------ Internal Variables -------------------------
        self.app_data = application_data
        self.mode = mode
        # ----------------------- Widget Initialization -----------------------
        combo_box = self.ui.convergenceComboBox
        combo_box.addItems(['Select header'] + headers_list)
        combo_box.setCurrentIndex(0)

        self.ui.buttonBox.setEnabled(False)
        # --------------------------- Signals/Slots ---------------------------
        combo_box.currentIndexChanged.connect(self.select_status_index)

        # ---------------------------------------------------------------------

    def select_status_index(self):
        """Sets the convergence flag column index into the application data
        storage and enables/disable the buttonbox.
        """
        current_txt = self.ui.convergenceComboBox.currentText()
        if current_txt != 'Select header':
            if self.mode == 'original':
                self.app_data.doe_csv_settings['convergence_index'] = \
                    current_txt
            else:
                self.app_data.reduced_doe_csv_settings['convergence_index'] = \
                    current_txt

            self.ui.buttonBox.setEnabled(True)
        else:
            self.ui.buttonBox.setEnabled(False)


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook

    app = QApplication(sys.argv)

    header_list = ['case', 'status', 'rr', 'df',
                   'd', 'xb', 'b', 'qr', 'l', 'v', 'f', 'xd']
    ds = DataStorage()

    w = ConvergenceSelectorDialog(headers_list=header_list,
                                  application_data=ds)
    w.show()

    sys.excepthook = my_exception_hook

    sys.exit(app.exec_())
