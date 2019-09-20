from PyQt5.QtCore import Qt, QEvent, QAbstractTableModel, QModelIndex, QPersistentModelIndex
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QBrush, QPalette
from PyQt5.QtWidgets import (QApplication, QDialog, QMessageBox,
                             QProgressDialog, QPushButton, QTableView,
                             QTableWidgetItem, QHeaderView)

from gui.models.data_storage import DataStorage
from gui.models.sim_connections import AspenConnection
from gui.views.py_files.loadsimulationtree import Ui_Dialog
from gui.calls.base import AliasEditorDelegate, ComboBoxDelegate, warn_the_user

# TODO: Include units in table display.


class VariableTableModel(QAbstractTableModel):
    """Table model used to manipulate input/output definitions of variables
    chosen through the variable trees.

    Parameters
    ----------
    application_data : DataStorage
        Application data storage object.
    mode : str {'input', 'output'}
        Which mode the table should assume for the type of variables.
        Default is 'input'
    """

    def __init__(self, application_data: DataStorage, parent: QTableView,
                 mode: str = 'input'):
        QAbstractTableModel.__init__(self, parent)
        self.app_data = application_data
        self.mode = mode
        self.load_data()

    def load_data(self):
        self.layoutAboutToBeChanged.emit()
        mode = self.mode
        if mode == 'input':
            self.variable_data = self.app_data.input_table_data
        elif mode == 'output':
            self.variable_data = self.app_data.output_table_data
        else:
            raise ValueError("Invalid table mode.")

        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return len(self.variable_data)

    def columnCount(self, parent=None):
        return 3

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        var_data = self.variable_data[row]

        if role == Qt.DisplayRole:
            if col == 0:
                return str(var_data['Path'])
            elif col == 1:
                return str(var_data['Alias'])
            elif col == 2:
                return str(var_data['Type'])
            else:
                return None

        elif role == Qt.TextAlignmentRole:
            if col >= 1:
                return Qt.AlignCenter
            else:
                return None

        elif role == Qt.BackgroundRole:
            if col == 1:
                # paints red if duplicates are found between input/output
                aliases = [row['Alias']
                           for row in self.app_data.input_table_data +
                           self.app_data.output_table_data]

                if aliases.count(self.variable_data[row]['Alias']) > 1:
                    return QBrush(Qt.red)
                else:
                    return QBrush(self.parent().palette().brush(
                        QPalette.Base))

            elif col == 2:
                if self.variable_data[row]['Type'] == 'Choose a type':
                    return QBrush(Qt.red)
                else:
                    return QBrush(self.parent().palette().brush(
                        QPalette.Base))

            else:
                return None

        else:
            return None

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):
        if role != Qt.EditRole or not index.isValid():
            return False

        row = index.row()
        col = index.column()

        if col == 0:
            self.variable_data[row]['Path'] = value
        elif col == 1:
            self.variable_data[row]['Alias'] = value
        elif col == 2:
            self.variable_data[row]['Type'] = value
        else:
            return False

        self.app_data.alias_data_changed.emit()
        self.dataChanged.emit(index.sibling(0, col),
                              index.sibling(self.rowCount(), col))

        self.parent().selectionModel().clearSelection()
        return True

    def insertRows(self, row: int, count: int = 1,
                   parent: QModelIndex = QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        # create the empty rows
        new_rows = [{'Path': '', 'Alias': 'alias_' + str(self.rowCount()),
                     'Type': 'Choose a type'} for i in range(count)]
        if row == 0:
            # prepend rows
            new_rows.extend(self.variable_data)
            self.variable_data = new_rows
        elif row == self.rowCount():
            # append rows
            self.variable_data.extend(new_rows)
        else:
            self.variable_data = self.variable_data[:row] + new_rows + \
                self.variable_data[row:]
        self.endInsertRows()

        if self.mode == 'input':
            self.app_data.input_table_data = self.variable_data
        else:
            self.app_data.output_table_data = self.variable_data
        return True

    def removeRows(self, row: int, count: int = 1,
                   parent: QModelIndex = QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)

        del self.variable_data[row: (row + count)]
        self.endRemoveRows()

        if self.mode == 'input':
            self.app_data.input_table_data = self.variable_data
        else:
            self.app_data.output_table_data = self.variable_data
        return True

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    return "Variable path"
                elif section == 1:
                    return "Alias"
                else:
                    return "Type"

    def flags(self, index: QModelIndex):

        row = index.row()
        col = index.column()

        if col == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | ~Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable


class LoadSimulationTreeDialog(QDialog):
    def __init__(self, application_database: DataStorage):
        # ------------------------ Internal Variables -------------------------
        self.app_data = application_database

        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        table_input = self.ui.tableViewInput
        table_output = self.ui.tableViewOutput

        self._input_table_model = VariableTableModel(self.app_data,
                                                     mode='input',
                                                     parent=table_input)
        self._output_table_model = VariableTableModel(self.app_data,
                                                      mode='output',
                                                      parent=table_output)

        table_input.setModel(self._input_table_model)
        table_output.setModel(self._output_table_model)

        table_input.setColumnWidth(0, 400)  # first column resize
        table_output.setColumnWidth(0, 400)

        # create tree models
        self.create_tree_models()

        # set the delegates for the tables
        self._input_alias_delegate = AliasEditorDelegate(max_characters=13)
        self._output_alias_delegate = AliasEditorDelegate(max_characters=13)
        table_input.setItemDelegateForColumn(1, self._input_alias_delegate)
        table_output.setItemDelegateForColumn(1, self._output_alias_delegate)

        input_combo_list = ["Manipulated (MV)", "Disturbance (d)", "Auxiliary"]
        output_combo_list = ["Candidate (CV)", "Auxiliary"]
        self._input_combo_delegate = ComboBoxDelegate(input_combo_list)
        self._output_combo_delegate = ComboBoxDelegate(output_combo_list)
        table_input.setItemDelegateForColumn(2, self._input_combo_delegate)
        table_output.setItemDelegateForColumn(2, self._output_combo_delegate)

        # --------------------------- Signals/Slots ---------------------------
        # opens the simulation connection and load its variable trees
        self.ui.pushButtonLoadTreeFromFile.clicked.connect(self.load_tree)

        # action associate with the double click of a node in the trees
        self.ui.treeViewInput.doubleClicked.connect(self.double_click_on_tree)
        self.ui.treeViewOutput.doubleClicked.connect(self.double_click_on_tree)

        # ok push button pressed
        self.ui.pushButtonOK.clicked.connect(self.ok_button_pressed)

        # forces the table views update from one another.
        self.app_data.alias_data_changed.connect(
            self._input_table_model.load_data)
        self.app_data.alias_data_changed.connect(
            self._output_table_model.load_data)

        # opens simulation GUI when checkbox is toggled
        self.ui.openSimGUICheckBox.stateChanged.connect(self.open_simulator_gui)
        # ---------------------------------------------------------------------

    def open_simulator_gui(self, checkstate: Qt.CheckState):
        # check if there is a connection object and open if not
        if hasattr(self, 'aspen_com'):
            con_obj = self.aspen_com.get_connection_object()

        else:
            self.load_tree()
            con_obj = self.aspen_com.get_connection_object()

        if checkstate == Qt.Checked:
            con_obj.Visible = 1
        else:
            con_obj.Visible = 0

    def create_tree_models(self):
        input_tree_dict_model = QStandardItemModel()
        output_tree_model = QStandardItemModel()

        # place the headers texts
        input_tree_dict_model.setHorizontalHeaderLabels(['Input variables'])
        output_tree_model.setHorizontalHeaderLabels(['Output variables'])

        # set the models in the views
        self.ui.treeViewInput.setModel(input_tree_dict_model)
        self.ui.treeViewOutput.setModel(output_tree_model)

        # make the tree views headers bold
        self.ui.treeViewInput.header().setStyleSheet('QWidget { font: bold }')
        self.ui.treeViewOutput.header().setStyleSheet('QWidget { font: bold }')

        # check if application has already tree dictionaries. If so, populate
        # with those values.
        if len(self.app_data.tree_model_input) != 0:
            input_tree_dict = self.app_data.tree_model_input
            self.populate_tree(self.ui.treeViewInput.model(), input_tree_dict)

        if len(self.app_data.tree_model_output) != 0:
            output_tre_dict = self.app_data.tree_model_output
            self.populate_tree(self.ui.treeViewOutput.model(), output_tre_dict)

    def load_tree(self):
        """Opens the connection with the simulation engine and loads the
        variable tree.
        """
        # disable the load tree and ok buttons
        self.ui.pushButtonLoadTreeFromFile.setEnabled(False)
        self.ui.pushButtonOK.setEnabled(False)

        # start the progress bar dialog
        progress_dialog = QProgressDialog(
            'Please wait while the variable tree is loaded...',
            None, 0, 0, self)
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setWindowTitle("Loading variables")
        progress_dialog.show()
        progress_dialog.setValue(0)

        # open the connection
        aspen_com = AspenConnection(self.app_data.simulation_file)
        self.aspen_com = aspen_com  # to keep the reference

        # load and store simulation data dictionary
        self.app_data.simulation_data = aspen_com.get_simulation_data()

        # load and store JSON dicts
        input_tree_dict = aspen_com.get_simulation_partial_io_tree('input')
        output_tree_dict = aspen_com.get_simulation_partial_io_tree('output')
        self.app_data.tree_model_input = input_tree_dict
        self.app_data.tree_model_output = output_tree_dict

        # transform the JSON dicts into tree models
        self.populate_tree(self.ui.treeViewInput.model(), input_tree_dict)
        self.populate_tree(self.ui.treeViewOutput.model(), output_tree_dict)

        # Complete progress dialog
        progress_dialog.setMaximum(1)
        progress_dialog.setValue(1)

        # Enable the load tree and ok buttons
        self.ui.pushButtonLoadTreeFromFile.setEnabled(True)
        self.ui.pushButtonOK.setEnabled(True)

    def populate_tree(self, model: QStandardItemModel, tree_nodes: dict):
        """Populates the model of a tree view.

        Parameters
        ----------
        model : QStandardItemModel
            TreeView model.
        tree_nodes : dict
            Dictionary containing the tree representation.
        """
        # clear all the current rows
        model.removeRows(0, model.rowCount())

        # append new rows
        model.appendRow(self.traverse_json_tree(tree_nodes))

    def traverse_json_tree(self, root_node: dict) -> QStandardItem:
        """Traverses a JSON dictionary tree representation through recursion.

        Parameters
        ----------
        root_node : dict
            Dictionary which is the root of the tree. See notes for node
            representation.

        Returns
        -------
        QStandardItem
            Root of the tree as a QStandardItem.

        Notes
        -----
        The `root_node` and subsequent nodes has to be in the following format:
            node = {'node': str_name_of_node,
                    'children': list_of_nodes,
                    'description': str_tooltip_description_of_node}

        Where list_of_nodes is, literally, a list of nodes. Duh.

        """
        rn = QStandardItem(root_node['node'])
        rn.setEditable(False)
        if 'description' in root_node:
            rn.setToolTip(root_node['description'])

        if 'children' in root_node:
            for child in root_node['children']:
                rn.appendRow(self.traverse_json_tree(child))

        return rn

    def double_click_on_tree(self):
        """Slot (function) that handles double click event on a single leaf
        node in the tree.
        """
        tree_name = self.sender().objectName()
        tree_view = self.ui.treeViewInput if tree_name == "treeViewInput" \
            else self.ui.treeViewOutput
        tree_model = tree_view.model()

        table_model = self.ui.tableViewInput.model() \
            if tree_name == 'treeViewInput' \
            else self.ui.tableViewOutput.model()

        # get the model index of the node clicked
        index_selected = tree_view.currentIndex()

        if not tree_model.itemFromIndex(index_selected).hasChildren():
            # Only proceed if the selected node is a leaf

            # intialize node construction
            branch_list = [tree_model.data(index_selected).lstrip()]

            # traverse the nodes upwards (stop on root node)
            parent_node = tree_model.itemFromIndex(index_selected).parent()
            while parent_node is not None:
                parent_node_name = parent_node.text().lstrip()
                branch_list.append(parent_node_name)
                parent_node = parent_node.parent()

            # create the full path string
            fullpath = '\\' + '\\'.join(list(reversed(branch_list)))

            # verify if full path is already in the table
            current_paths = [row['Path']
                             for row in self.app_data.input_table_data +
                             self.app_data.output_table_data]

            if fullpath in current_paths:
                # the variable is already in table, warn the user
                msg_box = QMessageBox(
                    QMessageBox.Warning,
                    "Duplicated variable",
                    "The selected variable is already the table!",
                    buttons=QMessageBox.Ok,
                    parent=None
                )
                msg_box.exec_()
            else:
                # variable not in table, insert it
                self.insert_new_single_row(table_model, fullpath)

    def insert_new_single_row(self, table_model: VariableTableModel,
                              node_str: str):
        """Inserts a single variable row in the table view.

        Parameters
        ----------
        table_model : VariableTableModel
            Which VariableTableModel to insert the row.
        node_str : str
            String containing the full path to the selected node.
        """
        # start by inserting an empty row
        table_model.insertRow(table_model.rowCount())

        # insert the path value
        n_rows = table_model.rowCount()
        table_model.setData(table_model.index(n_rows - 1, 0),
                            node_str, Qt.EditRole)

    def ok_button_pressed(self):
        input_var_data = self.app_data.input_table_data
        output_var_data = self.app_data.output_table_data

        in_alias_list = [row['Alias'] for row in input_var_data]
        out_alias_list = [row['Alias'] for row in output_var_data]

        # check if there is any duplicates between input and output
        is_alias_duplicated = True if len(in_alias_list + out_alias_list) != \
            len(set(in_alias_list + out_alias_list)) else False

        # check if there any variable without its type defined
        is_in_var_defined = False if 'Choose a type' in \
            [row['Type'] for row in input_var_data] else True

        is_out_var_defined = False if 'Choose a type' in \
            [row['Type'] for row in output_var_data] else True

        if not is_in_var_defined or not is_out_var_defined:
            # user did not define all the variable types
            if not is_in_var_defined and is_out_var_defined:
                iovartype = 'the selected input'
                iovartitle = 'Input'
            elif is_in_var_defined and not is_out_var_defined:
                iovartype = 'the selected output'
                iovartitle = 'Output'
            else:
                iovartype = 'both input and output'
                iovartitle = iovartype.capitalize()

            text = ("At least one of {0} variables does not have a defined"
                    " type.\nYou have to define it for all of them!").format(
                iovartype)
            title = "{0} variable without type detected!".format(iovartitle)

            warn_the_user(text, title)

        if is_alias_duplicated:
            # warn the user about duplicated entries
            text = ("Duplicated aliases between input and output found."
                    "\nAll the aliases together must be unique.")
            title = "Duplicated aliases detected!"
            warn_the_user(text, title)

        if is_in_var_defined and is_out_var_defined and \
                not is_alias_duplicated:
            # Everything is properly set, close the dialog.
            self.close()

    def keyPressEvent(self, event: QEvent):
        """keyPressEvent override of the QDialog class to extend keyboard
        interaction with the tables (i.e. delete rows).
        """
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Delete:
            # if the delete key was pressed
            widget = QApplication.focusObject()  # get widget that has focus
            widget_name = widget.objectName()
            if widget_name == self.ui.tableViewInput.objectName() \
                    or widget_name == self.ui.tableViewOutput.objectName():
                table_sel_model = widget.selectionModel()
                indexes = [QPersistentModelIndex(index)
                           for index in table_sel_model.selectedRows()]

                for index in indexes:
                    # delete selected rows
                    widget.model().removeRow(index.row())

                # clear selection
                widget.selectionModel().clearSelection()

    def closeEvent(self, event):
        # clean up of the aspen connection if there is one
        if hasattr(self, 'aspen_com'):
            self.aspen_com.close_connection()

        super().closeEvent(event)


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook
    from tests_.mock_data import LOADSIM_SAMPLING_MOCK_DS

    app = QApplication(sys.argv)

    # Load application storage mock
    ds = LOADSIM_SAMPLING_MOCK_DS

    # start the application
    w = LoadSimulationTreeDialog(ds)
    w.show()

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
