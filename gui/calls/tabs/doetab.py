import numpy as np
import pandas as pd
from PyQt5.QtCore import (
    QAbstractItemModel, QAbstractTableModel, QModelIndex, QSize, Qt)
from PyQt5.QtGui import QBrush, QFont, QPalette
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QHeaderView,
                             QTableView, QTableWidgetItem, QWidget)

from gui.calls.base import DoubleEditorDelegate
from gui.calls.dialogs.csveditor import CsvEditorDialog
from gui.calls.dialogs.samplingassistant import (InputBoundsModel,
                                                 SamplingAssistantDialog)
from gui.models.data_storage import DataStorage
from gui.views.py_files.doetab import Ui_Form


class DoeResultsView(QTableView):
    """TableView subclassing overriding the setModel to properly set the first
    and second row headers."""

    def setModel(self, model: QAbstractItemModel):
        super().setModel(model)
        for row in range(model.rowCount()):
            for col in range(model.columnCount()):
                span = model.span(model.index(row, col))
                if span.height() > 1 or span.width() > 1:
                    self.setSpan(row, col, span.height(), span.width())


class DoeResultsModel(QAbstractTableModel):
    """Model to be used as results display of sampled data"""
    _HEADER_ROW_OFFSET = 2
    _INPUT_COL_OFFSET = 2

    def __init__(self, application_data: DataStorage, parent=None):
        QAbstractTableModel.__init__(self, parent)

        self.app_data = application_data
        self.load_data()
        self.app_data.doe_sampled_data_changed.connect(self.load_data)

    def load_data(self):
        self.layoutAboutToBeChanged.emit()
        doe_data = self.app_data.doe_sampled_data.copy(deep=True)
        inp_data = self.app_data.input_table_data
        out_data = self.app_data.output_table_data
        expr_data = self.app_data.expression_table_data

        self._input_alias = inp_data.loc[
            inp_data['Type'] == self.app_data._INPUT_ALIAS_TYPES['mv'],
            'Alias'
        ].tolist()
        cand_data = pd.concat([out_data, expr_data], axis='index',
                              ignore_index=True, sort=False)
        self._candidates_alias = cand_data.loc[
            (cand_data['Type'] == self.app_data._OUTPUT_ALIAS_TYPES['cv']) |
            (cand_data['Type'] == self.app_data._EXPR_ALIAS_TYPES['cv']),
            'Alias'
        ].tolist()
        self._const_alias = expr_data.loc[
            expr_data['Type'] == self.app_data._EXPR_ALIAS_TYPES['cst'],
            'Alias'
        ].tolist()
        self._obj_alias = expr_data.loc[
            expr_data['Type'] == self.app_data._EXPR_ALIAS_TYPES['obj'],
            'Alias'
        ].tolist()
        self._aux_alias = out_data.loc[
            out_data['Type'] == self.app_data._OUTPUT_ALIAS_TYPES['aux'],
            'Alias'
        ].tolist()

        header_list = self._input_alias + self._candidates_alias + \
            self._const_alias + self._obj_alias + self._aux_alias

        # extract the inputs, candidate outputs and expression data
        if not doe_data.empty:
            self._case_data = doe_data.pop('case')
            self._stat_data = doe_data.pop('status')

        self._doe_data = doe_data[header_list]

        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return self._doe_data.shape[0] + self._HEADER_ROW_OFFSET

    def columnCount(self, parent=None):
        return self._doe_data.shape[1] + self._INPUT_COL_OFFSET

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
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        df_rows, df_cols = self._doe_data.shape
        rowoffset = self._HEADER_ROW_OFFSET
        coloffset = self._INPUT_COL_OFFSET

        if role == Qt.DisplayRole:
            if rowoffset - 1 < row < df_rows + rowoffset:
                if coloffset - 1 < col < df_cols + coloffset:
                    # numeric data display
                    val = self._doe_data.iloc[row - rowoffset, col - coloffset]
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
                    return str(self._doe_data.columns[col - coloffset])

        elif role == Qt.FontRole:
            if row == 0 or row == 1:
                df_font = QFont()
                df_font.setBold(True)
                return df_font
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        else:
            return None


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
        bounds_table = self.ui.tableViewInputVariables
        bounds_model = InputBoundsModel(
            application_data=self.application_database,
            parent=bounds_table)
        bounds_table.setModel(bounds_model)

        bounds_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        self._lb_delegate = DoubleEditorDelegate()
        self._ub_delegate = DoubleEditorDelegate()

        bounds_table.setItemDelegateForColumn(1, self._lb_delegate)
        bounds_table.setItemDelegateForColumn(2, self._ub_delegate)

        results_table = DoeResultsView(parent=self.ui.groupBox_4)
        results_model = DoeResultsModel(self.application_database,
                                        parent=results_table)
        results_table.setModel(results_model)

        self.ui.tableViewResultsDoe = results_table
        results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.gridLayout_9.addWidget(results_table, 1, 0, 1, 1)
        results_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        results_table.verticalHeader().hide()

        # --------------------------- Signals/Slots ---------------------------
        # open the sampling assistant dialog
        self.ui.openSamplerPushButton.clicked.connect(
            self.open_sampling_assistant)

        # open the csv editor dialog
        self.ui.csvImportPushButton.clicked.connect(self.open_csveditor)

        self.application_database.doe_mv_bounds_changed.connect(
            self.on_doe_mv_bounds_changed
        )

        # ---------------------------------------------------------------------

    def open_sampling_assistant(self):
        dialog = SamplingAssistantDialog(self.application_database)
        dialog.exec_()

    def open_csveditor(self):
        dialog = CsvEditorDialog(self.application_database)
        dialog.exec_()

    def on_doe_mv_bounds_changed(self):
        # check if the bounds are properly set. If so, enable the radio buttons
        bnd_df = self.application_database.doe_mv_bounds

        if bnd_df['lb'].ge(bnd_df['ub']).any():
            self.ui.samplingAssistantRadioButton.setEnabled(False)
            self.ui.csvEditorRadioButton.setEnabled(False)

            if self.ui.samplingAssistantRadioButton.isChecked():
                self.ui.openSamplerPushButton.setEnabled(False)
            else:
                self.ui.csvImportPushButton.setEnabled(False)
        else:
            self.ui.samplingAssistantRadioButton.setEnabled(True)
            self.ui.csvEditorRadioButton.setEnabled(True)

            if self.ui.samplingAssistantRadioButton.isChecked():
                self.ui.openSamplerPushButton.setEnabled(True)
            else:
                self.ui.csvImportPushButton.setEnabled(True)


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook
    from tests_.mock_data import DOE_TAB_MOCK_DS

    app = QApplication(sys.argv)
    ds = DOE_TAB_MOCK_DS
    w = DoeTab(application_database=ds)
    w.show()

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
