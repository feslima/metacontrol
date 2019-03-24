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
        filepath = r"C:\Users\Felipe\Desktop\GUI\python\infill.bkp"

    # w = LoadSimulationTreeDialog(filepath)
    w = LoadSimulationTreeDialog(filepath, streams_file_txt_path=stream_file, blocks_file_txt_path=blocks_file)

    w.show()

    if w.exec_():  # if the OK button was pressed
        var_list = w.return_data

    sys.exit(app.exec_())
