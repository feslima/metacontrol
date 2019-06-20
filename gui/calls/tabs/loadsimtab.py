import pathlib

from PyQt5.QtCore import QStringListModel, Qt
from PyQt5.QtGui import QBrush, QIcon, QPixmap
from PyQt5.QtWidgets import (QApplication, QComboBox, QCompleter, QFileDialog,
                             QHeaderView, QItemDelegate, QLineEdit,
                             QPushButton, QTableWidgetItem, QWidget,
                             QHeaderView)

from gui.calls.base import AliasEditorDelegate, ComboBoxDelegate
from gui.models.data_storage import DataStorage
from gui.views.py_files.loadsimtab import Ui_Form
from gui.models.math_check import ValidMathStr, is_expression_valid
from gui.calls.dialogs.simulationtree import LoadSimulationTreeDialog


class ExpressionAliasEditorDelegate(AliasEditorDelegate):

    def setModelData(self, editor, model, index):
        # override the alias editor delegate class method to check for
        # duplicates between expressions and aliases
        alias_tbl_mod = self.alias_item_model
        alias_tbl_col_idx = 0  # column index of table model where aliases are
        another_aliases = [alias_tbl_mod.data(
            alias_tbl_mod.index(row, alias_tbl_col_idx))
            for row in range(alias_tbl_mod.rowCount())]

        text = editor.text()
        model.setData(index, text, Qt.EditRole)

        current_expr_names = [model.data(model.index(row, index.column()))
                              for row in range(model.rowCount())]

        if current_expr_names.count(text) > 1 or text in another_aliases:
            model.setData(index, QBrush(Qt.red), Qt.BackgroundRole)
            model.parent().item(index.row(), index.column()).setToolTip(
                "Expression name already in use as an alias!")
        else:
            orig_back_color = editor.palette().color(editor.backgroundRole())
            model.setData(index, QBrush(orig_back_color), Qt.BackgroundRole)
            model.parent().item(index.row(), index.column()).setToolTip("")


