import sys
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtGui import QStandardItemModel
from gui.views.loadSimulationTree import *
from gui.models.load_simulation import construct_tree_items, read_simulation_tree


class MyForm(QDialog):
    def __init__(self, streams_file_path, blocks_file_path):
        super().__init__()  # initialize the QDialog
        self.ui = Ui_Dialog()  # instantiate the Dialog Window
        self.ui.setupUi(self)  # call the setupUi function to create and lay the window

        # create the model for the tree
        model_tree_input = QStandardItemModel()
        model_tree_ouput = QStandardItemModel()
        self.ui.treeViewInput.setModel(model_tree_input)
        self.ui.treeViewOutput.setModel(model_tree_ouput)

        # populate the data

        # Load the stream tree
        stream_raw = read_simulation_tree(streams_file_path)
        stream_input, stream_output = construct_tree_items(stream_raw)
        model_tree_input.appendRow(stream_input)
        model_tree_ouput.appendRow(stream_output)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    stream_file = "/home/felipe/Desktop/GUI/python/AspenTreeStreams - Input _ Output.txt"
    blocks_file = "/home/felipe/Desktop/GUI/python/AspenTreeBlocks - Input _ Output.txt"
    w = MyForm(stream_file)
    w.show()

    sys.exit(app.exec_())
