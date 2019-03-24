from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QEvent, QThread, pyqtSignal, QEventLoop
from PyQt5.QtGui import QBrush, QStandardItemModel
from PyQt5.QtWidgets import QDialog, QApplication, QProgressDialog

from gui.models.load_simulation import read_simulation_tree_from_fileobject, read_simulation_tree_from_path, \
    construct_tree_items
from gui.models.sim_connections import AspenConnection
from gui.views.py_files.loadSimulationTree import Ui_Dialog


class ComboboxDelegate(QtWidgets.QItemDelegate):

    def createEditor(self, parent, option, index):
        # Returns the widget used to edit the item specified by index for editing.
        # The parent widget and style option are used to control how the editor widget appears.
        combo_box = QtWidgets.QComboBox(parent)
        li = ["Manipulated (MV)", "Disturbance (d)"]
        combo_box.addItems(li)
        return combo_box

    # def setEditorData(self, combo_box, index):
        # Sets the data to be displayed and edited by the editor from the data model item specified by the model index.
        # combo_box.setCurrentIndex(0)

    def setModelData(self, combo_box, model, index):
        # Gets data from the editor widget and stores it in the specified model at the item index.
        value = combo_box.itemText(combo_box.currentIndex())

        model.setData(index, value, Qt.EditRole)
        model.setData(index, QBrush(Qt.white), Qt.BackgroundRole)  # paints the cell background to white

    def updateEditorGeometry(self, editor, option, index):
        # Updates the editor for the item specified by index according to the style option given.
        editor.setGeometry(option.rect)


