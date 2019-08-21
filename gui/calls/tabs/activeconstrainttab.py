from PyQt5.QtCore import QAbstractTableModel, QObject, Qt, QModelIndex
from PyQt5.QtWidgets import QApplication, QTableView, QWidget, QHeaderView
from PyQt5.QtGui import QFont, QBrush

from gui.models.data_storage import DataStorage
from gui.views.py_files.activeconstrainttab import Ui_Form
from gui.calls.base import CheckBoxDelegate, DoubleEditorDelegate

import pandas as pd


class ActiveConstraintTableModel(QAbstractTableModel):

    def __init__(self, app_data: DataStorage, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)
        self.app_data = app_data
        self.load_data()

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
                        return 'Type a value'
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

        if self.con_info.index[row] == 'Active':
            set_value = True if value == 1 else False
            self.con_info.iat[row, col] = set_value

            # change corresponding data in app storage
            alias = self.con_info.columns[col]
            self.app_data.active_constraint_info[alias]['Active'] = set_value

            # update the entire row
            self.dataChanged.emit(index.sibling(row, 0),
                                  index.sibling(row, self.columnCount()))

            return True

        elif self.con_info.index[row] == 'Value':
            value = None if value == '' else float(value)
            self.con_info.iat[row, col] = value

            alias = self.con_info.columns[col]
            self.app_data.active_constraint_info[alias]['Value'] = value

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
                self.con_info[var_name]['Type'] == 'Manipulated (MV)':
            # enable editing only for MV values
            return Qt.ItemIsEditable | Qt.ItemIsEnabled
        else:
            return ~Qt.ItemIsEditable | Qt.ItemIsSelectable


class ActiveConstraintTab(QWidget):
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
        active_table.setItemDelegateForRow(0, self._check_delegate)
        active_table.setItemDelegateForRow(2, self._value_delegate)
        # --------------------------- Signals/Slots ---------------------------
        # ---------------------------------------------------------------------


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook
    from tests_.mock_data import DOE_TAB_MOCK_DS

    app = QApplication(sys.argv)
    # ds = DataStorage()
    ds = DOE_TAB_MOCK_DS
    w = ActiveConstraintTab(application_database=ds)
    w.show()

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
