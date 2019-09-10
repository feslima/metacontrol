import pandas as pd
from PyQt5.QtCore import (QAbstractTableModel, QModelIndex, QObject,
                          QStringListModel, Qt)
from PyQt5.QtGui import QBrush, QFont, QPalette
from PyQt5.QtWidgets import QApplication, QHeaderView, QTableView, QWidget

from gui.calls.base import (CheckBoxDelegate, ComboBoxDelegate,
                            DoubleEditorDelegate)
from gui.calls.dialogs.reducedcsveditor import ReducedCsvEditorDialog
from gui.calls.tabs.doetab import DoeResultsModel, DoeResultsView
from gui.models.data_storage import DataStorage
from gui.views.py_files.reducedspacetab import Ui_Form


class ActiveConstraintTableModel(QAbstractTableModel):

    def __init__(self, app_data: DataStorage, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)
        self.app_data = app_data
        self.load_data()

        self.app_data.reduced_doe_constraint_activity_changed.connect(
            self.load_data)

    def load_data(self):
        self.layoutAboutToBeChanged.emit()

        self.con_info = pd.DataFrame(self.app_data.active_constraint_info)

        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return self.con_info.shape[0]

    def columnCount(self, parent=None):
        return self.con_info.shape[1]

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        value = self.con_info.iloc[row, col]

        if role == Qt.DisplayRole:
            if self.con_info.index[row] == 'Type':
                return str(value)
            elif self.con_info.index[row] == 'Value':
                # display fields only for MV types
                var_name = self.con_info.columns[col]
                if self.con_info[var_name]['Type'] == 'Manipulated (MV)':
                    if value is None:
                        return 'Type an optimal value'
                    else:
                        return str(value)
                else:
                    return None

            elif self.con_info.index[row] == 'Pairing':
                var_name = self.con_info.columns[col]
                if self.con_info[var_name]['Type'] != 'Manipulated (MV)':
                    if value is None:
                        return "Select a MV"
                    else:
                        return str(value)
                else:
                    return None

            else:
                return None

        elif role == Qt.BackgroundRole:
            var_name = self.con_info.columns[col]
            if value is None and \
                    self.con_info[var_name]['Type'] == 'Manipulated (MV)':
                if self.con_info.index[row] == 'Value':
                    # paint cell red if no value is defined for the MVs
                    return QBrush(Qt.red)

            if self.con_info.index[row] == 'Pairing' and \
                    self.con_info[var_name]['Type'] != 'Manipulated (MV)' and \
                    self.con_info.loc['Active', var_name] is True:
                # paint cell red if no pairing is selected and the active
                # variable is a constraint (do not paint cells corresponding to
                # MV's)
                if self.con_info[var_name]['Pairing'] is None or \
                        (self.con_info.loc['Pairing', :] ==
                         self.con_info[var_name]['Pairing']).sum() > 1:
                    return QBrush(Qt.red)

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.CheckStateRole:
            if self.con_info.index[row] == 'Active':
                if self.con_info.iloc[row, col]:
                    return Qt.Checked
                else:
                    return Qt.Unchecked
            else:
                return None

        else:
            return None

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):
        if role != Qt.EditRole or not index.isValid():
            return False

        row = index.row()
        col = index.column()

        alias = self.con_info.columns[col]

        if self.con_info.index[row] == 'Active':
            set_value = True if value == 1 else False
            self.con_info.iat[row, col] = set_value

            # change corresponding data in app storage
            self.app_data.active_constraint_info[alias]['Active'] = set_value

            # update the entire row
            self.dataChanged.emit(index.sibling(row, 0),
                                  index.sibling(row, self.columnCount()))

            self.app_data.reduced_doe_constraint_activity_changed.emit()

            return True

        elif self.con_info.index[row] == 'Value':
            value = None if value == '' else float(value)
            self.con_info.iat[row, col] = value

            self.app_data.active_constraint_info[alias]['Value'] = value

            self.dataChanged.emit(index.sibling(row, 0),
                                  index.sibling(row, self.columnCount()))

            self.app_data.reduced_doe_constraint_activity_changed.emit()

            return True

        elif self.con_info.index[row] == 'Pairing':
            value = None if value == 'Select a MV' else value
            self.con_info.iat[row, col] = value

            self.app_data.active_constraint_info[alias]['Pairing'] = value

            self.dataChanged.emit(index.sibling(row, 0),
                                  index.sibling(row, self.columnCount()))

            self.app_data.reduced_doe_constraint_activity_changed.emit()

            return True

        else:
            return False

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self.con_info.columns[section]

            elif role == Qt.FontRole:
                df_font = QFont()
                df_font.setBold(True)
                return df_font

            else:
                return None

        elif orientation == Qt.Vertical:
            if role == Qt.DisplayRole:
                return self.con_info.index[section]

            elif role == Qt.FontRole:
                df_font = QFont()
                df_font.setBold(True)
                return df_font

            else:
                return None

        else:
            return None

    def flags(self, index: QModelIndex):
        row = index.row()
        col = index.column()

        row_type = self.con_info.index[row]
        var_name = self.con_info.columns[col]

        if row_type == 'Active':
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | \
                Qt.ItemIsUserCheckable

        elif row_type == 'Value' and \
                self.con_info[var_name]['Type'] == 'Manipulated (MV)':
            # enable editing only for MV values
            return Qt.ItemIsEditable | Qt.ItemIsEnabled

        elif row_type == 'Pairing' and \
                self.con_info[var_name]['Type'] != 'Manipulated (MV)':
            # enable pairing dropdown if the constraints marked as active are
            # not MV's
            if self.con_info.loc['Active', var_name] is True:
                return Qt.ItemIsEditable | Qt.ItemIsEnabled
            else:
                return ~Qt.ItemIsEditable & ~Qt.ItemIsEnabled | \
                    Qt.ItemIsSelectable

        else:
            return ~Qt.ItemIsEditable | Qt.ItemIsSelectable


