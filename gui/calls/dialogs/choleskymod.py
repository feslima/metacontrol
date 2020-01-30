import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QHeaderView, QTableView, QDialog

from gui.views.py_files.choleskydialog import Ui_Dialog
from gui.models.data_storage import DataStorage
from gui.models.choleskymod import cholmod


class HessianMatrixTableModel(QAbstractTableModel):
    def __init__(self, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)

        self.matrix = pd.DataFrame()

    def update_matrix(self, matrix: pd.DataFrame):
        self.layoutAboutToBeChanged.emit()

        self.matrix = matrix

        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return self.matrix.shape[0] if not self.matrix.empty else 0

    def columnCount(self, parent=None):
        return self.matrix.shape[1] if not self.matrix.empty else 0

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):

        if self.matrix.empty:
            return None

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.matrix.columns[section]
            else:
                return self.matrix.index[section]

        elif role == Qt.FontRole:
            df_font = QFont()
            df_font.setBold(True)
            return df_font

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        else:
            return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or self.matrix.empty:
            return None

        row = index.row()
        col = index.column()

        value = self.matrix.iat[row, col]

        if role == Qt.DisplayRole:
            return str(value)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        else:
            return None


class ErrorTableModel(QAbstractTableModel):
    def __init__(self, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)

        self.error = pd.Series()

    def update_error(self, value: pd.Series):
        self.layoutAboutToBeChanged.emit()

        self.error = value

        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return self.error.size

    def columnCount(self, parent=None):
        return 1

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):

        if self.error.size == 0:
            return None

        if role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return self.error.index[section]
            else:
                return None

        elif role == Qt.FontRole:
            df_font = QFont()
            df_font.setBold(True)
            return df_font

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        else:
            return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or self.error.size == 0:
            return None

        row = index.row()
        col = index.column()

        value = self.error.iat[row]

        if role == Qt.DisplayRole:
            return str(value)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        else:
            return None


class CholeskyDialog(QDialog):
    def __init__(self, application_database: DataStorage):
        # ------------------------ Internal Variables -------------------------
        self.app_data = application_database
        self.juu = pd.DataFrame.from_dict(self.app_data.differential_juu)

        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowFlags(Qt.Window)
        # ----------------------- Widget Initialization -----------------------
        juu_table = self.ui.originalMatrixTableView
        juu_model = HessianMatrixTableModel(juu_table)
        juu_table.setModel(juu_model)

        juu_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        juu_model.update_matrix(self.juu)

        mod_juu_table = self.ui.modifiedMatrixTableView
        mod_juu_model = HessianMatrixTableModel(mod_juu_table)
        mod_juu_table.setModel(mod_juu_model)

        mod_juu_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        error_table = self.ui.errorMatrixTableView
        error_model = ErrorTableModel(error_table)
        error_table.setModel(error_model)

        error_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        self.apply_cholmod()
        # --------------------------- Signals/Slots ---------------------------
        self.ui.setPushButton.clicked.connect(self.set_modified_as_original)

    def apply_cholmod(self):
        mod_juu, _, indef, e = cholmod(self.juu.values)

        mod_juu_df = pd.DataFrame(mod_juu, columns=self.juu.columns,
                                  index=self.juu.index)
        self.ui.modifiedMatrixTableView.model().update_matrix(mod_juu_df)

        error_df = pd.Series(e, index=self.juu.index)
        self.ui.errorMatrixTableView.model().update_error(error_df)

        if indef:
            self.ui.modifyLabel.setText("The original Juu is not sufficiently "
                                        "positive definite."
                                        "The matrix was modified.")

            self.mod_juu = mod_juu_df.copy(deep=True)

        else:
            self.ui.modifyLabel.setText("The original Juu is already "
                                        "sufficiently positive definite. "
                                        "No modifications are necessary.")
            self.ui.setPushButton.setText("OK")

            self.mod_juu = self.juu.copy(deep=True)

        return

    def set_modified_as_original(self):
        self.app_data.differential_juu = self.mod_juu.to_dict(orient='dict')
        self.close()


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook
    from tests_.mock_data import indirect_mock

    app = QApplication(sys.argv)
    ds = indirect_mock()
    w = CholeskyDialog(application_database=ds)

    w.show()

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
