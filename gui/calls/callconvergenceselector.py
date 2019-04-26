import csv
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtCore import Qt

from gui.views.py_files.convergenceselector import Ui_Dialog


class ConvergenceSelectorDialog(QDialog):
    def __init__(self, header_list: list):
        # ---------------------- dialog initialization ----------------------
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Window)
        self.setWindowModality(Qt.WindowModal)

        # ------------------------------ WidgetInitialization ------------------------------
        self.ui.comboBox.addItems(header_list)

        # ------------------------------ Signals/Slots ------------------------------
        self.ui.comboBox.currentIndexChanged.connect(self.indexChanged)

        # ------------------------------ Internal Variables ------------------------------
        self.status_index = None

    def indexChanged(self):
        self.status_index = self.ui.comboBox.currentIndex()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    header_list = ['case', 'status', 'rr', 'df', 'd', 'xb', 'b', 'qr', 'l', 'v', 'f', 'xd']
    status_index = 0
    w = ConvergenceSelectorDialog(header_list, status_index)
    w.show()

    if w.exec():
        print(status_index)

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
