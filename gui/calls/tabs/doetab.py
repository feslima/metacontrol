import numpy as np
import pandas as pd
from py_expression_eval import Parser
from PyQt5.QtCore import (Qt, QSize, QAbstractTableModel, QModelIndex,
                          QAbstractItemModel)
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QHeaderView,
                             QTableView, QTableWidgetItem, QWidget)

from gui.calls.base import DoubleEditorDelegate
from gui.calls.dialogs.csveditor import CsvEditorDialog
from gui.calls.dialogs.samplingassistant import SamplingAssistantDialog
from gui.models.data_storage import DataStorage
from gui.views.py_files.doetab import Ui_Form


class doeResultsView(QTableView):
    """TableView subclassing overriding the setModel to properly set the first
    and second row headers."""

    def setModel(self, model: QAbstractItemModel):
        super().setModel(model)
        for row in range(model.rowCount()):
            for col in range(model.columnCount()):
                span = model.span(model.index(row, col))
                if span.height() > 1 or span.width() > 1:
                    self.setSpan(row, col, span.height(), span.width())


class doeResultsModel(QAbstractTableModel):
    """Model to be used as results display of sampled data"""
    _HEADER_ROW_OFFSET = 2
    _INPUT_COL_OFFSET = 2

    def __init__(self, application_data: DataStorage, parent=None):
        QAbstractTableModel.__init__(self, parent)

        self.app_data = application_data
        data = pd.DataFrame(self.app_data.doe_sampled_data)
        self._case_data = data.pop('case')
        self._stat_data = data.pop('status')

        self._input_alias = [row['Alias']
                             for row in self.app_data.input_table_data
                             if row['Type'] == 'Manipulated (MV)']
        self._candidates_alias = [row['Alias']
                                  for row in self.app_data.output_table_data
                                  if row['Type'] == 'Candidate (CV)'] + \
            [row['Name']
             for row in self.app_data.expression_table_data
             if row['Type'] == 'Candidate (CV)']
        self._const_alias = [row['Name']
                             for row in self.app_data.expression_table_data
                             if row['Type'] == "Constraint function"]
        self._obj_alias = [row['Name']
                           for row in self.app_data.expression_table_data
                           if row['Type'] == "Objective function (J)"]
        self._aux_alias = [row['Alias']
                           for row in self.app_data.input_table_data +
                           self.app_data.output_table_data
                           if row['Type'] == 'Auxiliary']

        # extract the inputs, candidate outputs and expression data
        self._data = data[self._input_alias + self._candidates_alias +
                          self._const_alias + self._obj_alias +
                          self._aux_alias]

    def rowCount(self, parent=None):
        return self._data.shape[0] + self._HEADER_ROW_OFFSET

    def columnCount(self, parent=None):
        return self._data.shape[1] + self._INPUT_COL_OFFSET

    def span(self, index: QModelIndex):
        row = index.row()
        col = index.column()

        rowoffset = self._HEADER_ROW_OFFSET
        coloffset = self._INPUT_COL_OFFSET

        if row == 0:
            if col == 0 or col == 1:
                # case number and status column
                return QSize(1, rowoffset)
            elif col == coloffset:
                # manipulated
                return QSize(len(self._input_alias), 1)
            elif col == coloffset + len(self._input_alias):
                # outputs candidates
                return QSize(len(self._candidates_alias), 1)
            elif col == coloffset + len(self._input_alias) + \
                    len(self._candidates_alias):
                    # constraints
                return QSize(len(self._const_alias), 1)
            elif col == coloffset + len(self._input_alias) + \
                    len(self._candidates_alias) + len(self._const_alias):
                    # objectives
                return QSize(len(self._obj_alias), 1)
            elif col == coloffset + len(self._input_alias) + \
                    len(self._candidates_alias) + len(self._const_alias) + \
                    len(self._obj_alias):
                return QSize(len(self._aux_alias), 1)
            else:
                return super().span(index)
        else:
            return super().span(index)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        row = index.row()
        col = index.column()

        df_rows, df_cols = self._data.shape
        rowoffset = self._HEADER_ROW_OFFSET
        coloffset = self._INPUT_COL_OFFSET

        if role == Qt.DisplayRole:
            if rowoffset - 1 < row < df_rows + rowoffset:
                if coloffset - 1 < col < df_cols + coloffset:
                    # numeric data display
                    val = self._data.iloc[row - rowoffset, col - coloffset]
                    return "{0:.7f}".format(val)

                elif col == 0:
                    # case number
                    return str(int(self._case_data[row - rowoffset]))

                elif col == 1:
                    # status
                    return str(self._stat_data[row - rowoffset])

            elif row == 0:
                # first row headers
                if col == 0:
                    return "Case Number"
                elif col == 1:
                    return "Status"
                elif col == coloffset:
                    return "Inputs - Manipulated"
                elif col == coloffset + len(self._input_alias):
                    return "Outputs - Candidates"
                elif col == coloffset + len(self._input_alias) + \
                        len(self._candidates_alias):
                    return "Outputs - Constraints"
                elif col == coloffset + len(self._input_alias) + \
                        len(self._candidates_alias) + len(self._const_alias):
                    return "Objective"
                elif col == coloffset + len(self._input_alias) + \
                        len(self._candidates_alias) + \
                        len(self._const_alias) + len(self._obj_alias):
                    return "Auxiliary data"
            elif row == 1:
                # second row headers
                if coloffset - 1 < col:
                    return str(self._data.columns[col - coloffset])

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter


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
        self.ui.tableWidgetResultsDoe = doeResultsView(
            parent=self.ui.groupBox_4)
        results_table = self.ui.tableWidgetResultsDoe
        results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.gridLayout_9.addWidget(results_table, 1, 0, 1, 1)

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

        # updates the table data storage
        self.application_database.doe_sampled_data_changed.connect(
            self.update_results_model)

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

        # FIXME: Not triggering doe_mv_bounds_changed

    def update_results_model(self):
        # clear the table model
        results_table = self.ui.tableWidgetResultsDoe

        if results_table.model() is not None:
            results_table.model().setParent(None)
            results_table.model().deleteLater()

        # create the model and set its view
        model = doeResultsModel(self.application_database)

        results_table.setModel(model)


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook
    from tests_.mock_data import DOE_TAB_MOCK_DS

    app = QApplication(sys.argv)
    ds = DOE_TAB_MOCK_DS
    w = DoeTab(application_database=ds)
    ds.doe_mv_bounds_changed.emit()  # just to update the input table on init
    ds.expr_data_changed.emit()  # just to update the results headers
    ds.doe_sampled_data_changed.emit()
    w.show()

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
