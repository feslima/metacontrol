import pathlib
from PyQt5.QtWidgets import QApplication, QFileDialog, QTableWidgetItem, QCompleter, QWidget, \
    QComboBox, QItemDelegate, QHeaderView, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QBrush, QIcon, QPixmap

from gui.calls.callsimulationtree import LoadSimulationTreeDialog, AliasEditorDelegate
from gui.models.data_storage import DataStorage
from gui.models.math_check import ValidMathStr, is_expression_valid
from gui.views.py_files.loadsimtab import Ui_Form


class LoadSimTab(QWidget):
    # expression table column indexes
    EXPR_DELETE_COL_IDX = 0
    EXPR_NAME_COL_IDX = 1
    EXPR_EXPR_COL_IDX = 2
    EXPR_TYPE_COL_IDX = 3

    def __init__(self, application_database: DataStorage, parent_tab=None, parent_tab_widget=None):
        # ------------------------------ Form Initialization ----------------------------
        super().__init__()
        self.ui = Ui_Form()
        parent_tab = parent_tab if parent_tab is not None else self
        self.ui.setupUi(parent_tab)
        self.parentTabMainWidget = parent_tab_widget

        # ------------------------------ Internal variables ------------------------------
        self.sim_filename = ""
        self.streams_file = None  # for when the tree txt files are specified
        self.blocks_file = None
        self.application_database = application_database

        # ------------------------------ Signal/Slots ------------------------------
        self.ui.buttonOpenSimFile.clicked.connect(self.openSimFileDialog)
        self.ui.buttonLoadVariables.clicked.connect(self.openSimTreeDialog)
        self.ui.buttonAddExpr.clicked.connect(self.insertRowExpression)

        # do a check every time the expression table changes
        self.application_database.exprDataChanged.connect(self.expressionTableCheck)

        # ------------------------------ Widget Initialization ------------------------------
        self.ui.tableWidgetExpressions.setColumnWidth(2, 700)
        self._expr_name_delegate = ExpressionAliasEditorDelegate(self.ui.tableWidgetAliasDisplay)
        self._math_expr_delegate = ExpressionEditorDelegate(self.ui.tableWidgetAliasDisplay, self.application_database)
        self._expr_type_delegate = ComboxBoxExpressionTypeDelegate()
        # update the table when the user changes an element
        self._expr_name_delegate.closeEditor.connect(self.updateExpressionDatabase)
        self._math_expr_delegate.closeEditor.connect(self.updateExpressionDatabase)
        self._expr_type_delegate.closeEditor.connect(self.updateExpressionDatabase)

        self.ui.tableWidgetExpressions.setItemDelegateForColumn(self.EXPR_NAME_COL_IDX, self._expr_name_delegate)
        self.ui.tableWidgetExpressions.setItemDelegateForColumn(self.EXPR_EXPR_COL_IDX, self._math_expr_delegate)
        self.ui.tableWidgetExpressions.setItemDelegateForColumn(self.EXPR_TYPE_COL_IDX, self._expr_type_delegate)
        self.ui.tableWidgetAliasDisplay.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tableWidgetSimulationData.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def deleteExpressionRow(self):
        # delete selected row
        self.ui.tableWidgetExpressions.removeRow(self.ui.tableWidgetExpressions.indexAt(self.sender().pos()).row())

        # and update the expression storage
        self.updateExpressionDatabase()

    # update the application database when the user changes an element in the expressions table
    def updateExpressionDatabase(self):
        # retrieve the current data in table
        table_view = self.ui.tableWidgetExpressions
        table_model = table_view.model()

        expr_info = []
        for row in range(table_model.rowCount()):
            expr_info.append({'Name': table_model.data(table_model.index(row, self.EXPR_NAME_COL_IDX)),
                              'Expr': table_model.data(table_model.index(row, self.EXPR_EXPR_COL_IDX)),
                              'Type': table_model.data(table_model.index(row, self.EXPR_TYPE_COL_IDX))})

        self.application_database.expression_table_data = expr_info  # store the data

    # open simulation file
    def openSimFileDialog(self):
        homedir = str(pathlib.Path.home())  # home directory (platform independent)
        sim_filename, sim_filetype = QFileDialog.getOpenFileName(self, "Select .bkp simulation file", homedir,
                                                                 "BKP files (*.bkp);; Input files (*.inp)")

        self.ui.textBrowserSimFile.setToolTip("")
        if sim_filename == "" or (sim_filetype != "BKP files (*.bkp)" and sim_filetype != "Input files (*.inp)"):
            # user canceled the file dialog or selected invalid file
            if self.ui.textBrowserSimFile.styleSheet() != "color: blue":  # if there isn't an invalid path already
                self.ui.textBrowserSimFile.setText("Invalid or no file selected.")
                self.ui.textBrowserSimFile.setStyleSheet("color: red")
                self.ui.buttonLoadVariables.setEnabled(False)  # deactivate load button

        else:
            # it's a valid file. Set its path as string and color. Also make its filepath available to the ui
            self.sim_filename = sim_filename
            self.ui.textBrowserSimFile.setText(sim_filename)
            self.ui.textBrowserSimFile.setStyleSheet("")
            self.ui.buttonLoadVariables.setEnabled(True)  # activate load button

    # open simulationtree dialog
    def openSimTreeDialog(self):
        if self.sim_filename != "":
            dialog = LoadSimulationTreeDialog(self.sim_filename, self.application_database,
                                              streams_file_txt_path=self.streams_file,
                                              blocks_file_txt_path=self.blocks_file)

            if dialog.exec_():
                # the ok button was pressed, get the variables the user selected and update other ui items
                self.loadDataIntoAliasTables()

    def insertRowExpression(self):
        expr_table_view = self.ui.tableWidgetExpressions
        last_row = expr_table_view.rowCount()
        expr_table_view.insertRow(last_row)

        delete_button = QPushButton(expr_table_view)
        delete_button.clicked.connect(self.deleteExpressionRow)
        icon = QIcon()
        icon.addPixmap(QPixmap(":/loadsim/delete_icon.svg"), QIcon.Normal, QIcon.Off)
        delete_button.setIcon(icon)

        table_expr_name = QTableWidgetItem('expr_' + str(last_row))
        table_expr_name.setTextAlignment(Qt.AlignCenter)

        table_expr_item = QTableWidgetItem('Type expression')
        table_expr_item.setForeground(QBrush(Qt.red))
        table_expr_item.setTextAlignment(Qt.AlignCenter)

        table_item_type = QTableWidgetItem('Choose a type')
        table_item_type.setData(Qt.BackgroundRole, QBrush(Qt.red))

        expr_table_view.setCellWidget(last_row, self.EXPR_DELETE_COL_IDX, delete_button)
        expr_table_view.setItem(last_row, self.EXPR_NAME_COL_IDX, table_expr_name)
        expr_table_view.setItem(last_row, self.EXPR_EXPR_COL_IDX, table_expr_item)
        expr_table_view.setItem(last_row, self.EXPR_TYPE_COL_IDX, table_item_type)

        # append the row to the data
        current_table = self.application_database.expression_table_data
        current_table.append({'Name': table_expr_name.text(),
                              'Expr': table_expr_item.text(),
                              'Type': table_item_type.text()})
        self.application_database.expression_table_data = current_table

    # mock function to load tree from txt file
    def setTreeTxtFilesPath(self, streams_file, blocks_file):
        self.streams_file = streams_file
        self.blocks_file = blocks_file

    def expressionTableCheck(self):
        """
        Check if there are duplicated expression names, invalid names and undefined expression types. If everything is
        ok, enable the sampling tab, otherwise update the expression table information.
        """
        # check if there are duplicated aliases
        expr_table_view = self.ui.tableWidgetExpressions
        expr_model = expr_table_view.model()

        alias_list = [self.ui.tableWidgetAliasDisplay.model().data(
            self.ui.tableWidgetAliasDisplay.model().index(row, 0))
            for row in range(self.ui.tableWidgetAliasDisplay.model().rowCount())]

        expr_info = []
        expr_valid_check = []
        for row in range(expr_model.rowCount()):
            expr_info.append({'Name': expr_model.data(expr_model.index(row, self.EXPR_NAME_COL_IDX)),
                              'Expr': expr_model.data(expr_model.index(row, self.EXPR_EXPR_COL_IDX)),
                              'Type': expr_model.data(expr_model.index(row, self.EXPR_TYPE_COL_IDX))})

            expr_valid_check.append(is_expression_valid(expr_model.data(expr_model.index(row, 2)), alias_list))

        expr_name = [entry['Name'] for entry in expr_info]
        is_name_duplicated = True if len(expr_name + alias_list) != \
                                     len(set(expr_name + alias_list)) else False
        is_exprs_valid = True if len(expr_valid_check) != 0 and all(expr_valid_check) else False

        is_exprs_defined = True if all([entry['Type'] != 'Choose a type' for entry in expr_info]) else False

        # if the expression is not valid, update the expression table colors
        for row in range(expr_model.rowCount()):
            if expr_valid_check[row]:
                expr_model.setData(expr_model.index(row, self.EXPR_EXPR_COL_IDX), QBrush(Qt.green), Qt.ForegroundRole)
            else:
                expr_model.setData(expr_model.index(row, self.EXPR_EXPR_COL_IDX), QBrush(Qt.red), Qt.ForegroundRole)

        if is_exprs_valid and not is_name_duplicated and is_exprs_defined:
            self.parentTabMainWidget.setTabEnabled(1, True)  # enable sampling tab
        else:
            self.parentTabMainWidget.setTabEnabled(1, False)  # disable sampling tab

    def loadDataIntoAliasTables(self):
        vars_list = [self.application_database.input_table_data,
                     self.application_database.output_table_data]

        simulation_form_data = self.application_database.simulation_data

        # -------------------------------- set the simulation form data --------------------------------
        siminfo_lmb_fun = lambda x: '' if simulation_form_data[x] == '' else str(len(simulation_form_data[x]))
        self.ui.lineEditComponents.setText(siminfo_lmb_fun('components'))
        self.ui.lineEditBlocks.setText(siminfo_lmb_fun('blocks'))
        self.ui.lineEditStreams.setText(siminfo_lmb_fun('streams'))
        self.ui.lineEditMethodName.setText(str(simulation_form_data['therm_method'][0]))
        self.ui.lineEditReactions.setText(siminfo_lmb_fun('reactions'))
        self.ui.lineEditSensAnalysis.setText(siminfo_lmb_fun('sens_analysis'))
        self.ui.lineEditCalculators.setText(siminfo_lmb_fun('calculators'))
        self.ui.lineEditOptimizations.setText(siminfo_lmb_fun('optimizations'))
        self.ui.lineEditDesSpecs.setText(siminfo_lmb_fun('design_specs'))

        # -------------------------------- set alias table data --------------------------------
        alias_table_view = self.ui.tableWidgetAliasDisplay

        new_aliases_to_insert = []
        new_types_to_insert = []

        for input_row in vars_list[0]:
            new_aliases_to_insert.append(input_row['Alias'])
            new_types_to_insert.append(input_row['Type'])

        for output_row in vars_list[1]:
            new_aliases_to_insert.append(output_row['Alias'])
            new_types_to_insert.append(output_row['Type'])

        num_rows_alias = alias_table_view.rowCount()

        if num_rows_alias != 0:  # alias table is not empty
            alias_table_view.setRowCount(0)  # delete all the present rows

        for i in range(len(new_aliases_to_insert)):
            alias_table_view.insertRow(i)

            alias_table_item_name = QTableWidgetItem(new_aliases_to_insert[i])
            alias_table_item_type = QTableWidgetItem(new_types_to_insert[i])

            alias_table_item_name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            alias_table_item_type.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            alias_table_item_name.setTextAlignment(Qt.AlignCenter)
            alias_table_item_type.setTextAlignment(Qt.AlignCenter)

            alias_table_view.setItem(i, 0, alias_table_item_name)
            alias_table_view.setItem(i, 1, alias_table_item_type)

        # do a check of expressions
        self.expressionTableCheck()

        # -------------------------------- set the simulation info table data --------------------------------
        if all(simulation_form_data[key] == '' and simulation_form_data['therm_method'] == ['']
               for key in simulation_form_data.keys() if key != 'therm_method'):
            # dictionary is empty
            pass
        else:
            n_rows = len(simulation_form_data[max(simulation_form_data,
                                                  key=lambda x: len(set(simulation_form_data[x])))])
            siminfo_table = self.ui.tableWidgetSimulationData

            # clear the table
            siminfo_table.setRowCount(0)
            siminfo_table.setRowCount(n_rows)

            keys_list = [key for key in simulation_form_data.keys() if key != 'therm_method']
            for col in range(len(keys_list)):
                for r in range(len(simulation_form_data[keys_list[col]])):
                    item = QTableWidgetItem(simulation_form_data[keys_list[col]][r])
                    item.setTextAlignment(Qt.AlignCenter)
                    siminfo_table.setItem(r, col, item)

    def loadDataIntoExpressionTables(self):
        expr_list = self.application_database.expression_table_data

        expr_table_view = self.ui.tableWidgetExpressions
        for row in range(len(expr_list)):
            delete_button = QPushButton(expr_table_view)
            delete_button.clicked.connect(self.deleteExpressionRow)
            icon = QIcon()
            icon.addPixmap(QPixmap(":/loadsim/delete_icon.svg"), QIcon.Normal, QIcon.Off)
            delete_button.setIcon(icon)

            expr_table_view.insertRow(expr_table_view.rowCount())
            table_expr_name = QTableWidgetItem(expr_list[row]['Name'])
            table_expr_name.setTextAlignment(Qt.AlignCenter)

            table_expr_item = QTableWidgetItem(expr_list[row]['Expr'])
            table_expr_item.setTextAlignment(Qt.AlignCenter)

            table_item_type = QTableWidgetItem(expr_list[row]['Type'])
            table_item_type.setTextAlignment(Qt.AlignCenter)

            expr_table_view.setCellWidget(row, self.EXPR_DELETE_COL_IDX, delete_button)
            expr_table_view.setItem(row, self.EXPR_NAME_COL_IDX, table_expr_name)
            expr_table_view.setItem(row, self.EXPR_EXPR_COL_IDX, table_expr_item)
            expr_table_view.setItem(row, self.EXPR_TYPE_COL_IDX, table_item_type)

        self.expressionTableCheck()


