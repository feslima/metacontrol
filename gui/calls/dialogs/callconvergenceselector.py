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

        # ------------------------------ WidgetInitialization ------------------------------
        self.ui.convergenceComboBox.addItems(['Select header'] + header_list)
        self.ui.convergenceComboBox.setCurrentIndex(0)

        # ------------------------------ Signals/Slots ------------------------------
        self.ui.convergenceComboBox.currentIndexChanged.connect(self.statusIndexChanged)
        self.ui.caseComboBox.currentIndexChanged.connect(self.caseIndexChanged)

        # ------------------------------ Internal Variables ------------------------------
        self.status_index = None
        self.case_name = 'None'
        self.header_list = header_list.copy()

    def statusIndexChanged(self):
        if self.ui.convergenceComboBox.currentText() == 'Select header':
            self.ui.caseComboBox.setEnabled(False)

        else:
            self.status_index = self.header_list.index(self.ui.convergenceComboBox.currentText())
            if self.status_index is not None:
                self.ui.caseComboBox.setEnabled(True)
                h_list = self.header_list.copy()
                h_list.remove(self.header_list[self.status_index])
                self.ui.caseComboBox.clear()
                self.ui.caseComboBox.addItems(['None'] + h_list)

            else:
                self.ui.caseComboBox.setEnabled(False)

    def caseIndexChanged(self):
        self.case_name = self.ui.caseComboBox.currentText()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    header_list = ['case', 'status', 'rr', 'df', 'd', 'xb', 'b', 'qr', 'l', 'v', 'f', 'xd']

    w = ConvergenceSelectorDialog(header_list)
    w.show()

    if w.exec():
        print(w.status_index)
        print(w.case_name)

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
