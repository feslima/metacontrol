import sys
import os
import tempfile
import traceback
from gui.calls.callmainwindow import MainWindow

from PyQt5.QtWidgets import QApplication, QMessageBox

# app initialization
app = QApplication(sys.argv)

w = MainWindow()
w.show()


def my_exception_hook(exctype, value, tback):
    # Print the error and traceback
    # print(exctype, value, traceback)
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Critical)
    error_dialog.setText(traceback.format_exception(exctype, value, tback)[-1])
    error_dialog.setDetailedText(''.join(traceback.format_exception(exctype, value, tback)))

    error_dialog.exec_()
    # Call the normal Exception hook after
    sys.__excepthook__(exctype, value, tback)
    sys.exit()

    # Back up the reference to the exceptionhook

sys._excepthook = sys.excepthook

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook

sys.exit(app.exec_())