class ExpressionAliasEditorDelegate(AliasEditorDelegate):

    def setModelData(self, line_editor, model, index):
        alias_model = self.alias_table.model()
        # override of alias editor delegate to check for duplicates between expressions and aliases
        text = line_editor.text()

        model.setData(index, text, Qt.EditRole)

        # check if the alias is duplicated
        current_expr_names = [model.data(model.index(row, index.column())) for row in range(model.rowCount())]
        current_aliases = [alias_model.data(alias_model.index(row, 0)) for row in range(alias_model.rowCount())]

        if current_expr_names.count(text) > 1 or text in current_aliases:
            model.setData(index, QBrush(Qt.red), Qt.BackgroundRole)
            model.parent().item(index.row(), index.column()).setToolTip('Expression already in use as an alias!')
        else:
            original_backgrd_color = line_editor.palette().color(line_editor.backgroundRole())
            model.setData(index, QBrush(original_backgrd_color), Qt.BackgroundRole)
            model.parent().item(index.row(), index.column()).setToolTip('')


class ExpressionEditorDelegate(QItemDelegate):

    def __init__(self, alias_table, gui_data, parent=None):
        QItemDelegate.__init__(self, parent)
        self.alias_table = alias_table
        self.gui_data = gui_data

    def createEditor(self, parent, option, index):
        line_editor = QLineEdit(parent)
        line_editor.setAlignment(Qt.AlignCenter)

        completer = QCompleter()
        line_editor.setCompleter(completer)

        model = QStringListModel()
        completer.setModel(model)
        completer.setFilterMode(Qt.MatchContains)

        # get aliases in display and set them to the completer
        vars_list = [self.gui_data.input_table_data,
                     self.gui_data.output_table_data]
        if vars_list[0] is not None and vars_list[1] is not None:
            aliases_in_display = []

            aliases_in_display.extend([input_row['Alias'] for input_row in vars_list[0]])
            aliases_in_display.extend([output_row['Alias'] for output_row in vars_list[1]])

            model.setStringList(aliases_in_display)

        # insert the validator
        exp_validator = ValidMathStr(line_editor)
        line_editor.setValidator(exp_validator)

        return line_editor

    def setModelData(self, editor, model, index):
        text = editor.text()
        aliases_in_display = editor.completer().model().stringList()

        model.setData(index, text, Qt.EditRole)
        if is_expression_valid(text, aliases_in_display):
            model.setData(index, QBrush(Qt.green), Qt.ForegroundRole)
        else:
            model.setData(index, QBrush(Qt.red), Qt.ForegroundRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class ComboxBoxExpressionTypeDelegate(QItemDelegate):

    def createEditor(self, parent, option, index):
        combo_box = QComboBox(parent)
        type_list = ["Objective function (J)", "Constraint function", "Candidate (CV)"]

        combo_box.addItems(type_list)

        return combo_box

    def setEditorData(self, combo_box, index):
        combo_box.showPopup()

    def setModelData(self, combo_box, model, index):
        value = combo_box.itemText(combo_box.currentIndex())

        model.setData(index, value, Qt.EditRole)
        original_backgrd_color = combo_box.palette().color(combo_box.backgroundRole())
        model.setData(index, QBrush(original_backgrd_color), Qt.BackgroundRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    w = LoadSimTab(DataStorage(), None, None)
    w.show()

    sys.exit(app.exec_())
