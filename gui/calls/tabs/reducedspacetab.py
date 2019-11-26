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

        self.con_info = self.app_data.active_constraint_info.copy(deep=True)

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
                if self.con_info.at['Type', var_name] == 'Manipulated (MV)':
                    if value is None:
                        return 'Type an optimal value'
                    else:
                        return str(value)
                else:
                    return None

            elif self.con_info.index[row] == 'Pairing':
                var_name = self.con_info.columns[col]
                if self.con_info.at['Type', var_name] != 'Manipulated (MV)':
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
                    self.con_info.at['Type', var_name] == 'Manipulated (MV)':
                if self.con_info.index[row] == 'Value':
                    # paint cell red if no value is defined for the MVs
                    return QBrush(Qt.red)

            if self.con_info.index[row] == 'Pairing' and \
                    self.con_info.at['Type', var_name] != 'Manipulated (MV)' and \
                    self.con_info.at['Active', var_name] is True:
                # paint cell red if no pairing is selected and the active
                # variable is a constraint (do not paint cells corresponding to
                # MV's)
                if self.con_info.at['Pairing', var_name] is None or \
                        (self.con_info.loc['Pairing', :] ==
                         self.con_info.at['Pairing', var_name]).sum() > 1:
                    return QBrush(Qt.red)

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.CheckStateRole:
            if self.con_info.index[row] == 'Active':
                if self.con_info.iat[row, col]:
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
            value = True if value == 1 else False

            # change corresponding data in app storage
            self.app_data.active_constraint_info.at['Active', alias] = value
            self.app_data.reduced_doe_constraint_activity_changed.emit()

            # update the entire row
            self.dataChanged.emit(index.sibling(row, 0),
                                  index.sibling(row, self.columnCount()))

            return True

        elif self.con_info.index[row] == 'Value':
            value = None if value == '' else float(value)

            self.app_data.active_constraint_info.at['Value', alias] = value
            self.app_data.reduced_doe_constraint_activity_changed.emit()

            self.dataChanged.emit(index.sibling(row, 0),
                                  index.sibling(row, self.columnCount()))

            return True

        elif self.con_info.index[row] == 'Pairing':
            value = None if value == 'Select a MV' else value

            self.app_data.active_constraint_info.at['Pairing', alias] = value
            self.app_data.reduced_doe_constraint_activity_changed.emit()

            self.dataChanged.emit(index.sibling(row, 0),
                                  index.sibling(row, self.columnCount()))

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
                self.con_info.at['Type', var_name] == 'Manipulated (MV)':
            # enable editing only for MV values
            return Qt.ItemIsEditable | Qt.ItemIsEnabled

        elif row_type == 'Pairing' and \
                self.con_info.at['Type', var_name] != 'Manipulated (MV)':
            # enable pairing dropdown if the constraints marked as active are
            # not MV's
            if self.con_info.at['Active', var_name] is True:
                return Qt.ItemIsEditable | Qt.ItemIsEnabled
            else:
                return ~Qt.ItemIsEditable & ~Qt.ItemIsEnabled | \
                    Qt.ItemIsSelectable

        else:
            return ~Qt.ItemIsEditable | Qt.ItemIsSelectable


class ReducedDoeResultsModel(DoeResultsModel):

    def __init__(self, application_data: DataStorage, parent=None):
        QAbstractTableModel.__init__(self, parent)

        self.app_data = application_data
        self.load_data()
        self.app_data.reduced_doe_sampled_data_changed.connect(self.load_data)

    def load_data(self):
        self.layoutAboutToBeChanged.emit()
        doe_data = self.app_data.reduced_doe_sampled_data

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
        return self.d_bounds.shape[0]

    def columnCount(self, parent=None):
        return self.d_bounds.shape[1]

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

        value = self.d_bounds.iat[row, col]

        if role == Qt.DisplayRole:
            return str(value)

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.BackgroundRole or role == Qt.ToolTipRole:
            if col == 1 or col == 2:
                if self.d_bounds.at[row, 'lb'] >= self.d_bounds.at[row, 'ub']:
                    return QBrush(Qt.red) if role == Qt.BackgroundRole \
                        else "Lower bound can't be greater than upper bound!"
                else:
                    par = self.parent()
                    return QBrush(par.palette().brush(QPalette.Base)) \
                        if role == Qt.BackgroundRole else ""

            elif col == 3:
                if self.d_bounds.at[row, 'nominal'] > \
                        self.d_bounds.at[row, 'ub'] or \
                    self.d_bounds.at[row, 'nominal'] < \
                        self.d_bounds.at[row, 'lb']:
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

        d_df = self.app_data.reduced_doe_d_bounds

        if col == 1:
            d_df.at[row, 'lb'] = float(value)
        elif col == 2:
            d_df.at[row, 'ub'] = float(value)
        elif col == 3:
            d_df.at[row, 'nominal'] = float(value)
        else:
            return False

        self.app_data.reduced_doe_d_bounds = d_df

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

        inp_data = self.application_database.input_table_data
        mv_list = inp_data.loc[
            inp_data['Type'] ==
            self.application_database._INPUT_ALIAS_TYPES['mv'],
            'Alias'].tolist()
        self._pairing_delegate = ComboBoxDelegate(item_list=mv_list)

        active_table.setItemDelegateForRow(0, self._check_delegate)
        active_table.setItemDelegateForRow(1, self._pairing_delegate)
        active_table.setItemDelegateForRow(3, self._value_delegate)

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

        # whenever alias data changes, update combobox delegate item list
        self.application_database.input_alias_data_changed.connect(
            self.update_combobox_items
        )
        # ---------------------------------------------------------------------

    def open_reduced_csv_editor(self):
        dialog = ReducedCsvEditorDialog(self.application_database)
        dialog.exec_()

    def update_combobox_items(self):
        inp_data = self.application_database.input_table_data
        mv_list = inp_data.loc[
            inp_data['Type'] ==
            self.application_database._INPUT_ALIAS_TYPES['mv'],
            'Alias'].tolist()
        self._pairing_delegate.item_list = mv_list


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
