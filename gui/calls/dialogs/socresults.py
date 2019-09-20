import numpy as np
import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog, QHeaderView,
                             QTableView)
from pysoc.bnb import pb3wc
from pysoc.soc import helm

from gui.models.data_storage import DataStorage
from gui.views.py_files.socresults import Ui_Dialog


class LossTableModel(QAbstractTableModel):
    def __init__(self, dataframe: pd.DataFrame, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)

        self.df = dataframe.copy()

    def set_dataframe(self, dataframe: pd.DataFrame):
        self.layoutAboutToBeChanged.emit()
        self.df = dataframe.copy()
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return self.df.shape[0] if not self.df.empty else 0

    def columnCount(self, parent=None):
        return self.df.shape[1] if not self.df.empty else 0

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if self.df.empty:
            return None

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.df.columns[section]
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
        if not index.isValid() or self.df.empty:
            return None

        row = index.row()
        col = index.column()

        value = self.df.iat[row, col]

        if role == Qt.DisplayRole:
            return str(value)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        else:
            return None

    def sort(self, column: int, order=Qt.AscendingOrder):
        col_name = self.df.columns[column]

        self.layoutAboutToBeChanged.emit()
        self.df.sort_values(by=col_name, ascending=order == Qt.AscendingOrder,
                            inplace=True)
        self.df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()


class HTableModel(QAbstractTableModel):
    def __init__(self, dataframe: pd.DataFrame, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)

        self.df = dataframe.copy()

    def set_dataframe(self, dataframe: pd.DataFrame):
        self.layoutAboutToBeChanged.emit()
        self.df = dataframe.copy()
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return self.df.shape[0] if not self.df.empty else 0

    def columnCount(self, parent=None):
        return self.df.shape[1] if not self.df.empty else 0

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if self.df.empty:
            return None

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.df.columns[section]
            else:
                return self.df.index[section]

        elif role == Qt.FontRole:
            df_font = QFont()
            df_font.setBold(True)
            return df_font

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        else:
            return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or self.df.empty:
            return None

        row = index.row()
        col = index.column()

        value = self.df.iat[row, col]

        if role == Qt.DisplayRole:
            # NaN cells show as empty
            return str(value) if not np.isnan(value) else "∅"
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        elif role == Qt.FontRole:
            df_font = QFont()
            if np.isnan(value):
                df_font.setPointSize(16)

            return df_font
        else:
            return None


class SensitivityTableModel(QAbstractTableModel):
    def __init__(self, dataframe: pd.DataFrame, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)

        self.df = dataframe.copy()

    def set_dataframe(self, dataframe: pd.DataFrame):
        self.layoutAboutToBeChanged.emit()
        self.df = dataframe.copy()
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return self.df.shape[0] if not self.df.empty else 0

    def columnCount(self, parent=None):
        return self.df.shape[1] if not self.df.empty else 0

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if self.df.empty:
            return None

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.df.columns[section]
            else:
                return self.df.index[section]

        elif role == Qt.FontRole:
            df_font = QFont()
            df_font.setBold(True)
            return df_font

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        else:
            return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or self.df.empty:
            return None

        row = index.row()
        col = index.column()

        value = self.df.iat[row, col]

        if role == Qt.DisplayRole:
            # NaN cells show as empty
            return str(value) if not np.isnan(value) else "∅"
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        elif role == Qt.FontRole:
            df_font = QFont()
            if np.isnan(value):
                df_font.setPointSize(16)

            return df_font
        else:
            return None