class ReducedDoeResultsModel(DoeResultsModel):

    def load_data(self):
        self.layoutAboutToBeChanged.emit()
        data = pd.DataFrame(self.app_data.reduced_doe_sampled_data)

        self._input_alias = [row['Alias']
                             for row in self.app_data.input_table_data
                             if row['Type'] == 'Manipulated (MV)']
        self._candidates_alias = [row['Alias']
                                  for row in self.app_data.output_table_data
                                  if row['Type'] == 'Candidate (CV)'] + \
            [row['Alias']
             for row in self.app_data.expression_table_data
             if row['Type'] == 'Candidate (CV)']
        self._const_alias = [row['Alias']
                             for row in self.app_data.expression_table_data
                             if row['Type'] == "Constraint function"]
        self._obj_alias = [row['Alias']
                           for row in self.app_data.expression_table_data
                           if row['Type'] == "Objective function (J)"]
        self._aux_alias = [row['Alias']
                           for row in self.app_data.input_table_data +
                           self.app_data.output_table_data
                           if row['Type'] == 'Auxiliary']

        header_list = self._input_alias + self._candidates_alias + \
            self._const_alias + self._obj_alias + self._aux_alias

        # extract the inputs, candidate outputs and expression data
        if not data.empty:
            self._case_data = data.pop('case')
            self._stat_data = data.pop('status')

        self._data = data[header_list]

        self.layoutChanged.emit()


