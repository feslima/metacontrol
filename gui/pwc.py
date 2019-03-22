import sys
from gui.calls.callmainwindow import MainWindow

from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)

w = MainWindow()
w.show()


def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

    # Back up the reference to the exceptionhook


sys._excepthook = sys.excepthook

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook

sys.exit(app.exec_())