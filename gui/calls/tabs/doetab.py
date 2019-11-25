import numpy as np
import pandas as pd
from PyQt5.QtCore import (QAbstractItemModel, QAbstractTableModel, QModelIndex,
                          QSize, Qt)
from PyQt5.QtGui import QBrush, QFont, QPalette
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QHeaderView,
                             QTableView, QTableWidgetItem, QWidget)

from gui.calls.dialogs.csveditor import CsvEditorDialog
from gui.calls.dialogs.samplingassistant import SamplingAssistantDialog
from gui.models.data_storage import DataStorage
from gui.views.py_files.doetab import Ui_Form


class InputVariablesTableModel(QAbstractTableModel):
    def __init__(self, application_data: DataStorage, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)
        self.app_data = application_data
        self.load_data()
        self.app_data.doe_mv_bounds_changed.connect(self.load_data)
        self.headers = ["Manipulated variable", "Lower bound", "Upper bound"]

    def load_data(self):
        self.layoutAboutToBeChanged.emit()
        self.mv_bounds = self.app_data.doe_mv_bounds
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return self.mv_bounds.shape[0]

    def columnCount(self, parent=None):
        return self.mv_bounds.shape[1]

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.headers[section]

            else:
                return None

        elif role == Qt.FontRole:
            if orientation == Qt.Horizontal:
                df_font = QFont()
                df_font.setBold(True)
                return df_font
            else:
                return None
        else:
            return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        value = self.mv_bounds.iat[row, col]

        if role == Qt.DisplayRole:
            return str(value)

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.BackgroundRole:
            if col == 1 or col == 2:
                if self.mv_bounds.at[row, 'lb'] >= \
                        self.mv_bounds.at[row, 'ub']:
                    return QBrush(Qt.red)
                else:
                    return QBrush(self.parent().palette().brush(QPalette.Base))
            else:
                return None

        elif role == Qt.ToolTipRole:
            if col == 1 or col == 2:
                if self.mv_bounds.at[row, 'lb'] >= \
                        self.mv_bounds.at[row, 'ub']:
                    return "Lower bound can't be greater than upper bound!"
                else:
                    return ""
            else:
                return None

        else:
            return None

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):
        if role != Qt.EditRole or not index.isValid():
            return False

        row = index.row()
        col = index.column()

        if col == 1:
            self.app_data.doe_mv_bounds.at[row, 'lb'] = float(value)
        elif col == 2:
            self.app_data.doe_mv_bounds.at[row, 'ub'] = float(value)
        else:
            return False

        self.app_data.doe_mv_bounds_changed.emit()
        self.dataChanged.emit(index.sibling(row, 1), index.sibling(row, 2))
        return True

    def flags(self, index: QModelIndex):
        if index.column() != 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | ~Qt.ItemIsEditable


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
        data = self.app_data.doe_sampled_data
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
        if not data.empty:
            self._case_data = data.pop('case')
            self._stat_data = data.pop('status')

        self._data = data[header_list]

        self.layoutChanged.emit()

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
        if not index.isValid():
            return None

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
        bounds_model = InputVariablesTableModel(
            application_data=self.application_database,
            parent=bounds_table)
        bounds_table.setModel(bounds_model)

        bounds_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

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

        # ---------------------------------------------------------------------

    def open_sampling_assistant(self):
        dialog = SamplingAssistantDialog(self.application_database)
        dialog.exec_()

    def open_csveditor(self):
        dialog = CsvEditorDialog(self.application_database)
        dialog.exec_()


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
