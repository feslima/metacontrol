import pandas as pd
import pythoncom
from PyQt5.QtCore import (QAbstractTableModel, QEvent, QModelIndex, QObject,
                          QPersistentModelIndex, Qt, QThread, pyqtSignal,
                          pyqtSlot)
from PyQt5.QtGui import QBrush, QPalette, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QDialog, QHeaderView, QMessageBox,
                             QProgressDialog, QPushButton, QTableView,
                             QTableWidgetItem)
from win32com.client import Dispatch

from gui.calls.base import AliasEditorDelegate, ComboBoxDelegate, warn_the_user
from gui.models.data_storage import DataStorage
from gui.models.sim_connections import AspenConnection
from gui.views.py_files.loadsimulationtree import Ui_Dialog

#import ptvsd


# TODO: Include units in table display.
class ConnectionWorker(QObject):
    # signals
    connection_open = pyqtSignal()
    input_tree_loaded = pyqtSignal()
    output_tree_loaded = pyqtSignal()
    connection_id_created = pyqtSignal(object)  # emits the server ID

    def __init__(self, app_data: DataStorage, mode: str = 'tree', parent=None):
        super().__init__(parent)
        self.app_data = app_data
        if mode in ['tree', 'open']:
            self.mode = mode
        else:
            raise ValueError("Invalid mode!")

    @pyqtSlot()
    def open_connection(self):
        #ptvsd.debug_this_thread()

        # open the connection
        pythoncom.CoInitialize()
        self.connection = AspenConnection(self.app_data.simulation_file)
        self.connection_open.emit()

        if self.mode == 'open':
            self.create_connection_id()

    @pyqtSlot()
    def load_tree(self):
        self.open_connection()

        # load and store simulation data dictionary
        self.app_data.simulation_data = self.app_data._uneven_array_to_frame(
            self.connection.get_simulation_data())

        # load the trees
        input_tree = self.connection.get_simulation_partial_io_tree('input')
        self.app_data.tree_model_input = input_tree
        self.input_tree_loaded.emit()

        output_tree = self.connection.get_simulation_partial_io_tree('output')
        self.app_data.tree_model_output = output_tree
        self.output_tree_loaded.emit()

        self.create_connection_id()

    @pyqtSlot()
    def create_connection_id(self):
        # create the COM server ID (this enables connection from form thread)
        self.connection_id = pythoncom.CoMarshalInterThreadInterfaceInStream(
            pythoncom.IID_IDispatch,
            self.connection.get_connection_object())
        self.connection_id_created.emit(self.connection_id)


