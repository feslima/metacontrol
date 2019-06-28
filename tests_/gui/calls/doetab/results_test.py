import pandas as pd
from PyQt5.QtCore import (QAbstractItemModel, QAbstractTableModel, QModelIndex,
                          Qt, QSize)
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QHeaderView,
                             QTableView)

from gui.models.data_storage import DataStorage


class doeResultsView(QTableView):

    def setModel(self, model: QAbstractItemModel):
        super().setModel(model)
        for row in range(model.rowCount()):
            for col in range(model.columnCount()):
                span = model.span(model.index(row, col))
                if span.height() > 1 or span.width() > 1:
                    self.setSpan(row, col, span.height(), span.width())


class doeResultsModel(QAbstractTableModel):
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


if __name__ == "__main__":
    import sys
    from tests_.mock_data import DOE_TAB_MOCK_DS

    app = QApplication(sys.argv)

    w = doeResultsView()
    w.horizontalHeader().hide()
    w.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    w.verticalHeader().hide()

    model = doeResultsModel(DOE_TAB_MOCK_DS)

    w.setModel(model)

    w.show()

    sys.exit(app.exec_())
