from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QRegExp, QEvent
from PyQt5.QtGui import QBrush, QStandardItemModel, QRegExpValidator
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

    def setEditorData(self, combo_box, index):
        # Sets the data to be displayed and edited by the editor from the data model item specified by the model index.
        combo_box.showPopup()

    def setModelData(self, combo_box, model, index):
        # Gets data from the editor widget and stores it in the specified model at the item index.
        value = combo_box.itemText(combo_box.currentIndex())

        model.setData(index, value, Qt.EditRole)

        # paints the cell background back to original color
        original_backgrd_color = combo_box.palette().color(combo_box.backgroundRole())
        model.setData(index, QBrush(original_backgrd_color), Qt.BackgroundRole)

    def updateEditorGeometry(self, editor, option, index):
        # Updates the editor for the item specified by index according to the style option given.
        editor.setGeometry(option.rect)


class AliasEditorDelegate(QtWidgets.QItemDelegate):

    def createEditor(self, parent, option, index):
        line_editor = QtWidgets.QLineEdit(parent)
        reg_ex = QRegExp("^[a-z$][a-z_$0-9]{,9}$")
        input_validator = QRegExpValidator(reg_ex, line_editor)
        line_editor.setValidator(input_validator)

        return line_editor

    def setModelData(self, line_editor, model, index):
        text = line_editor.text()

        model.setData(index, text, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class LoadSimulationTreeDialog(QDialog):
    def __init__(self, bkp_file_path, gui_data_storage_object, streams_file_txt_path=None, blocks_file_txt_path=None):
        """

        :param bkp_file_path:
        """
        # TODO: check for duplicated aliases in tables
        self.bkp_path = bkp_file_path  # temporary bkp file path
        self.gui_data = gui_data_storage_object

        self.streams_file_txt_path = streams_file_txt_path
        self.blocks_file_txt_path = blocks_file_txt_path

        super().__init__()  # initialize the QDialog
        self.ui = Ui_Dialog()  # instantiate the Dialog Window
        self.ui.setupUi(self)  # call the setupUi function to create and lay the window)

        self.ui.pushButtonOK.clicked.connect(self.okButtonPressed)  # closes window when button is pressed
        self.ui.pushButtonLoadTreeFromFile.clicked.connect(self.loadSimTreeButtonPressed)

        self.ui.treeViewInput.doubleClicked.connect(self.treeDoubleClick)  # assign double click event
        self.ui.treeViewOutput.doubleClicked.connect(self.treeDoubleClick)

        self.ui.tableWidgetInput.setColumnWidth(0, 400)  # first column resizing
        self.ui.tableWidgetOutput.setColumnWidth(0, 450)

        # create the model for the tree if there wasn't one loaded in the database
        if self.gui_data.getInputTreeModel() is None:
            self.model_tree_input = QStandardItemModel()
            self.gui_data.setInputTreeModel(self.model_tree_input)
        else:
            self.model_tree_input = self.gui_data.getInputTreeModel()

        if self.gui_data.getOutputTreeModel() is None:
            self.model_tree_output = QStandardItemModel()
            self.gui_data.setOutputTreeModel(self.model_tree_output)
        else:
            self.model_tree_output = self.gui_data.getOutputTreeModel()

        # set the alias editor delegate for the alias column
        self._input_alias_delegate = AliasEditorDelegate()
        self._output_alias_delegate = AliasEditorDelegate()

        # why the self.: https://stackoverflow.com/questions/46746551/
        # how-do-i-set-item-delegates-for-multiple-columns-in-a-model-that-is-processed-by
        # The view does not take ownership of the delegate, so you must keep a reference to it yourself
        # (otherwise it will be garbage-collected by python):

        self.ui.tableWidgetInput.setItemDelegateForColumn(1, self._input_alias_delegate)
        self.ui.tableWidgetOutput.setItemDelegateForColumn(1, self._output_alias_delegate)

        # do the same to table data
        if self.gui_data.getInputTableData() is not None:
            self.insertDataOnTableCreation(self.ui.tableWidgetInput, self.gui_data.getInputTableData())

        if self.gui_data.getOutputTableData() is not None:
            self.insertDataOnTableCreation(self.ui.tableWidgetOutput, self.gui_data.getOutputTableData())

        # set the combobox delegate for type column
        delegate = ComboboxDelegate()
        self.ui.tableWidgetInput.setItemDelegateForColumn(2, delegate)

        self.model_tree_input.setHorizontalHeaderLabels(['Input variables'])
        self.model_tree_output.setHorizontalHeaderLabels(['Output variables'])

        self.ui.treeViewInput.setModel(self.model_tree_input)
        self.ui.treeViewOutput.setModel(self.model_tree_output)

        # make the qtreeview headers bold
        self.ui.treeViewInput.header().setStyleSheet('QWidget { font: bold }')
        self.ui.treeViewOutput.header().setStyleSheet('QWidget { font: bold }')

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
                indexes = table_model.selectedIndexes()

                for index in indexes:
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

                if branch_str not in row_list:  # the value isn't in the table. Insert it
                    self.insertNewSingleRow(table_view, row_position, branch_str)

                else:
                    # warn the user
                    msg_box = QtWidgets.QMessageBox()
                    msg_box.setIcon(QtWidgets.QMessageBox.Warning)
                    msg_box.setText("The selected variable is already the table!")
                    msg_box.setWindowTitle("Duplicated variable")
                    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)

                    msg_box.exec()
            else:
                self.insertNewSingleRow(table_view, row_position, branch_str)

    def insertNewSingleRow(self, table_view, row_position, branch_str):
        """
        Insert a single named row into the table view input
        """
        table_view.insertRow(row_position)  # insert an empty row

        table_item_path = QtWidgets.QTableWidgetItem(branch_str)
        table_item_type = QtWidgets.QTableWidgetItem('Choose a type')

        table_item_path.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # disable edit of the first col
        table_view.setItem(row_position, 0, table_item_path)
        default_alias = 'alias_' + str(row_position) if table_view.objectName() == 'tableWidgetInput' \
            else 'cv_alias_' + str(row_position)
        table_view.setItem(row_position, 1, QtWidgets.QTableWidgetItem(default_alias))
        table_view.setItem(row_position, 2, table_item_type)

        table_item_type.setData(Qt.BackgroundRole, QBrush(Qt.red))  # paints the cell background to red

    def insertDataOnTableCreation(self, table_view, table_data):
        for i in range(len(table_data)):
            table_view.insertRow(i)

            if table_view.objectName() == 'tableWidgetInput':
                first_col_item = QtWidgets.QTableWidgetItem(table_data[i]['Path'])
                first_col_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                table_view.setItem(i, 0, first_col_item)
                table_view.setItem(i, 1, QtWidgets.QTableWidgetItem(table_data[i]['Alias']))
                table_view.setItem(i, 2, QtWidgets.QTableWidgetItem(table_data[i]['Type']))
            else:
                first_col_item = QtWidgets.QTableWidgetItem(table_data[i]['Path'])
                first_col_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                table_view.setItem(i, 0, first_col_item)
                table_view.setItem(i, 1, QtWidgets.QTableWidgetItem(table_data[i]['Alias']))

    def okButtonPressed(self):
        # read the data from the tables
        in_table = self.ui.tableWidgetInput
        out_table = self.ui.tableWidgetOutput

        in_model = in_table.model()
        input_data = []
        for row in range(in_model.rowCount()):
            input_data.append({'Path': in_model.data(in_model.index(row, 0)),
                               'Alias': in_model.data(in_model.index(row, 1)),
                               'Type': in_model.data(in_model.index(row, 2))})

        out_model = out_table.model()
        output_data = []
        for row in range(out_model.rowCount()):
            output_data.append({'Path': out_model.data(out_model.index(row, 0)),
                                'Alias': out_model.data(out_model.index(row, 1))})

        input_aliases_list = [entry['Alias'] for entry in input_data]
        output_aliases_list = [entry['Alias'] for entry in output_data]

        is_alias_duplicated = True if len(input_aliases_list + output_aliases_list) != \
                                      len(set(input_aliases_list + output_aliases_list)) else False
        is_input_alias_defined = True if 'Choose a type' in [input_data_row['Type']
                                                             for input_data_row in input_data] else False
        if is_input_alias_defined:
            # the user did not choose a type for a selected variable. Alert him to do so.
            msg_box_text = "At least one of the selected input variables does not have a defined type (either MV or " \
                           "d). You have to define it for all of them!"
            msg_box_title = "Input variable without type detected"

            self.warnTheUserDialog(msg_box_text, msg_box_title)

        if is_alias_duplicated:
            # warn the user of duplicate entries
            msg_box_text = "Duplicated aliases found. Input AND output aliases must be unique."
            msg_box_title = "Duplicated aliases"

            self.warnTheUserDialog(msg_box_text, msg_box_title)

        if not is_input_alias_defined and not is_alias_duplicated:
            # input aliases properly defined and no duplicated detected, proceed as normal
            self.gui_data.setInputTableData(input_data)
            self.gui_data.setOutputTableData(output_data)

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

        if self.streams_file_txt_path is not None and self.blocks_file_txt_path is not None:
            # THIS SECTION IS FOR DEVELOPING PURPOSE
            # if tree text file containing the variables are specified do not load from bkp file
            progress_dialog.setLabelText(
                'Please wait while the variable tree is loaded...\nLoading Stream variables...')
            stream_raw = read_simulation_tree_from_path(self.streams_file_txt_path)
            progress_dialog.setValue(2)

            progress_dialog.setLabelText('Please wait while the variable tree is loaded...\nLoading Block variables...')
            blocks_raw = read_simulation_tree_from_path(self.blocks_file_txt_path)
            progress_dialog.setValue(3)

            # set the simulation data dictionary to fill the form in mainwindow. THIS IS A DUMMY DICTIONARY
            simulation_data = {'components': ['PROPANE', 'PROPENE'],
                               'therm_method': ['PENG-ROB'],
                               'blocks': ['TOWER'],
                               'streams': ['B', 'D', 'F'],
                               'reactions': [],
                               'sens_analysis': ['S-1'],
                               'calculators': ['C-1'],
                               'optimizations': ['O-1'],
                               'design_specs': []}

            self.gui_data.setSimulationDataDictionary(simulation_data)

        else:
            # Open the connection
            progress_dialog.setLabelText('Please wait while the variable tree is loaded...\nOpening connection...')
            aspen_com = AspenConnection(self.bkp_path)
            progress_dialog.setValue(1)

            # load the tree from the connection file
            progress_dialog.setLabelText(
                'Please wait while the variable tree is loaded...\nLoading Stream variables...')

            stream_raw = read_simulation_tree_from_fileobject(aspen_com.GenerateTreeFile(r"\Data\Streams"))
            progress_dialog.setValue(2)

            progress_dialog.setLabelText('Please wait while the variable tree is loaded...\nLoading Block variables...')

            blocks_raw = read_simulation_tree_from_fileobject(aspen_com.GenerateTreeFile(r"\Data\Blocks"))
            progress_dialog.setValue(3)

            # set the simulation data dictionary to fill the form in mainwindow
            self.gui_data.setSimulationDataDictionary(aspen_com.GetSimulationData())

            # Destroy the aspen_com object closing files as well
            aspen_com.Destructor()

        # Populate the data
        self.ui.treeViewInput.model().removeRows(0, self.ui.treeViewInput.model().rowCount())
        self.ui.treeViewOutput.model().removeRows(0, self.ui.treeViewOutput.model().rowCount())

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

    def warnTheUserDialog(self, text, box_title):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Warning)
        msg_box.setText(text)
        msg_box.setWindowTitle(box_title)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)

        msg_box.exec()


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
