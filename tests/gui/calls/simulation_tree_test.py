import sys
from PyQt5.QtWidgets import QApplication

from gui.calls.callsimulationtree import LoadSimulationTreeDialog

if __name__ == '__main__':
    app = QApplication(sys.argv)

    import os

    if os.name == 'posix':
        stream_file = "/home/felipe/Desktop/GUI/python/AspenTreeStreams - Input _ Output.txt"
        blocks_file = "/home/felipe/Desktop/GUI/python/AspenTreeBlocks - Input _ Output.txt"
    elif os.name == 'nt':  # windows
        stream_file = r"C:\Users\Felipe\Desktop\GUI\python\AspenTreeStreams - Input & Output.txt"
        blocks_file = r"C:\Users\Felipe\Desktop\GUI\python\AspenTreeBlocks - Input & Output.txt"

    w = LoadSimulationTreeDialog(stream_file, blocks_file)
    w.show()

    sys.exit(app.exec_())
