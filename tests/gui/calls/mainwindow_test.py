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
    w.setTreeTxtFilesPath(stream_file, blocks_file)
    w.show()

    sys.exit(app.exec_())
