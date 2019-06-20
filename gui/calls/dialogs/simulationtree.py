from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QBrush
from PyQt5.QtWidgets import (QApplication, QDialog, QMessageBox,
                             QProgressDialog, QPushButton, QTableWidget,
                             QTableWidgetItem)

from gui.models.data_storage import DataStorage
from gui.models.sim_connections import AspenConnection
from gui.views.py_files.loadsimulationtree import Ui_Dialog
from gui.calls.base import AliasEditorDelegate, ComboBoxDelegate

# TODO: Include units in table display.


class LoadSimulationTreeDialog(QDialog):
    def __init__(self, application_database: DataStorage):
        # ------------------------ Internal Variables -------------------------
        self.app_data = application_database

        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        table_input = self.ui.tableWidgetInput
        table_output = self.ui.tableWidgetOutput

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

        # check the application for variable data
        self.check_variable_data()

        # --------------------------- Signals/Slots ---------------------------
        # opens the simulation connection and load its variable trees
        self.ui.pushButtonLoadTreeFromFile.clicked.connect(self.load_tree)

        # action associate with the double click of a node in the trees
        self.ui.treeViewInput.doubleClicked.connect(self.double_click_on_tree)
        self.ui.treeViewOutput.doubleClicked.connect(self.double_click_on_tree)

        # ok push button pressed
        self.ui.pushButtonOK.clicked.connect(self.ok_button_pressed)

        # ---------------------------------------------------------------------

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

    def check_variable_data(self):
        """Checks the application data storage for variable data and sets them
        in their tables.
        """
        # subfunction that iterates the data and sets it the table
        def set_data_into_table(table_widget: QTableWidget, table_data: list):
            for row, var in enumerate(table_data):
                table_widget.insertRow(row)

                item_path = QTableWidgetItem(var['Path'])
                item_alias = QTableWidgetItem(var['Alias'])
                item_type = QTableWidgetItem(var['Type'])

                item_path.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                item_alias.setTextAlignment(Qt.AlignCenter)
                item_type.setTextAlignment(Qt.AlignCenter)

                table_widget.setItem(row, 0, item_path)
                table_widget.setItem(row, 1, item_alias)
                table_widget.setItem(row, 2, item_type)

        inp_var_table = self.ui.tableWidgetInput
        out_var_table = self.ui.tableWidgetOutput

        inp_data = self.app_data.input_table_data
        out_data = self.app_data.output_table_data

        set_data_into_table(inp_var_table, inp_data)
        set_data_into_table(out_var_table, out_data)

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

        table_view = self.ui.tableWidgetInput if tree_name == 'treeViewInput' \
            else self.ui.tableWidgetOutput

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
            current_paths = [table_view.model().index(row, 0).data()
                             for row in range(table_view.rowCount())]

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
                self.insert_new_single_row(table_view, fullpath)

    def insert_new_single_row(self, table_view: QTableWidget, node_str: str):
        """Inserts a single variable row in the table view.

        Parameters
        ----------
        table_view : QTableWidget
            Which QTableWidget widget to insert the row
        node_str : str
            String containing the full path to the selected node.
        """
        # start by inserting an empty row
        n_rows_table = table_view.rowCount()
        table_view.insertRow(n_rows_table)

        default_alias = 'in_alias_' + str(n_rows_table) \
            if table_view.objectName() == 'tableWidgetInput' \
            else 'out_alias_' + str(n_rows_table)

        table_item_path = QTableWidgetItem(node_str)
        table_item_alias = QTableWidgetItem(default_alias)
        table_item_type = QTableWidgetItem('Choose a type')

        # disable edit of the first column
        table_item_path.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        # paint the cell backgroud of type column red
        table_item_type.setData(Qt.BackgroundRole, QBrush(Qt.red))

        # set the alignments of table items
        table_item_alias.setTextAlignment(Qt.AlignCenter)
        table_item_type.setTextAlignment(Qt.AlignCenter)

        # place the items
        table_view.setItem(n_rows_table, 0, table_item_path)
        table_view.setItem(n_rows_table, 1, table_item_alias)
        table_view.setItem(n_rows_table, 2, table_item_type)

    def ok_button_pressed(self):
        # subfunction to read variables in tables into list of dicts
        def table_into_list(table_view: QTableWidget) -> list:
            var_list = []
            model = table_view.model()
            for row in range(model.rowCount()):
                var_list.append({'Path': model.data(model.index(row, 0)),
                                 'Alias': model.data(model.index(row, 1)),
                                 'Type': model.data(model.index(row, 2))})

            return var_list

        # subfuction to display warnings about variables selection to the user
        def warn_the_user(msg_text: str, msg_title: str) -> None:
            msg_box = QMessageBox(
                QMessageBox.Warning,
                msg_title,
                msg_text,
                buttons=QMessageBox.Ok,
                parent=None
            )
            msg_box.exec_()

        input_var_data = table_into_list(self.ui.tableWidgetInput)
        output_var_data = table_into_list(self.ui.tableWidgetOutput)

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
            # Everything is properly set, store then in the application and
            # close the dialog.

            self.app_data.input_table_data = input_var_data
            self.app_data.output_table_data = output_var_data

            self.close()

    def keyPressEvent(self, event: QEvent):
        """keyPressEvent override of the QDialog class to extend keyboard
        interaction with the tables (i.e. delete rows).
        """
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Delete:
            # if the delete key was pressed
            widget = QApplication.focusObject()  # get widget that has focus
            widget_name = widget.objectName()
            if widget_name == self.ui.tableWidgetInput.objectName() \
                    or widget_name == self.ui.tableWidgetOutput.objectName():
                table_sel_model = widget.selectionModel()
                indexes = table_sel_model.selectedIndexes()

                for index in indexes:
                    # delete selected rows
                    widget.removeRow(index.row())

    def closeEvent(self, event):
        # clean up of the aspen connection if there is one
        if hasattr(self, 'aspen_com'):
            self.aspen_com.close_connection()

        super().closeEvent(event)


