from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog, QApplication

from tests.gui.regex_test.expr_val import *


class RegExp(QDialog):
    def __init__(self):
        super().__init__()  # initialize the QDialog
        self.ui = Ui_Dialog()  # instantiate the Dialog Window
        self.ui.setupUi(self)  # call the setupUi function to create and lay the window)

        reg_ex = QRegExp("^[a-z$][a-z_$0-9]{7}$")
        input_validator = QRegExpValidator(reg_ex, self.ui.lineEdit)
        self.ui.lineEdit.setValidator(input_validator)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    w = RegExp()
    w.show()


    def my_exception_hook(exctype, value, tback):
        # Print the error and traceback
        print(exctype, value, tback)

        # Call the normal Exception hook after
        sys.__excepthook__(exctype, value, tback)
        sys.exit()

        # Back up the reference to the exceptionhook


    sys._excepthook = sys.excepthook

    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook

    sys.exit(app.exec_())
