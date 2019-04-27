import numpy as np
from py_expression_eval import Parser

from PyQt5.QtWidgets import QApplication, QWidget, QHeaderView, QFileDialog, QTableWidgetItem, QItemDelegate, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QBrush

from gui.views.py_files.doetab import Ui_Form
from gui.calls.callsamplingassistant import SamplingAssistantDialog
from gui.models.data_storage import DataStorage
from gui.calls.callcsveditor import CsvEditorDialog


class DoeTab(QWidget):
    def __init__(self, application_database: DataStorage, parent_widget=None):
        # ------------------------------ Form Initialization ----------------------------
        super().__init__()
        self.ui = Ui_Form()
        parent_widget = parent_widget if parent_widget is not None else self
        self.ui.setupUi(parent_widget)

        self.application_database = application_database

        # ------------------------------ WidgetInitialization ------------------------------
        self.ui.tableWidgetInputVariables.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tableWidgetResultsDoe.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self._lb_itemdelegate = BoundEditorDelegate()
        self._ub_itemdelegate = BoundEditorDelegate()
        self.ui.tableWidgetInputVariables.setItemDelegateForColumn(1, self._lb_itemdelegate)
        self.ui.tableWidgetInputVariables.setItemDelegateForColumn(2, self._ub_itemdelegate)

        # ------------------------------ Signals/Slots ------------------------------
        self.application_database.doeMvDataChanged.connect(self.loadInputVariables)
        self.application_database.inputAliasDataChanged.connect(self.loadResultsTable)
        self.application_database.outputAliasDataChanged.connect(self.loadResultsTable)
        self.application_database.exprDataChanged.connect(self.loadResultsTable)
        self._lb_itemdelegate.closeEditor.connect(self.updateDoeMvStorage)
        self._ub_itemdelegate.closeEditor.connect(self.updateDoeMvStorage)
        self.ui.openSamplerPushButton.clicked.connect(self.openSamplingAssistant)
        self.ui.csvImportPushButton.clicked.connect(self.openCsvImportDialog)

        # ------------------------------ Internal variables ------------------------------
        self._doe_results_table = None
        self.parser = Parser()

    def openSamplingAssistant(self):
        samp_dialog = SamplingAssistantDialog(self.application_database)
        if samp_dialog.exec_():
            self._set_data_from_samp_dialog(samp_dialog.sampled_data)

    def openCsvImportDialog(self):
        csv_editor_dialog = CsvEditorDialog(self.application_database)
        if csv_editor_dialog.exec_():
            self._set_data_from_samp_dialog(csv_editor_dialog.sampled_data)

    def _set_data_from_samp_dialog(self, samp_data):
        if len(samp_data) == 0:  # table is empty
            input_index = []
            const_index = []
            obj_index = []
            conv_flags = []
        else:
            cast_samp = np.asfarray(samp_data)
            conv_flags = cast_samp[:, 0].tolist()
            samp_data = cast_samp[:, 1:]

            # display the data
            results_table_view = self.ui.tableWidgetResultsDoe
            input_alias_list = [row['Alias'] for row in self.application_database.input_table_data
                                if row['Type'] == 'Manipulated (MV)']
            output_alias_list = [row['Alias'] for row in self.application_database.output_table_data]
            expr_list = [row['Name'] for row in self.application_database.expression_table_data]

            results_table_view.setRowCount(2)
            results_table_view.setColumnCount(1 + len(input_alias_list + output_alias_list + expr_list))
            results_table_view.setSpan(0, 0, 2, 1)
            results_table_view.setItem(0, 0, QTableWidgetItem('Case Number'))
            results_table_view.item(0, 0).setTextAlignment(Qt.AlignCenter)

            results_table_view.setSpan(0, 1, 1, len(input_alias_list))
            results_table_view.setItem(0, 1, QTableWidgetItem('Inputs'))
            results_table_view.item(0, 1).setTextAlignment(Qt.AlignCenter)

            results_table_view.setSpan(0, 3, 1, len(output_alias_list + expr_list))
            results_table_view.setItem(0, 3, QTableWidgetItem('Outputs'))
            results_table_view.item(0, 3).setTextAlignment(Qt.AlignCenter)

            # place the subheaders (alias) in the second row
            all_alias = input_alias_list + output_alias_list + expr_list
            for j in range(len(all_alias)):
                item_place_holder = QTableWidgetItem(all_alias[j])
                results_table_view.setItem(1, j + 1, item_place_holder)
                item_place_holder.setTextAlignment(Qt.AlignCenter)

            # expando rows and place data
            rows, cols_samp = samp_data.shape
            results_table_view.setRowCount(2 + rows)
            for row in range(rows):
                case_num_placeholder = QTableWidgetItem(str(row + 1))
                case_num_placeholder.setTextAlignment(Qt.AlignCenter)
                results_table_view.setItem(2 + row, 0, case_num_placeholder)

                expr_var_values_dict = dict(zip(output_alias_list, samp_data[row, len(input_alias_list):].tolist()))

                for col in range(cols_samp):
                    sampled_values_placeholder = QTableWidgetItem(str(samp_data[row, col]))
                    sampled_values_placeholder.setTextAlignment(Qt.AlignCenter)
                    results_table_view.setItem(row + 2, col + 1, sampled_values_placeholder)

                # evaluate the expressions
                for col_idx, expr_dict in enumerate(self.application_database.expression_table_data):
                    expr_value = self.parser.parse(expr_dict['Expr']).evaluate(expr_var_values_dict)
                    expr_value_placeholder = QTableWidgetItem(str(expr_value))
                    expr_value_placeholder.setTextAlignment(Qt.AlignCenter)
                    results_table_view.setItem(row + 2, cols_samp + col_idx + 1, expr_value_placeholder)

            # set the input, constraint and objective indexes
            input_index = [results_table_view.findItems(alias, Qt.MatchExactly)[0].column()
                           for alias in input_alias_list]
            const_index = [results_table_view.findItems(alias, Qt.MatchExactly)[0].column() for alias in
                           [row['Name'] for row in self.application_database.expression_table_data
                            if row['Type'] == 'Constraint function']]
            obj_index = [results_table_view.findItems(alias, Qt.MatchExactly)[0].column() for alias in
                         [row['Name'] for row in self.application_database.expression_table_data
                          if row['Type'] == 'Objective function (J)']]

            # uncast the data from np to list
            samp_data = samp_data.tolist()

        self.application_database.doe_sampled_data = {'input_index': input_index,
                                                      'constraint_index': const_index,
                                                      'objective_index': obj_index,
                                                      'convergence_flag': conv_flags,
                                                      'data': samp_data}

    def loadInputVariables(self):
        # load the MV aliases into the variable table
        mv_alias_data = self.application_database.doe_data

        mv_alias_list, lb_list, ub_list = zip(*[row.values() for row in mv_alias_data['mv']])

        table_view = self.ui.tableWidgetInputVariables

        # clear the table rows
        table_view.setRowCount(0)

        # insert the aliases and validators
        for row in range(len(mv_alias_list)):
            table_view.insertRow(row)
            alias_item = QTableWidgetItem(mv_alias_list[row])
            alias_item.setTextAlignment(Qt.AlignCenter)
            alias_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # disable the edit

            table_view.setItem(row, 0, alias_item)

            table_view.setItem(row, 1, QTableWidgetItem(str(lb_list[row])))
            table_view.item(row, 1).setTextAlignment(Qt.AlignCenter)
            table_view.setItem(row, 2, QTableWidgetItem(str(ub_list[row])))
            table_view.item(row, 2).setTextAlignment(Qt.AlignCenter)

        self.inputTableCheck()

    def loadResultsTable(self):
        # load the headers
        results_table_view = self.ui.tableWidgetResultsDoe
        input_alias_list = [row['Alias'] for row in self.application_database.input_table_data
                            if row['Type'] == 'Manipulated (MV)']
        output_alias_list = [row['Alias'] for row in self.application_database.output_table_data]

        expr_list = [row['Name'] for row in self.application_database.expression_table_data]

        # clear the table
        results_table_view.setColumnCount(0)
        results_table_view.setRowCount(0)

        # place the headers in the first and second rows
        results_table_view.setRowCount(2)
        results_table_view.setColumnCount(len(input_alias_list + output_alias_list + expr_list))
        results_table_view.setSpan(0, 0, 1, len(input_alias_list))
        results_table_view.setItem(0, 0, QTableWidgetItem('Inputs'))
        results_table_view.item(0, 0).setTextAlignment(Qt.AlignCenter)
        results_table_view.setSpan(0, 2, 1, len(output_alias_list + expr_list))
        results_table_view.setItem(0, 2, QTableWidgetItem('Outputs'))
        results_table_view.item(0, 2).setTextAlignment(Qt.AlignCenter)

        # place the subheaders (alias) in the second row
        all_alias = input_alias_list + output_alias_list + expr_list
        for j in range(len(all_alias)):
            item_place_holder = QTableWidgetItem(all_alias[j])
            results_table_view.setItem(1, j, item_place_holder)
            item_place_holder.setTextAlignment(Qt.AlignCenter)

        if self._doe_results_table is not None:
            results_table_view.setRowCount(self._doe_results_table.shape[0] + 2)  # expand the rows

            for row in range(self._doe_results_table.shape[0]):
                for col in range(self._doe_results_table.shape[1]):
                    item_place_holder = QTableWidgetItem(str(self._doe_results_table[row, col]))
                    results_table_view.setItem(2 + row, col, item_place_holder)
                    item_place_holder.setTextAlignment(Qt.AlignCenter)

        # results_table_view.setHorizontalHeaderLabels(alias_list + expr_list)

    # check the input variables table
    def inputTableCheck(self):
        table_view = self.ui.tableWidgetInputVariables

        lb_list = []
        ub_list = []
        flag_list = []
        for row in range(table_view.rowCount()):
            lb_list.append(float(table_view.item(row, 1).text()))
            ub_list.append(float(table_view.item(row, 2).text()))
            flag_list.append(lb_list[row] < ub_list[row])

        is_bound_set = all(flag_list)

        if is_bound_set:  # paint/repaint cells

            org_color = table_view.palette().color(table_view.backgroundRole())

            for row in range(table_view.rowCount()):
                table_view.model().setData(table_view.model().index(row, 1), QBrush(org_color), Qt.BackgroundRole)
                table_view.model().setData(table_view.model().index(row, 2), QBrush(org_color), Qt.BackgroundRole)
        else:
            row_to_paint = [idx for idx, e in enumerate(flag_list) if e is False]
            for row in row_to_paint:
                table_view.model().setData(table_view.model().index(row, 1), QBrush(Qt.red), Qt.BackgroundRole)
                table_view.model().setData(table_view.model().index(row, 2), QBrush(Qt.red), Qt.BackgroundRole)

    # update the doe data storage
    def updateDoeMvStorage(self):
        table_view = self.ui.tableWidgetInputVariables
        mv_bound_info = []
        for row in range(table_view.rowCount()):
            mv_bound_info.append({'name': table_view.item(row, 0).text(),
                                  'lb': table_view.item(row, 1).text(),
                                  'ub': table_view.item(row, 2).text()})

        self.application_database.doe_mv_data = mv_bound_info


class BoundEditorDelegate(QItemDelegate):

    def createEditor(self, parent, option, index):
        line_editor = QLineEdit(parent)
        double_validator = QDoubleValidator(line_editor)
        line_editor.setValidator(double_validator)

        return line_editor

    def setModelData(self, editor, model, index):
        text = editor.text()

        model.setData(index, text, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


if __name__ == "__main__":
    import sys
    from gui.models.data_storage import DataStorage
    from tests_.gui.mock_data import mock_storage

    app = QApplication(sys.argv)

    w = DoeTab(mock_storage)
    w.show()


    def my_exception_hook(exctype, value, tback):
        # Print the error and traceback
        print(exctype, value, tback)
        # Call the normal Exception hook after
        sys.__excepthook__(exctype, value, tback)
        sys.exit()


    sys._excepthook = sys.excepthook

    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