class ExpressionEditorDelegate(QItemDelegate):
    def __init__(self, gui_data: DataStorage, parent=None):
        QItemDelegate.__init__(self, parent)
        self.gui_data = gui_data

    def createEditor(self, parent, option, index):
        line_editor = QLineEdit(parent)
        line_editor.setAlignment(Qt.AlignCenter)

        completer = QCompleter()
        line_editor.setCompleter(completer)

        # TODO: Implement match for multivariables
        model = QStringListModel()
        completer.setModel(model)
        completer.setFilterMode(Qt.MatchContains)

        # get aliases in display and set them to the completer
        aliases_in_display = []
        aliases_in_display.extend([input_row['Alias'] for input_row in
                                   self.gui_data.input_table_data])
        aliases_in_display.extend([output_row['Alias'] for output_row in
                                   self.gui_data.output_table_data])

        model.setStringList(aliases_in_display)

        # insert the math validator
        exp_validator = ValidMathStr(line_editor)
        line_editor.setValidator(exp_validator)

        return line_editor

    def setModelData(self, editor, model, index):
        text = editor.text()
        aliases_in_display = editor.completer().model().stringList()

        model.setData(index, text, Qt.EditRole)
        if is_expression_valid(text, aliases_in_display):
            # if the expression is valid, set the font color to green
            model.setData(index, QBrush(Qt.green), Qt.ForegroundRole)
        else:
            # invalid expression, set font color to red
            model.setData(index, QBrush(Qt.red), Qt.ForegroundRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class ExpressionTypeDelegate(ComboBoxDelegate):
    def __init__(self, item_list=None, parent=None):
        type_list = ["Objective function (J)", "Constraint function",
                     "Candidate (CV)"]
        super().__init__(type_list, parent=parent)


class LoadSimTab(QWidget):
    # ---------------------------- Class Constants ----------------------------
    EXPR_DELETE_COL = 0
    EXPR_NAME_COL = 1
    EXPR_EXPR_COL = 2
    EXPR_TYPE_COL = 3

    _EMPTY_SIM_INFO = DataStorage().simulation_file

    def __init__(self, application_database: DataStorage,
                 parent_tab=None):
        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Form()
        parent_tab = parent_tab if parent_tab is not None else self
        self.ui.setupUi(parent_tab)

        # ------------------------ Internal Variables -------------------------
        self.application_database = application_database

        # ----------------------- Widget Initialization -----------------------
        expr_table = self.ui.tableWidgetExpressions
        alias_table = self.ui.tableWidgetAliasDisplay
        sim_info_table = self.ui.tableWidgetSimulationData

        expr_table.setColumnWidth(2, 600)
        alias_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        sim_info_table.horizontalHeader().setMinimumSectionSize(80)
        sim_info_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        # set the delegates of the expression table
        self._expr_name_delegate = ExpressionAliasEditorDelegate(
            alias_item_model=alias_table.model())

        self._expr_math_delegate = ExpressionEditorDelegate(
            self.application_database)

        self._expr_type_delegate = ExpressionTypeDelegate()

        expr_table.setItemDelegateForColumn(self.EXPR_NAME_COL,
                                            self._expr_name_delegate)
        expr_table.setItemDelegateForColumn(self.EXPR_EXPR_COL,
                                            self._expr_math_delegate)
        expr_table.setItemDelegateForColumn(self.EXPR_TYPE_COL,
                                            self._expr_type_delegate)

        # --------------------------- Signals/Slots ---------------------------
        # update the table when the user changes an element
        self._expr_name_delegate.closeEditor.connect(self.update_expr_data)
        self._expr_math_delegate.closeEditor.connect(self.update_expr_data)
        self._expr_type_delegate.closeEditor.connect(self.update_expr_data)

        # open simulation file dialog
        self.ui.buttonOpenSimFile.clicked.connect(
            self.open_simulation_file_dialog)

        # open simulation variables tree dialog
        self.ui.buttonLoadVariables.clicked.connect(
            self.open_simulation_tree_dialog)

        # update the filename text browser
        self.application_database.simulation_file_changed.connect(
            self.update_simfilepath_display)

        # update the simulation info form
        self.application_database.simulation_info_changed.connect(
            self.update_siminfo_display)

        # update the selected alias table display
        self.application_database.input_alias_data_changed.connect(
            self.update_alias_display)
        self.application_database.output_alias_data_changed.connect(
            self.update_alias_display)

        # update the expression data display
        self.application_database.expr_data_changed.connect(
            self.update_expr_display)

        # inserts a new row into the expression table
        self.ui.buttonAddExpr.clicked.connect(self.insert_new_expression)

    # -------------------------------------------------------------------------
    def insert_new_expression(self):
        """Inserts a new default row into the expression table and updates the
        expression data storage.
        """
        self.insert_expression_row(expr_dict=None)
        self.update_expr_data()

    def insert_expression_row(self, expr_dict: dict = None):
        """Inserts a single expression data dictionary into the expression
        table.
        """
        expr_table_view = self.ui.tableWidgetExpressions
        n_rows = expr_table_view.rowCount()

        # insert the row
        expr_table_view.insertRow(n_rows)

        # create the button that deletes the current expression
        icon = QIcon()
        icon.addPixmap(QPixmap(":/loadsim/delete_icon.svg"),
                       QIcon.Normal, QIcon.Off)
        delete_btn = QPushButton(expr_table_view)
        delete_btn.setIcon(icon)
        delete_btn.clicked.connect(self.delete_expression_row)

        # create other items of the row
        if expr_dict is None:
            expr_dict = {'Name': 'expr_' + str(n_rows),
                         'Expr': 'Type expression',
                         'Type': 'Choose a type'}

        expr_name = QTableWidgetItem(expr_dict['Name'])
        expr_math = QTableWidgetItem(expr_dict['Expr'])
        expr_type = QTableWidgetItem(expr_dict['Type'])

        expr_name.setTextAlignment(Qt.AlignCenter)
        expr_math.setTextAlignment(Qt.AlignCenter)
        expr_type.setTextAlignment(Qt.AlignCenter)

        in_alias_list = [row['Alias'] for row in
                         self.application_database.input_table_data]
        out_alias_list = [row['Alias'] for row in
                          self.application_database.output_table_data]

        if is_expression_valid(expr_dict['Expr'],
                               in_alias_list + out_alias_list):
            expr_math.setForeground(QBrush(Qt.green))
        else:
            expr_math.setForeground(QBrush(Qt.red))
            expr_type.setData(Qt.BackgroundRole, QBrush(Qt.red))

        # insert the items into the table
        expr_table_view.setCellWidget(n_rows, self.EXPR_DELETE_COL, delete_btn)
        expr_table_view.setItem(n_rows, self.EXPR_NAME_COL, expr_name)
        expr_table_view.setItem(n_rows, self.EXPR_EXPR_COL, expr_math)
        expr_table_view.setItem(n_rows, self.EXPR_TYPE_COL, expr_type)

    def delete_expression_row(self):
        """Deletes the row where the delete button was clicked and updates the
        application data storage.
        """
        expr_view = self.ui.tableWidgetExpressions
        expr_view.removeRow(expr_view.indexAt(self.sender().pos()).row())

        self.update_expr_data()

    def update_expr_data(self):
        """Updates the application database when the user changes an
        element in the expressions table.
        """
        table_view = self.ui.tableWidgetExpressions
        model = table_view.model()

        expr_info = []
        for row in range(model.rowCount()):
            expr_info.append(
                {'Name': model.data(model.index(row, self.EXPR_NAME_COL)),
                 'Expr': model.data(model.index(row, self.EXPR_EXPR_COL)),
                 'Type': model.data(model.index(row, self.EXPR_TYPE_COL))})

        # store the data
        self.application_database.expression_table_data = expr_info

    def open_simulation_file_dialog(self):
        """Prompts the user to select Aspen Plus simulation files.
        """
        homedir = pathlib.Path().home()
        sim_filename, sim_filetype = QFileDialog.getOpenFileName(
            self, "Select Aspen Plus simulation files.",
            str(homedir),
            "BKP files (*.bkp);; Input files (*.inp)"
        )

        self.application_database.simulation_file = sim_filename

    def open_simulation_tree_dialog(self):
        """Opens a new dialog where the user can select input/output variables
        from the simulation tree.
        """
        dialog = LoadSimulationTreeDialog(self.application_database)
        dialog.exec_()

    def update_simfilepath_display(self):
        """Grabs the simulation file path from app_storage and displays it on
        the text browser widget.
        """
        browser = self.ui.textBrowserSimFile
        sim_file_name = self.application_database.simulation_file
        sim_file_ext = pathlib.Path(sim_file_name).suffix

        if sim_file_name == "" or \
                (sim_file_ext != ".bkp" and sim_file_ext != ".inp"):
            # user canceled the file dialog or selected an invalid file
            if browser.styleSheet() != "color: blue":
                # if there isn't an invalid path in display already
                browser.setText("Invalid or no file selected.")
                browser.setStyleSheet("color: red")

                # deactivate the load simulation tree button
                self.ui.buttonLoadVariables.setEnabled(False)

        else:
            # it's a valid file. Set its path as string and color.
            browser.setText(sim_file_name)
            browser.setStyleSheet("")

            # enable the load simulation tree button
            self.ui.buttonLoadVariables.setEnabled(True)

    def update_siminfo_display(self):
        """Updates the simulation info form display.
        """
        sim_data = self.application_database.simulation_data
        # ----------------------------- Form data -----------------------------

        def siminfo_num_ele(x): return "" if set(sim_data[x]) == set([""]) \
            else str(len(sim_data[x]))

        self.ui.lineEditComponents.setText(siminfo_num_ele('components'))
        self.ui.lineEditBlocks.setText(siminfo_num_ele('blocks'))
        self.ui.lineEditStreams.setText(siminfo_num_ele('streams'))
        self.ui.lineEditMethodName.setText(str(sim_data['therm_method'][0]))
        self.ui.lineEditReactions.setText(siminfo_num_ele('reactions'))
        self.ui.lineEditSensAnalysis.setText(siminfo_num_ele('sens_analysis'))
        self.ui.lineEditCalculators.setText(siminfo_num_ele('calculators'))
        self.ui.lineEditOptimizations.setText(siminfo_num_ele('optimizations'))
        self.ui.lineEditDesSpecs.setText(siminfo_num_ele('design_specs'))

        # ---------------------------- Table data -----------------------------
        if sim_data != self._EMPTY_SIM_INFO:
            sim_info_table = self.ui.tableWidgetSimulationData
            n_rows = len(sim_data[
                max(sim_data, key=lambda x: len(sim_data[x]))])

            # clear the table and intialize new rows
            sim_info_table.setRowCount(0)
            sim_info_table.setRowCount(n_rows)

            key_list = [k for k in sim_data if k != 'therm_method']
            for col in range(len(key_list)):
                for row in range(len(sim_data[key_list[col]])):
                    item = QTableWidgetItem(sim_data[key_list[col]][row])
                    item.setTextAlignment(Qt.AlignCenter)
                    sim_info_table.setItem(row, col, item)

    def update_alias_display(self):
        """Updates the selected alias table display.
        """
        alias_table_view = self.ui.tableWidgetAliasDisplay
        aliases_to_insert = []
        types_to_insert = []
        input_vars = self.application_database.input_table_data
        output_vars = self.application_database.output_table_data

        # clear table
        alias_table_view.setRowCount(0)

        # insert the data
        for row, var in enumerate(input_vars + output_vars):
            alias_table_view.insertRow(row)

            item_alias = QTableWidgetItem(var['Alias'])
            item_type = QTableWidgetItem(var['Type'])

            item_alias.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item_type.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            item_alias.setTextAlignment(Qt.AlignCenter)
            item_type.setTextAlignment(Qt.AlignCenter)

            alias_table_view.setItem(row, 0, item_alias)
            alias_table_view.setItem(row, 1, item_type)

    def update_expr_display(self):
        """Updates the expression data display.
        """
        # clear the table
        self.ui.tableWidgetExpressions.setRowCount(0)

        expr_data = self.application_database.expression_table_data

        for row in expr_data:
            self.insert_expression_row(expr_dict=row)


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook
    app = QApplication(sys.argv)
    w = LoadSimTab(DataStorage())
    w.show()

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
