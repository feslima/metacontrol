import numpy as np
import pandas as pd
from py_expression_eval import Parser
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import (QApplication, QHeaderView, QTableWidgetItem,
                             QWidget)

from gui.models.data_storage import DataStorage
from gui.views.py_files.doetab import Ui_Form
from gui.calls.base import DoubleEditorDelegate
from gui.calls.dialogs.samplingassistant import SamplingAssistantDialog
from gui.calls.dialogs.csveditor import CsvEditorDialog


class BoundEditorDelegate(DoubleEditorDelegate):

    def setModelData(self, editor, model, index):
        text = editor.text()

        model.setData(index, text, Qt.EditRole)

        item_row = index.row()
        item_col = index.column()

        if item_col == 1:
            # lower bound
            sib_index = index.sibling(item_row, item_col + 1)
            lb_value = float(text)
            ub_value = float(model.data(sib_index, Qt.DisplayRole))
        else:
            # upper bound
            sib_index = index.sibling(item_row, item_col - 1)
            lb_value = float(model.data(sib_index, Qt.DisplayRole))
            ub_value = float(text)

        if lb_value >= ub_value:
            # lb >= ub, paint row red
            model.setData(index, QBrush(Qt.red), Qt.BackgroundRole)
            model.setData(sib_index, QBrush(Qt.red), Qt.BackgroundRole)
        else:
            # lb < ub, paint original color
            org_bck_clr = editor.palette().color(editor.backgroundRole())
            model.setData(index, QBrush(org_bck_clr), Qt.BackgroundRole)
            model.setData(sib_index, QBrush(org_bck_clr), Qt.BackgroundRole)