class LoadSimulationTreeDialog(QDialog):
    def __init__(self, bkp_file_path, streams_file_txt_path=None, blocks_file_txt_path=None):
        """

        :param bkp_file_path:
        :param streams_file_txt_path:
        :param blocks_file_txt_path:
        """
        self.bkp_path = bkp_file_path  # temporary bkp file path
        self.streams_file_txt_path = streams_file_txt_path  # in case the text tree file is available
        self.blocks_file_txt_path = blocks_file_txt_path

        super().__init__()  # initialize the QDialog
        self.ui = Ui_Dialog()  # instantiate the Dialog Window
        self.ui.setupUi(self)  # call the setupUi function to create and lay the window)

        self.ui.pushButtonOK.clicked.connect(self.okButtonPressed)  # closes window when button is pressed
        self.ui.pushButtonLoadTreeFromFile.clicked.connect(self.loadSimTreeButtonPressed)

        self.ui.treeViewInput.doubleClicked.connect(self.treeDoubleClick)  # assign double click event
        self.ui.treeViewOutput.doubleClicked.connect(self.treeDoubleClick)

        self.ui.tableWidgetInput.setColumnWidth(0, 450)  # first column resizing
        self.ui.tableWidgetOutput.setColumnWidth(0, 450)

        # create the model for the tree
        self.model_tree_input = QStandardItemModel()
        self.model_tree_output = QStandardItemModel()

        self.model_tree_input.setHorizontalHeaderLabels(['Input variables'])
        self.model_tree_output.setHorizontalHeaderLabels(['Output variables'])

        self.ui.treeViewInput.setModel(self.model_tree_input)
        self.ui.treeViewOutput.setModel(self.model_tree_output)

        # make the qtreeview headers bold
        self.ui.treeViewInput.header().setStyleSheet('QWidget { font: bold }')
        self.ui.treeViewOutput.header().setStyleSheet('QWidget { font: bold }')

        # values to be returned
        self.return_data = []

    def keyPressEvent(self, event):
        """
        keyPressEvent override of the QDialog class to extend keyboard interaction with the tables (i.e. delete rows)

        Parameters
        ----------
        event
        """
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Delete:  # if delete key was pressed
            widget = QApplication.focusWidget()  # get the widget which has focus
            if widget.objectName() == self.ui.tableWidgetInput.objectName() or \
                    widget.objectName() == self.ui.tableWidgetOutput.objectName():  # and is the table widget
                table_model = widget.selectionModel()
                indices = table_model.selectedRows()

                for index in indices:
                    widget.removeRow(index.row())  # delete selected rows

    def treeDoubleClick(self):
        """
        Event handling associated with a double click of a single LEAF node of the tree
        """
        tree_name = self.sender().objectName()

        tree_view = self.ui.treeViewInput if tree_name == 'treeViewInput' else self.ui.treeViewOutput

        table_view = self.ui.tableWidgetInput if tree_name == 'treeViewInput' else self.ui.tableWidgetOutput

        # get QModelIndex object of selected item. (It's a "pointer" in the QStandardModelItem)
        index_selected = tree_view.currentIndex()

        # get tree model
        tree_model = tree_view.model()

        if not tree_model.itemFromIndex(index_selected).hasChildren():
            # Only proceed if the selected node is a leaf (i.e. has no children)

            # get QStandardItem of the node clicked
            parent_node_std_item = tree_model.itemFromIndex(index_selected).parent()

            # construct the node path
            branch_list = [tree_model.data(index_selected).lstrip()]  # initialization

            while parent_node_std_item is not None:
                parent_node_name = parent_node_std_item.text().lstrip()
                branch_list.append(parent_node_name)
                parent_node_std_item = parent_node_std_item.parent()

            # create full path name
            branch_str = '\\' + '\\'.join(list(reversed(branch_list)))

            # verify if the entry is already in the table
            row_position = table_view.rowCount()  # count the current number of rows

            if row_position != 0:  # table is not empty
                row_list = []
                for i in range(row_position):
                    row_list.append(table_view.model().index(i, 0).data())  # get all rows in table

                if branch_str not in row_list:  # there isn't the value in table. Insert it
                    table_view.insertRow(row_position)

                    table_item_path = QtWidgets.QTableWidgetItem(branch_str)
                    table_item_type = QtWidgets.QTableWidgetItem('Choose a type')

                    table_item_path.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # disable edit of the first col
                    table_view.setItem(row_position, 0, table_item_path)
                    default_alias = 'Alias_' + str(row_position) if table_view.objectName() == 'tableWidgetInput' \
                        else 'CV_Alias_' + str(row_position)
                    table_view.setItem(row_position, 1, QtWidgets.QTableWidgetItem(default_alias))
                    table_view.setItem(row_position, 2, table_item_type)

                    table_item_type.setData(Qt.BackgroundRole, QBrush(Qt.red))  # paints the cell background to red

                else:
                    # warn the user
                    msg_box = QtWidgets.QMessageBox()
                    msg_box.setIcon(QtWidgets.QMessageBox.Warning)
                    msg_box.setText("The selected variable is already the table!")
                    msg_box.setWindowTitle("Duplicated variable")
                    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)

                    msg_box.exec()
            else:
                table_view.insertRow(row_position)  # insert an empty row

                table_item_path = QtWidgets.QTableWidgetItem(branch_str)
                table_item_type = QtWidgets.QTableWidgetItem('Choose a type')

                table_item_path.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # disable edit of the first col
                table_view.setItem(row_position, 0, table_item_path)
                default_alias = 'Alias_' + str(row_position) if table_view.objectName() == 'tableWidgetInput' \
                    else 'CV_Alias_' + str(row_position)
                table_view.setItem(row_position, 1, QtWidgets.QTableWidgetItem(default_alias))
                table_view.setItem(row_position, 2, table_item_type)

                table_item_type.setData(Qt.BackgroundRole, QBrush(Qt.red))  # paints the cell background to red

                if table_view.objectName() == 'tableWidgetInput':
                    # set the combobox delegate for type column
                    delegate = ComboboxDelegate()
                    table_view.setItemDelegateForColumn(2, delegate)

    def okButtonPressed(self):
        # read the data from the tables
        in_table = self.ui.tableWidgetInput
        out_table = self.ui.tableWidgetOutput

        in_model = in_table.model()
        input_data = []
        for row in range(in_model.rowCount()):
            input_data.append([in_model.data(in_model.index(row, 0)),
                               in_model.data(in_model.index(row, 1)),
                               in_model.data(in_model.index(row, 2))])

        out_model = out_table.model()
        output_data = []
        for row in range(out_model.rowCount()):
            output_data.append([out_model.data(out_model.index(row, 0)),
                                out_model.data(out_model.index(row, 1))])

        if any('Choose a type' in input_data_row for input_data_row in input_data):
            # the user did not choose a type for a selected variable. Alert him to do so.
            msg_box = QtWidgets.QMessageBox()
            msg_box.setIcon(QtWidgets.QMessageBox.Warning)
            msg_box.setText("At least one of the selected input variables does not have a defined type (either MV or "
                            "d). You have to define it for all of them!")
            msg_box.setWindowTitle("Input variable without type detected")
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)

            msg_box.exec()

        else:
            # both tables empty or both filled, proceed as normal
            self.return_data.append(input_data)
            self.return_data.append(output_data)

            self.accept()  # close window with accept, so that values are allowed to be returned

    def loadSimTreeButtonPressed(self):
        """
        Open connection with simulation engine and loads the variable tree
        """
        self.ui.pushButtonLoadTreeFromFile.setEnabled(False)
        self.ui.pushButtonOK.setEnabled(False)

        progress_dialog = QProgressDialog('Please wait while the variable tree is loaded...', None, 0, 5, self)
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setWindowTitle('Loading')
        progress_dialog.show()
        progress_dialog.setValue(0)

        progress_dialog.setLabelText('Please wait while the variable tree is loaded...\nOpening connection...')

        if self.streams_file_txt_path is not None and self.blocks_file_txt_path is not None:
            progress_dialog.setValue(1)
            # if tree text file containing the variables are specified do not load from bkp file
            progress_dialog.setLabelText(
                'Please wait while the variable tree is loaded...\nLoading Stream variables...')
            stream_raw = read_simulation_tree_from_path(self.streams_file_txt_path)
            progress_dialog.setValue(2)

            progress_dialog.setLabelText('Please wait while the variable tree is loaded...\nLoading Block variables...')
            blocks_raw = read_simulation_tree_from_path(self.blocks_file_txt_path)
            progress_dialog.setValue(3)

        else:
            # Open the connection
            aspen_com = AspenConnection(self.bkp_path)
            progress_dialog.setValue(1)

            # load the tree from the connection file
            progress_dialog.setLabelText('Please wait while the variable tree is loaded...\nLoading Stream variables...')

            stream_raw = read_simulation_tree_from_fileobject(aspen_com.GenerateTreeFile(r"\Data\Streams"))
            progress_dialog.setValue(2)

            progress_dialog.setLabelText('Please wait while the variable tree is loaded...\nLoading Block variables...')

            blocks_raw = read_simulation_tree_from_fileobject(aspen_com.GenerateTreeFile(r"\Data\Blocks"))
            progress_dialog.setValue(3)

        # Populate the data

        # load the stream tree
        progress_dialog.setLabelText('Please wait while the variable tree is loaded...\nConstructing the trees...')

        stream_input, stream_output = construct_tree_items(stream_raw)
        self.model_tree_input.appendRow(stream_input)
        self.model_tree_output.appendRow(stream_output)
        progress_dialog.setValue(4)

        # load the blocks tree
        blocks_input, blocks_output = construct_tree_items(blocks_raw)
        self.model_tree_input.appendRow(blocks_input)
        self.model_tree_output.appendRow(blocks_output)
        progress_dialog.setValue(5)

        # enable ok and load buttons
        self.ui.pushButtonLoadTreeFromFile.setEnabled(True)
        self.ui.pushButtonOK.setEnabled(True)


