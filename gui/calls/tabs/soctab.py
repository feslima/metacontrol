import numpy as np
import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtGui import QBrush, QFont, QPalette
from PyQt5.QtWidgets import QApplication, QHeaderView, QTableView, QWidget
from scipy.special import comb

from gui.calls.base import DoubleEditorDelegate, IntegerEditorDelegate
from gui.models.data_storage import DataStorage
from gui.views.py_files.soctab import Ui_Form


class MagnitudeTableModel(QAbstractTableModel):
    def __init__(self, app_data: DataStorage, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)
        self.app_data = app_data
        self.mag = pd.DataFrame()

    def load_data(self, mag_type: str):
        self.layoutAboutToBeChanged.emit()

        if mag_type == 'disturbance':
            self.mag = pd.DataFrame.from_dict(
                self.app_data.soc_disturbance_magnitude)
        elif mag_type == 'error':
            self.mag = pd.DataFrame.from_dict(
                self.app_data.soc_measure_error_magnitude)
        else:
            raise ValueError("Invalid mag_type.")

        self.layoutChanged.emit()

    def rowCount(self, parent):
        return self.mag.shape[0] if not self.mag.empty else 0

    def columnCount(self, parent):
        return self.mag.shape[1] if not self.mag.empty else 0

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if self.mag.empty:
            return None

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.mag.columns[section]
            elif orientation == Qt.Vertical:
                return self.mag.index[section]
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
        if not index.isValid() or self.mag.empty:
            return None

        row = index.row()
        col = index.column()

        mag_data = self.mag.iat[row, col]

        if role == Qt.DisplayRole:
            if mag_data is None:
                return "Type Value"
            elif np.isnan(mag_data):
                return "Type Value"
            else:
                return str(mag_data)

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.BackgroundRole:
            if mag_data is None:
                return QBrush(Qt.red)
            elif np.isnan(mag_data):
                return QBrush(Qt.red)
            else:
                par = self.parent()
                return QBrush(par.palette().brush(QPalette.Base))
        else:
            return None

    def flags(self, index: QModelIndex):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable


class DistMagTableModel(MagnitudeTableModel):
    def __init__(self, app_data: DataStorage, parent: QTableView):
        super().__init__(app_data, parent)
        self.app_data.soc_dist_mag_data_changed.connect(self.load_data)

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):
        if role != Qt.EditRole or not index.isValid() or self.mag.empty:
            return False

        row = index.row()
        col = index.column()

        soc_d = self.app_data.soc_disturbance_magnitude
        soc_d['Value'][self.mag.index[row]] = float(value)
        self.app_data.soc_dist_mag_data_changed.emit('disturbance')

        self.dataChanged.emit(index, index)
        return True


class MeasErrMagTableModel(MagnitudeTableModel):
    def __init__(self, app_data: DataStorage, parent: QTableView):
        super().__init__(app_data, parent)
        self.app_data.soc_meas_mag_data_changed.connect(self.load_data)

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):
        if role != Qt.EditRole or not index.isValid() or self.mag.empty:
            return False

        row = index.row()
        col = index.column()

        soc_me = self.app_data.soc_measure_error_magnitude
        soc_me['Value'][self.mag.index[row]] = float(value)
        self.app_data.soc_meas_mag_data_changed.emit('error')

        self.dataChanged.emit(index, index)
        return True


class SubsetSizeTableModel(QAbstractTableModel):
    def __init__(self, app_data: DataStorage, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)
        self.app_data = app_data
        self.load_data()
        self.app_data.soc_subset_data_changed.connect(self.load_data)

    def load_data(self):
        self.layoutAboutToBeChanged.emit()

        self.ss_list = pd.DataFrame(self.app_data.soc_subset_size_list)

        self.layoutChanged.emit()

    def rowCount(self, parent):
        return self.ss_list.shape[0] if not self.ss_list.empty else 0

    def columnCount(self, parent):
        return self.ss_list.shape[1] if not self.ss_list.empty else 0

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: Qt.DisplayRole):
        if self.ss_list.empty:
            return None

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return "Size " + str(self.ss_list.columns[section])
            elif orientation == Qt.Vertical:
                return self.ss_list.index[section]
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
        if not index.isValid() or self.ss_list.empty:
            return None

        row = index.row()
        col = index.column()

        ss_data = self.ss_list.iat[row, col]

        if role == Qt.DisplayRole:
            return str(ss_data)

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.BackgroundRole or role == Qt.ToolTipRole:
            # maximum number of combinations allowed
            max_comb = comb(N=self.ss_list.columns[-1],
                            k=self.ss_list.columns[col], exact=True)
            if ss_data > max_comb:
                return QBrush(Qt.red) if role == Qt.BackgroundRole \
                    else "For this subset size, only a maximum of " + \
                    str(max_comb) + " best subsets is allowed!"
            else:
                par = self.parent()
                return QBrush(par.palette().brush(QPalette.Base))

        else:
            return None

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):
        if role != Qt.EditRole or not index.isValid():
            return False

        row = index.row()
        col = index.column()

        ss_list = self.app_data.soc_subset_size_list
        ss_list[str(col + 1)]['Subset number'] = int(value)
        self.app_data.soc_subset_data_changed.emit()

        self.dataChanged.emit(index, index)
        return True

    def flags(self, index: QModelIndex):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable


class SocTab(QWidget):
    def __init__(self, application_database: DataStorage, parent_tab=None):
        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Form()
        parent_tab = parent_tab if parent_tab is not None else self
        self.ui.setupUi(parent_tab)
        # ------------------------ Internal Variables -------------------------
        self.application_database = application_database
        # ----------------------- Widget Initialization -----------------------
        dist_table = self.ui.disturbanceMagTableView
        dist_model = DistMagTableModel(self.application_database,
                                       parent=dist_table)
        dist_model.load_data(mag_type='disturbance')  # trigger initial load
        dist_table.setModel(dist_model)

        self._dist_mag_delegate = DoubleEditorDelegate()
        dist_table.setItemDelegateForColumn(0, self._dist_mag_delegate)

        dist_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        meas_table = self.ui.measurementErrTableView
        meas_model = MeasErrMagTableModel(self.application_database,
                                          parent=meas_table)
        meas_model.load_data(mag_type='error')
        meas_table.setModel(meas_model)

        self._meas_mag_delegate = DoubleEditorDelegate()
        meas_table.setItemDelegateForColumn(0, self._meas_mag_delegate)
        meas_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        ss_table = self.ui.subsetSizingTableView
        ss_model = SubsetSizeTableModel(self.application_database,
                                        parent=ss_table)
        ss_table.setModel(ss_model)

        self._ss_size_delegate = IntegerEditorDelegate()
        ss_table.setItemDelegateForRow(0, self._ss_size_delegate)
        ss_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # --------------------------- Signals/Slots ---------------------------
        # ---------------------------------------------------------------------


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook
    from tests_.mock_data import HESSIAN_TAB_MOCK_DS

    app = QApplication(sys.argv)
    ds = HESSIAN_TAB_MOCK_DS
    w = SocTab(application_database=ds)

    w.show()

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