class DoeTab(QWidget):

    # CONSTANTS
    _INPUT_COL_OFFSET = 2
    _HEADER_ROW_OFFSET = 2

    def __init__(self, application_database: DataStorage, parent_tab=None):
        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Form()
        parent_tab = parent_tab if parent_tab is not None else self
        self.ui.setupUi(parent_tab)

        # ------------------------ Internal Variables -------------------------
        self.application_database = application_database

        # ----------------------- Widget Initialization -----------------------
        var_table = self.ui.tableWidgetInputVariables
        results_table = self.ui.tableWidgetResultsDoe

        var_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        results_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        results_table.verticalHeader().hide()

        # set bound values delegates
        self._lb_delegate = BoundEditorDelegate()
        self._ub_delegate = BoundEditorDelegate()
        var_table.setItemDelegateForColumn(1, self._lb_delegate)
        var_table.setItemDelegateForColumn(2, self._ub_delegate)

        # --------------------------- Signals/Slots ---------------------------
        # update the input variable display info
        self.application_database.doe_mv_bounds_changed.connect(
            self.update_input_variables_display)

        # update the input variable storage
        self._lb_delegate.closeEditor.connect(self.update_input_variables_data)
        self._ub_delegate.closeEditor.connect(self.update_input_variables_data)

        # open the sampling assistant dialog
        self.ui.openSamplerPushButton.clicked.connect(
            self.open_sampling_assistant)

        # open the csv editor dialog
        self.ui.csvImportPushButton.clicked.connect(self.open_csveditor)

        # update the results table headers whenever a variable or expression
        # alias changes
        self.application_database.input_alias_data_changed.connect(
            self.update_results_headers_display)
        self.application_database.output_alias_data_changed.connect(
            self.update_results_headers_display)
        self.application_database.expr_data_changed.connect(
            self.update_results_headers_display)

        # update the results table data whenever the sampled data changes
        self.application_database.doe_sampled_data_changed.connect(
            self.update_results_data_display)
        # ---------------------------------------------------------------------

    def open_sampling_assistant(self):
        dialog = SamplingAssistantDialog(self.application_database)
        dialog.exec_()

    def open_csveditor(self):
        dialog = CsvEditorDialog(self.application_database)
        dialog.exec_()

    def update_input_variables_display(self):
        """Updates the input variables table display. Model to View.
        """
        mv_bnd_data = self.application_database.doe_mv_bounds

        aliases, lb_bnds, ub_bnds = zip(*[row.values() for row in mv_bnd_data])

        table_view = self.ui.tableWidgetInputVariables

        # clear the table
        table_view.setRowCount(0)

        # insert the variables
        for row, alias in enumerate(aliases):
            table_view.insertRow(row)

            alias_item = QTableWidgetItem(alias)
            lb_item = QTableWidgetItem(str(lb_bnds[row]))
            ub_item = QTableWidgetItem(str(ub_bnds[row]))

            alias_item.setTextAlignment(Qt.AlignCenter)
            lb_item.setTextAlignment(Qt.AlignCenter)
            ub_item.setTextAlignment(Qt.AlignCenter)

            alias_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            table_view.setItem(row, 0, alias_item)
            table_view.setItem(row, 1, lb_item)
            table_view.setItem(row, 2, ub_item)

    def update_input_variables_data(self):
        """Updates the input variables (MVs) data in the application storage.
        View to Model.
        """
        table_view = self.ui.tableWidgetInputVariables

        mv_bnd = []
        for row in range(table_view.rowCount()):
            mv_bnd.append({'name': table_view.item(row, 0).text(),
                           'lb': float(table_view.item(row, 1).text()),
                           'ub': float(table_view.item(row, 2).text())})

    def update_results_headers_display(self):
        """Update the sampled data table headers from application data storage.
        Model to View.
        """
        results_view = self.ui.tableWidgetResultsDoe

        # display the headers
        input_alias = [row['Alias']
                       for row in self.application_database.input_table_data
                       if row['Type'] == 'Manipulated (MV)']
        output_alias = [row['Alias']
                        for row in self.application_database.output_table_data]
        expr_alias = [row['Name'] for row in
                      self.application_database.expression_table_data]

        aliases = input_alias + output_alias + expr_alias

        # clear the table
        results_view.setRowCount(self._HEADER_ROW_OFFSET)
        results_view.setColumnCount(len(aliases) + self._INPUT_COL_OFFSET)

        # case number header
        case_num_item = QTableWidgetItem('Case Number')
        case_num_item.setTextAlignment(Qt.AlignCenter)
        results_view.setSpan(0, 0, self._HEADER_ROW_OFFSET, 1)
        results_view.setItem(0, 0, case_num_item)

        # case status header
        case_status_item = QTableWidgetItem('Status')
        case_status_item.setTextAlignment(Qt.AlignCenter)
        results_view.setSpan(0, 1, self._HEADER_ROW_OFFSET, 1)
        results_view.setItem(0, 1, case_status_item)

        # Inputs section header
        inputs_item = QTableWidgetItem('Inputs')
        inputs_item.setTextAlignment(Qt.AlignCenter)
        results_view.setSpan(0, self._INPUT_COL_OFFSET, 1, len(input_alias))
        results_view.setItem(0, self._INPUT_COL_OFFSET, inputs_item)

        # Outputs section header
        outputs_item = QTableWidgetItem('Outputs')
        outputs_item.setTextAlignment(Qt.AlignCenter)
        results_view.setSpan(0, self._INPUT_COL_OFFSET +
                             self._INPUT_COL_OFFSET, 1, len(output_alias +
                                                            expr_alias))
        results_view.setItem(0, self._INPUT_COL_OFFSET +
                             self._INPUT_COL_OFFSET, outputs_item)

        # place the subheaders
        for col, alias in enumerate(aliases):
            item = QTableWidgetItem(alias)
            item.setTextAlignment(Qt.AlignCenter)

            results_view.setItem(1, col + self._INPUT_COL_OFFSET, item)

    def update_results_data_display(self):
        """Update the sampled data table values from application data storage.
        Model to View.
        """
        results_view = self.ui.tableWidgetResultsDoe

        sampled_data = pd.DataFrame(self.application_database.doe_sampled_data)
        n_rows, n_cols = sampled_data.shape
        results_view.setRowCount(self._HEADER_ROW_OFFSET + n_rows)

        headers = [results_view.item(1, col + self._INPUT_COL_OFFSET).text()
                   for col in
                   range(len(self.application_database.input_table_data +
                             self.application_database.output_table_data +
                             self.application_database.expression_table_data))]
        for row in range(n_rows):
            case_num = QTableWidgetItem(str(int(sampled_data['case'][row])))
            case_num.setTextAlignment(Qt.AlignCenter)
            results_view.setItem(self._HEADER_ROW_OFFSET + row, 0, case_num)

            case_status = QTableWidgetItem(sampled_data['status'][row])
            case_status.setTextAlignment(Qt.AlignCenter)
            results_view.setItem(self._HEADER_ROW_OFFSET + row, 1, case_status)

            for col, alias in enumerate(headers):
                value = QTableWidgetItem(str(sampled_data[alias][row]))
                value.setTextAlignment(Qt.AlignCenter)
                results_view.setItem(self._HEADER_ROW_OFFSET + row,
                                     self._INPUT_COL_OFFSET + col, value)


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook
    from tests_.mock_data import DOE_TAB_MOCK_DS

    app = QApplication(sys.argv)
    ds = DOE_TAB_MOCK_DS
    w = DoeTab(application_database=ds)
    ds.doe_mv_bounds_changed.emit()  # just to update the input table on init
    ds.expr_data_changed.emit()  # just to update the results headers
    ds.doe_sampled_data_changed.emit()  # just to update results data
    w.show()

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
