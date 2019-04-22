from PyQt5.QtWidgets import QApplication
import qdarkstyle
from gui.calls.callmainwindow import MainWindow


if __name__ == '__main__':
    import sys

    # dummy text files for testing
    stream_file = r"C:\Users\Felipe\Desktop\GUI\python\AspenTreeStreams - Input & Output.txt"
    blocks_file = r"C:\Users\Felipe\Desktop\GUI\python\AspenTreeBlocks - Input & Output.txt"

    app = QApplication(sys.argv)
    w = MainWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    w.loadsimtab.setTreeTxtFilesPath(stream_file, blocks_file)
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
