from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtGui import QBrush, QFont, QPalette
from PyQt5.QtWidgets import QApplication, QHeaderView, QTableView, QWidget

from gui.calls.base import CheckBoxDelegate, DoubleEditorDelegate
from gui.models.data_storage import DataStorage
from gui.views.py_files.metamodeltab import Ui_Form


class ThetaTableModel(QAbstractTableModel):
    def __init__(self, application_data: DataStorage, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)
        self.app_data = application_data
        self.load_data()
        self.headers = ['Variable', 'Lower Bound', 'Upper Bound', 'Estimate']

        self.app_data.alias_data_changed.connect(self.load_data)

    def load_data(self):
        self.layoutAboutToBeChanged.emit()
        self.theta_data = self.app_data.metamodel_theta_data
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return len(self.theta_data)

    def columnCount(self, parent):
        return len(self.headers)

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):

        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self.headers[section]

            elif role == Qt.FontRole:
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

        theta_row = self.theta_data[row]

        if role == Qt.DisplayRole:
            if col == 0:
                return str(theta_row['Alias'])
            elif col == 1:
                return str(theta_row['lb'])
            elif col == 2:
                return str(theta_row['ub'])
            elif col == 3:
                return str(theta_row['theta0'])
            else:
                return None

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.BackgroundColorRole:
            if col == 1 or col == 2:
                if theta_row['lb'] >= theta_row['ub']:
                    return QBrush(Qt.red)
                else:
                    return QBrush(self.parent().palette().brush(QPalette.Base))

            elif col == 3:
                if theta_row['theta0'] < theta_row['lb'] or \
                        theta_row['theta0'] > theta_row['ub']:
                    return QBrush(Qt.red)
                else:
                    return QBrush(self.parent().palette().brush(QPalette.Base))
            else:
                return None

        elif role == Qt.ToolTipRole:
            if col == 1 or col == 2:
                if theta_row['lb'] >= theta_row['ub']:
                    return "Lower bound can't be greater than upper bound!"
                else:
                    return ""
            elif col == 3:
                if theta_row['theta0'] < theta_row['lb'] or \
                        theta_row['theta0'] > theta_row['ub']:
                    return ("Initial estimate can't be lower than lb or "
                            "greater than ub!")
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

        theta_row = self.theta_data[row]

        if col == 1:
            theta_row['lb'] = float(value)
        elif col == 2:
            theta_row['ub'] = float(value)
        elif col == 3:
            theta_row['theta0'] = float(value)
        else:
            return False

        self.dataChanged.emit(index.sibling(row, 1), index.sibling(row, 2))
        return True

    def flags(self, index: QModelIndex):
        if index.column() != 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | ~Qt.ItemIsEditable


class VariableSelectionTableModel(QAbstractTableModel):
    def __init__(self, application_data: DataStorage, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)
        self.app_data = application_data
        self.headers = ['Select', 'Alias', 'Type']
        self.load_data()

        self.app_data.alias_data_changed.connect(self.load_data)
        self.app_data.expr_data_changed.connect(self.load_data)

    def load_data(self):
        self.layoutAboutToBeChanged.emit()

        # get candidates, constraints and objective function
        self.variables = self.app_data.metamodel_selected_data

        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return len(self.variables)

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

        var_data = self.variables[row]

        if role == Qt.DisplayRole:
            if col == 1:
                return str(var_data['Alias'])
            elif col == 2:
                return str(var_data['Type'])
            else:
                return None

        elif role == Qt.CheckStateRole:
            if col == 0:
                if var_data['Checked']:
                    return Qt.Checked
                else:
                    return Qt.Unchecked
            else:
                return None

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):
        if role != Qt.EditRole or not index.isValid():
            return False

        row = index.row()
        col = index.column()

        var_data = self.variables[row]

        if col == 0:
            var_data['Checked'] = True if value == 1 else False

            self.dataChanged.emit(index.sibling(row, col + 1),
                                  index.sibling(row, self.columnCount()))

            return True

        return False

    def flags(self, index: QModelIndex):
        row = index.row()
        col = index.column()

        var_data = self.variables[row]

        if col == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | \
                Qt.ItemIsEditable
        else:
            if var_data['Checked']:
                # enable row
                return Qt.ItemIsEnabled | Qt.ItemIsSelectable
            else:
                # disable row
                return ~Qt.ItemIsEnabled | Qt.ItemIsSelectable


class MetamodelTab(QWidget):
    def __init__(self, application_database: DataStorage, parent_tab=None):
        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Form()
        parent_tab = parent_tab if parent_tab is not None else self
        self.ui.setupUi(parent_tab)

        # ------------------------ Internal Variables -------------------------
        self.application_database = application_database

        # ----------------------- Widget Initialization -----------------------
        theta_table = self.ui.thetaTableView
        theta_model = ThetaTableModel(self.application_database,
                                      parent=theta_table)
        theta_table.setModel(theta_model)

        theta_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        sel_var_table = self.ui.outvariableTableView
        sel_var_model = VariableSelectionTableModel(self.application_database,
                                                    parent=sel_var_table)
        sel_var_table.setModel(sel_var_model)

        sel_var_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        # bounds and estimate double value delegate
        self._lb_delegate = DoubleEditorDelegate()
        self._ub_delegate = DoubleEditorDelegate()
        self._theta0_delegate = DoubleEditorDelegate()

        theta_table.setItemDelegateForColumn(1, self._lb_delegate)
        theta_table.setItemDelegateForColumn(2, self._ub_delegate)
        theta_table.setItemDelegateForColumn(3, self._theta0_delegate)

        # checkbox delegate for selected output variables
        self._check_delegate = CheckBoxDelegate()
        sel_var_table.setItemDelegateForColumn(0, self._check_delegate)
        # --------------------------- Signals/Slots ---------------------------
        # ---------------------------------------------------------------------


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook
    from tests_.mock_data import DOE_TAB_MOCK_DS

    app = QApplication(sys.argv)
    ds = DOE_TAB_MOCK_DS
    w = MetamodelTab(application_database=ds)
    w.show()

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