class VariableTableModel(QAbstractTableModel):
    """Table model used to manipulate input/output definitions of variables
    chosen through the variable trees.

    Parameters
    ----------
    application_data : DataStorage
        Application data storage object.
    parent : QTableView
        Parent table to be associated.
    mode : str, optional ('input', 'output')
        Which mode the table should assume for the type of variables.
        Default is 'input'.
    """

    def __init__(self, application_data: DataStorage, parent: QTableView,
                 mode: str = 'input'):
        QAbstractTableModel.__init__(self, parent)
        self.app_data = application_data
        self.column_headers = self.app_data._ALIAS_COLS
        self.mode = mode

        # forces the table views update from one another.
        if self.mode == 'input':
            self.app_data.input_alias_data_changed.connect(self.load_data)
        elif mode == 'output':
            self.app_data.output_alias_data_changed.connect(self.load_data)
        else:
            raise ValueError("Invalid table mode.")

        self.load_data()

    def load_data(self):
        self.layoutAboutToBeChanged.emit()
        mode = self.mode
        if mode == 'input':
            self.variable_data = self.app_data.input_table_data
        else:
            self.variable_data = self.app_data.output_table_data

        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return self.variable_data.shape[0]

    def columnCount(self, parent=None):
        return self.variable_data.shape[1]

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        value = self.variable_data.iat[row, col]

        if role == Qt.DisplayRole:
            return str(value)

        elif role == Qt.TextAlignmentRole:
            if self.variable_data.columns[col] != 'Path':
                return Qt.AlignCenter
            else:
                return None

        elif role == Qt.BackgroundRole:
            if self.variable_data.columns[col] == 'Alias':
                # paints red if duplicates are found between input/output
                aliases = pd.concat([self.app_data.input_table_data,
                                     self.app_data.output_table_data],
                                    axis='index', ignore_index=True,
                                    sort=False)

                if aliases['Alias'].value_counts()[value] > 1:
                    return QBrush(Qt.red)
                else:
                    return QBrush(self.parent().palette().brush(
                        QPalette.Base))

            elif self.variable_data.columns[col] == 'Type':
                if value == 'Choose a type':
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

        if self.variable_data.columns[col] in self.app_data._ALIAS_COLS:
            self.variable_data.iat[row, col] = value

            if self.mode == 'input':
                self.app_data.input_table_data = self.variable_data
            else:
                self.app_data.output_table_data = self.variable_data

        else:
            return False

        self.dataChanged.emit(index.sibling(0, col),
                              index.sibling(self.rowCount(), col))

        self.parent().selectionModel().clearSelection()
        return True

    def insertRows(self, row: int, count: int = 1,
                   parent: QModelIndex = QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        # create the empty rows
        new_rows = pd.DataFrame.from_records(
            [{'Path': '', 'Alias': 'alias_' + str(self.rowCount()),
              'Type': 'Choose a type'} for i in range(count)]
        )
        if row == 0:
            # prepend rows
            self.variable_data = pd.concat([new_rows, self.variable_data],
                                           axis='index', ignore_index=True,
                                           sort=False)
        elif row == self.rowCount():
            # append rows
            self.variable_data = pd.concat([self.variable_data, new_rows],
                                           axis='index', ignore_index=True,
                                           sort=False)
        else:
            # the drop=True is to prevent an additional column
            self.variable_data = pd.concat(
                [self.variable_data.iloc[:row], new_rows,
                 self.variable_data.iloc[row:]],
                ignore_index=True
            ).reset_index(drop=True)

        self.endInsertRows()

        if self.mode == 'input':
            self.app_data.input_table_data = self.variable_data
        else:
            self.app_data.output_table_data = self.variable_data
        return True

    def removeRows(self, row: int, count: int = 1,
                   parent: QModelIndex = QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)

        df = self.variable_data
        df.drop(labels=df.index[row: (row + count)], axis='index',
                inplace=True)
        self.endRemoveRows()

        if self.mode == 'input':
            self.app_data.input_table_data = df
        else:
            self.app_data.output_table_data = df
        return True

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.variable_data.columns[section])
            else:
                return None

    def flags(self, index: QModelIndex):

        row = index.row()
        col = index.column()

        if self.variable_data.columns[col] == 'Path':
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

        input_combo_list = list(self.app_data._INPUT_ALIAS_TYPES.values())
        output_combo_list = list(self.app_data._OUTPUT_ALIAS_TYPES.values())
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

        # opens simulation GUI when checkbox is toggled
        self.ui.openSimGUICheckBox.stateChanged.connect(
            self.open_simulator_gui)
        # ---------------------------------------------------------------------

    def open_simulator_gui(self, checkstate: Qt.CheckState):
        # check if there is a connection object and open if not
        if not hasattr(self, 'aspen_com'):
            # FIXME: set an apropriate logic that doesn't freeze the UI
            self.aspen_com = AspenConnection(self.app_data.simulation_file)

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
            'Please wait while the simulation engine is loaded...',
            None, 0, 0, self)
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setWindowTitle("Loading variables")
        progress_dialog.show()
        progress_dialog.setValue(0)

        self.progress_dialog = progress_dialog

        self.connection_worker = ConnectionWorker(app_data=self.app_data,
                                                  mode='tree')
        self.connection_thread = QThread()

        # connect worker signals
        self.connection_worker.connection_open.connect(
            self.on_connection_opened
        )
        self.connection_worker.input_tree_loaded.connect(
            self.on_input_tree_loaded
        )
        self.connection_worker.output_tree_loaded.connect(
            self.on_output_tree_loaded
        )
        self.connection_worker.connection_id_created.connect(
            self.on_connection_id_created
        )

        # move worker to thread
        self.connection_worker.moveToThread(self.connection_thread)

        # connect thread to load slot
        self.connection_thread.started.connect(
            self.connection_worker.load_tree
        )

        # start the thread
        self.connection_thread.start()

    def on_connection_opened(self):
        self.progress_dialog.setLabelText('Loading input tree variables...')

    def on_input_tree_loaded(self):
        self.progress_dialog.setLabelText('Loading output tree variables...')

        self.populate_tree(self.ui.treeViewInput.model(),
                           self.app_data.tree_model_input)

    def on_output_tree_loaded(self):
        self.populate_tree(self.ui.treeViewOutput.model(),
                           self.app_data.tree_model_output)

        # close progress dialog
        self.progress_dialog.setMaximum(1)
        self.progress_dialog.setValue(1)

        # Enable the load tree and ok buttons
        self.ui.pushButtonLoadTreeFromFile.setEnabled(True)
        self.ui.pushButtonOK.setEnabled(True)

    def on_connection_id_created(self, connection_id):
        # make the server available to this thread
        pythoncom.CoInitialize()
        self.aspen_com = AspenConnection(self.app_data.simulation_file)

        # populate internal connection variable of AspenConnection class
        # this is a horrendous fix... it works though!
        self.aspen_com._aspen = Dispatch(
            pythoncom.CoGetInterfaceAndReleaseStream(connection_id,
                                                     pythoncom.IID_IDispatch)
        )

        # quit the thread
        if hasattr(self, 'connection_thread'):
            self.connection_thread.quit()

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
            current_paths = pd.concat([self.app_data.input_table_data,
                                       self.app_data.output_table_data],
                                      axis='index',
                                      ignore_index=True,
                                      sort=False)['Path'].tolist()

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

        final_tab = pd.concat([input_var_data, output_var_data],
                              axis='index', ignore_index=True, sort=False)
        # check if there is any duplicates between input and output
        is_alias_duplicated = not final_tab['Alias'].is_unique

        # check if there any variable without its type defined
        is_in_var_defined = not input_var_data['Type'].eq(
            'Choose a type').any()

        is_out_var_defined = not output_var_data['Type'].eq(
            'Choose a type').any()

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
                           for index in table_sel_model.selectedIndexes()]

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
    from tests_.mock_data import ASPEN_BKP_FILE_PATH, loadsim_mock

    app = QApplication(sys.argv)

    # Load application storage mock
    ds = loadsim_mock()
    # ds = DataStorage()
    ds.simulation_file = str(ASPEN_BKP_FILE_PATH)

    # start the application
    w = LoadSimulationTreeDialog(ds)
    w.show()

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