class SocResultsDialog(QDialog):
    def __init__(self, application_data: DataStorage):
        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Window)
        self.setWindowState(Qt.WindowMaximized)
        # ------------------------ Internal Variables -------------------------
        self.app_data = application_data

        Gy = pd.DataFrame(self.app_data.differential_gy)
        Gyd = pd.DataFrame(self.app_data.differential_gyd)
        Juu = pd.DataFrame(self.app_data.differential_juu)
        Jud = pd.DataFrame(self.app_data.differential_jud)
        md = pd.DataFrame(self.app_data.soc_disturbance_magnitude)
        me = pd.DataFrame(self.app_data.soc_measure_error_magnitude)
        ss_list = self.app_data.soc_subset_size_list

        # ensure correct indexation
        # index of Gyd has to be the same order as index of Gy
        Gyd = Gyd.reindex(index=Gy.index)
        # index of md has to be the same order as columns of Gyd
        md = md.reindex(index=Gyd.columns)
        # index of me has to be the same order as index of Gy
        me = me.reindex(index=Gy.index)
        # index/columns of Juu has to be the same order as columns of Gy
        Juu = Juu.reindex(index=Gy.columns, columns=Gy.columns)
        # index of Jud has to be the same order as columns of Gy and
        # columns of Jud has to be the same order as columns of Gyd
        Jud = Jud.reindex(index=Gy.columns, columns=Gyd.columns)

        # keys are the subset sizes
        soc_results = {}

        for ss in ss_list:
            n = int(ss)
            nc = int(ss_list[ss]['Subset number'])

            res = helm(Gy=Gy.to_numpy(), Gyd=Gyd.to_numpy(),
                       Juu=Juu.to_numpy(), Jud=Jud.to_numpy(),
                       md=md.to_numpy().flatten(),
                       me=me.to_numpy().flatten(),
                       ss_size=n, nc_user=nc)

            # prepare the frames to be displayed
            worst_loss_list, average_loss_list, sset_bnb, cond_list, \
                H_list, Gy_list, Gyd_list, F_list = res

            # losses dataframe
            loss_df = pd.DataFrame(np.nan, index=range(nc),
                                   columns=['Structure', 'Worst-case loss',
                                            'Average loss',
                                            'Gy conditional number'],
                                   dtype=object)

            soc_results[ss] = {'loss': loss_df}

            for i in range(nc):
                # build the structure string
                st = ""
                ss_row = sset_bnb[i, :]
                for j in ss_row:
                    if j != ss_row[-1]:
                        st += Gy.index[j - 1] + " | "
                    else:
                        st += Gy.index[j - 1]

                # assign structure
                loss_df.at[i, 'Structure'] = st

                loss_df.at[i, 'Worst-case loss'] = worst_loss_list[i]
                loss_df.at[i, 'Average loss'] = average_loss_list[i]
                loss_df.at[i, 'Gy conditional number'] = cond_list[i]

            soc_results[ss]['h'] = {}
            soc_results[ss]['f'] = {}
            for i in range(nc):
                ss_row = sset_bnb[i, :]

                # H dataframe
                h_df = pd.DataFrame(None, index=Juu.index,
                                    columns=Gy.index)

                # sensitivity matrices
                F = pd.DataFrame(F_list[i], index=Gy.index[ss_row - 1],
                                 columns=Gyd.columns)
                soc_results[ss]['f']["Set " + str(i + 1)] = F
                # populate H matrix
                for col, j in enumerate(ss_row):
                    h_df.loc[:, Gy.index[j - 1]] = H_list[i][0, col]
                soc_results[ss]['h'][loss_df.at[i, 'Structure']] = h_df

        self.soc_results = soc_results

        # ----------------------- Widget Initialization -----------------------
        ss_combo = self.ui.subsetSizeComboBox
        ss_combo.addItems(['Select size'] + list(soc_results.keys()))

        setstruct_combo = self.ui.selectHComboBox
        setstruct_combo.addItem('Select structure')
        setstruct_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        setnum_combo = self.ui.setNumberComboBox
        setnum_combo.addItem('Select number')

        loss_table = self.ui.lossesTableView
        loss_model = LossTableModel(pd.DataFrame({}), parent=loss_table)
        loss_table.setModel(loss_model)

        loss_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        h_table = self.ui.hMatrixTableView
        h_model = HTableModel(pd.DataFrame({}), parent=h_table)
        h_table.setModel(h_model)

        h_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        h_table.resizeRowsToContents()

        f_table = self.ui.sensitivityTableView
        f_model = SensitivityTableModel(pd.DataFrame({}), parent=f_table)
        f_table.setModel(f_model)

        f_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # --------------------------- Signals/Slots ---------------------------
        ss_combo.currentTextChanged[str].connect(self.on_subset_size_changed)

        setstruct_combo.currentTextChanged[str].connect(
            self.on_combo_set_structure_changed)

        setnum_combo.currentTextChanged[str].connect(
            self.on_combo_set_number_changed)

        self.ui.closeDialogPushButton.clicked.connect(self.close)
        # ---------------------------------------------------------------------

    def on_subset_size_changed(self, ss_size: str):
        # loads the loss and h table models based on subset size selected in
        # combobox

        if ss_size != 'Select size':
            loss_values = self.soc_results[ss_size]['loss']
            # h_values = self.soc_results[ss_size]['h']
            h_items = ['Select structure'] + \
                list(self.soc_results[ss_size]['h'].keys())
            f_items = ['Select number'] + \
                list(self.soc_results[ss_size]['f'].keys())
        else:
            loss_values = pd.DataFrame({})
            # h_values = pd.DataFrame({})
            h_items = []
            f_items = []

        loss_model = self.ui.lossesTableView.model()
        loss_model.set_dataframe(loss_values)

        # h matrices
        setstruct_combo = self.ui.selectHComboBox
        setstruct_combo.clear()
        setstruct_combo.addItems(h_items)
        setstruct_combo.setCurrentIndex(0)

        # sensitivity matrices
        setnum_combo = self.ui.setNumberComboBox
        setnum_combo.clear()  # remove all items
        setnum_combo.addItems(f_items)
        setnum_combo.setCurrentIndex(0)

    def on_combo_set_structure_changed(self, set_structure: str):
        ss_size = self.ui.subsetSizeComboBox.currentText()

        if set_structure == "Select structure" or set_structure == "":
            h_values = pd.DataFrame({})
        else:
            h_values = self.soc_results[ss_size]['h'][set_structure]

        h_model = self.ui.hMatrixTableView.model()
        h_model.set_dataframe(h_values)

    def on_combo_set_number_changed(self, set_number: str):
        ss_size = self.ui.subsetSizeComboBox.currentText()

        if set_number == "Select number" or set_number == "":
            f_values = pd.DataFrame({})
        else:
            f_values = self.soc_results[ss_size]['f'][set_number]

        f_model = self.ui.sensitivityTableView.model()
        f_model.set_dataframe(f_values)


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook
    from tests_.mock_data import SOC_TAB_MOC_DS

    app = QApplication(sys.argv)
    ds = SOC_TAB_MOC_DS
    w = SocResultsDialog(application_data=ds)
    w.show()

    sys.excepthook = my_exception_hook

    sys.exit(app.exec_())
