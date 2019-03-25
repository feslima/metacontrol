from PyQt5.QtWidgets import QApplication

from gui.calls.callmainwindow import MainWindow
from gui.calls.callsimulationtree import LoadSimulationTreeDialog

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()

    sys.exit(app.exec_())