class AspenThread(QThread):
    notifyProgress = pyqtSignal(int)
    taskFinished = pyqtSignal()

    def run(self):
        import time
        for i in range(101):
            self.notifyProgress.emit(i)
            time.sleep(0.01)
        self.taskFinished.emit()

        # Open the connection

        # aspen_com = AspenConnection(self.bkp_path)
        # self.notifyProgress
        #
        # stream_raw = read_simulation_tree_from_fileobject(aspen_com.GenerateTreeFile(r"\Data\Streams"))
        # blocks_raw = read_simulation_tree_from_fileobject(aspen_com.GenerateTreeFile(r"\Data\Blocks"))
        #
        # # Populate the data
        #
        # # load the stream tree
        # stream_input, stream_output = construct_tree_items(stream_raw)
        # self.model_tree_input.appendRow(stream_input)
        # self.model_tree_output.appendRow(stream_output)
        #
        # # load the blocks tree
        # blocks_input, blocks_output = construct_tree_items(blocks_raw)
        # self.model_tree_input.appendRow(blocks_input)
        # self.model_tree_output.appendRow(blocks_output)


if __name__ == '__main__':
    import sys
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

    ex_code = w.exec_()
    if ex_code:
        a = w.return_data
        print(a)

    sys.exit(app.exec_())