if __name__ == "__main__":
    import sys
    import json
    import pathlib
    from gui.calls.base import my_exception_hook

    app = QApplication(sys.argv)

    # store bkp test file in home dir
    ds = DataStorage()
    filepath = str(pathlib.Path().home() / "infill.bkp")
    ds.simulation_file = filepath

    # load the test tree
    jsonfilepath = r"C:\Users\Felipe\Desktop\GUI\python\infill.json"

    with open(jsonfilepath, 'r') as jfile:
        tree = json.load(jfile)

    root_input = tree['input']
    root_output = tree['output']

    ds.tree_model_input = root_input
    ds.tree_model_output = root_output

    # some input/output variables
    ds.input_table_data = [{'Path': r"\Data\Blocks\TOWER\Input\BASIS_RR", 'Alias': 'rr', 'Type': 'Manipulated (MV)'},
                           {'Path': r"\Data\Blocks\TOWER\Input\D:F", 'Alias': 'df', 'Type': 'Manipulated (MV)'}]
    ds.output_table_data = [{'Path': r"\Data\Streams\D\Output\TOT_FLOW", 'Alias': 'd', 'Type': 'Auxiliary'},
                            {'Path': r"\Data\Streams\B\Output\MOLEFRAC\MIXED\PROPENE", 'Alias': 'xb', 'Type': 'Candidate (CV)'},
                            {'Path': r"\Data\Streams\B\Output\TOT_FLOW", 'Alias': 'b', 'Type': 'Auxiliary'},
                            {'Path': r"\Data\Blocks\TOWER\Output\REB_DUTY", 'Alias': 'qr', 'Type': 'Auxiliary'},
                            {'Path': r"\Data\Blocks\TOWER\Output\MOLE_L1", 'Alias': 'l', 'Type': 'Auxiliary'},
                            {'Path': r"\Data\Blocks\TOWER\Output\MOLE_VN", 'Alias': 'v', 'Type': 'Auxiliary'},
                            {'Path': r"\Data\Streams\FEED\Output\TOT_FLOW", 'Alias': 'f', 'Type': 'Auxiliary'},
                            {'Path': r"\Data\Streams\D\Output\MOLEFRAC\MIXED\PROPENE", 'Alias': 'xd', 'Type': 'Candidate (CV)'}]

    # start the application
    w = LoadSimulationTreeDialog(ds)
    w.show()

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