class RangeOfDisturbanceTableModel(QAbstractTableModel):
    def __init__(self, app_data: DataStorage, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)
        self.app_data = app_data
        self.load_data()
        self.headers = ["Disturbance variable", "Lower bound", "Upper bound",
                        "Nominal Value"]
        self.app_data.reduced_d_bounds_changed.connect(self.load_data)

    def load_data(self):
        self.layoutAboutToBeChanged.emit()

        self.d_bounds = self.app_data.reduced_doe_d_bounds

        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return len(self.d_bounds)

    def columnCount(self, parent=None):
        return len(self.headers)

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.headers[section]

            else:
                return None

        elif role == Qt.FontRole:
            if orientation == Qt.Horizontal or orientation == Qt.Vertical:
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

        d_data = self.d_bounds[row]

        if role == Qt.DisplayRole:
            if col == 0:
                return str(d_data['name'])
            elif col == 1:
                return str(d_data['lb'])
            elif col == 2:
                return str(d_data['ub'])
            elif col == 3:
                return str(d_data['nom'])
            else:
                return None

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.BackgroundRole or role == Qt.ToolTipRole:
            if col == 1 or col == 2:
                if d_data['lb'] >= d_data['ub']:
                    return QBrush(Qt.red) if role == Qt.BackgroundRole \
                        else "Lower bound can't be greater than upper bound!"
                else:
                    par = self.parent()
                    return QBrush(par.palette().brush(QPalette.Base)) \
                        if role == Qt.BackgroundRole else ""

            elif col == 3:
                if d_data['nom'] > d_data['ub'] or \
                        d_data['nom'] < d_data['lb']:
                    return QBrush(Qt.red) if role == Qt.BackgroundRole \
                        else "Nominal value must be between lower and upper " \
                        "bound!"
                else:
                    par = self.parent()
                    return QBrush(par.palette().brush(QPalette.Base)) \
                        if role == Qt.BackgroundRole else ""

            else:
                return None

        else:
            return None

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):
        if role != Qt.EditRole or not index.isValid():
            return False

        row = index.row()
        col = index.column()

        var_data = self.d_bounds[row]

        if col == 1:
            var_data['lb'] = float(value)
        elif col == 2:
            var_data['ub'] = float(value)
        elif col == 3:
            var_data['nom'] = float(value)
        else:
            return False

        self.dataChanged.emit(index.sibling(row, 1), index.sibling(row, 2))
        return True

    def flags(self, index: QModelIndex):
        if index.column() != 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | ~Qt.ItemIsEditable


class ReducedSpaceTab(QWidget):
    def __init__(self, application_database: DataStorage, parent_tab=None):
        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Form()
        parent_tab = parent_tab if parent_tab is not None else self
        self.ui.setupUi(parent_tab)

        # ------------------------ Internal Variables -------------------------
        self.application_database = application_database
        # ----------------------- Widget Initialization -----------------------
        active_table = self.ui.activeConstraintTableView
        active_model = ActiveConstraintTableModel(self.application_database,
                                                  parent=active_table)
        active_table.setModel(active_model)

        active_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        self._check_delegate = CheckBoxDelegate()
        self._value_delegate = DoubleEditorDelegate()

        mv_list = [row['Alias']
                   for row in self.application_database.input_table_data
                   if row['Type'] == 'Manipulated (MV)']
        self._pairing_delegate = ComboBoxDelegate(item_list=mv_list)

        active_table.setItemDelegateForRow(0, self._check_delegate)
        active_table.setItemDelegateForRow(1, self._pairing_delegate)
        active_table.setItemDelegateForRow(2, self._value_delegate)

        dist_table = self.ui.disturbanceRangeTableView
        dist_model = RangeOfDisturbanceTableModel(self.application_database,
                                                  parent=dist_table)
        dist_table.setModel(dist_model)
        dist_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        self._dlb_delegate = DoubleEditorDelegate()
        self._dub_delegate = DoubleEditorDelegate()
        self._dnom_delegate = DoubleEditorDelegate()

        dist_table.setItemDelegateForColumn(1, self._dlb_delegate)
        dist_table.setItemDelegateForColumn(2, self._dub_delegate)
        dist_table.setItemDelegateForColumn(3, self._dnom_delegate)

        results_table = self.ui.reducedDataResultTableView
        results_model = ReducedDoeResultsModel(self.application_database,
                                               parent=results_table)
        results_table.setModel(results_model)
        results_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        # --------------------------- Signals/Slots ---------------------------
        # open the reduced space csv editor dialog
        self.ui.openCsvEditorPushButton.clicked.connect(
            self.open_reduced_csv_editor)

        # whenever reduced doe sampled data changes, update the table
        self.application_database.reduced_doe_sampled_data_changed.connect(
            results_model.load_data
        )
        # ---------------------------------------------------------------------

    def open_reduced_csv_editor(self):
        dialog = ReducedCsvEditorDialog(self.application_database)
        dialog.exec_()


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook
    from tests_.mock_data import DOE_TAB_MOCK_DS

    app = QApplication(sys.argv)
    # ds = DataStorage()
    ds = DOE_TAB_MOCK_DS
    w = ReducedSpaceTab(application_database=ds)
    w.show()

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
