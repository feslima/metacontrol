import pathlib

import pandas as pd
from PyQt5.QtCore import (QAbstractTableModel, QModelIndex, QObject,
                          QStringListModel, Qt, pyqtSignal)
from PyQt5.QtGui import QBrush, QFont, QPalette
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHeaderView,
                             QTableView, QWidget)

from gui.calls.base import (CheckBoxDelegate, ComboBoxDelegate,
                            DoubleEditorDelegate)
from gui.calls.dialogs.reducedcsveditor import ReducedCsvEditorDialog
from gui.calls.dialogs.reducedspacesamplingassistant import (
    RangeOfDisturbanceTableModel, SamplingAssistantDialog)
from gui.calls.tabs.doetab import DoeResultsModel, DoeResultsView
from gui.models.data_storage import DataStorage
from gui.views.py_files.reducedspacetab import Ui_Form


class ReducedSpaceDofTableModel(QAbstractTableModel):

    def __init__(self, app_data: DataStorage, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)
        self.app_data = app_data
        self.load_data()

        self.app_data.reduced_space_dof_changed.connect(self.load_data)

    def load_data(self):
        self.layoutAboutToBeChanged.emit()

        self.dof_info = self.app_data.reduced_space_dof

        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return self.dof_info.shape[0]

    def columnCount(self, parent=None):
        return self.dof_info.shape[1]

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self.dof_info.columns[section]

            elif role == Qt.FontRole:
                df_font = QFont()
                df_font.setBold(True)
                return df_font

            else:
                return None

        elif orientation == Qt.Vertical:
            return None

        else:
            return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        value = self.dof_info.iat[row, col]

        if role == Qt.DisplayRole:
            if self.dof_info.columns[col] == 'Alias':
                return str(value)
            else:
                return None

        elif role == Qt.CheckStateRole:
            if self.dof_info.column[col] == 'Checked':
                if value:
                    return Qt.Checked
                else:
                    return Qt.Unchecked
            else:
                return None

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        else:
            return None

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):
        if role != Qt.EditRole or not index.isValid():
            return False

        row = index.row()
        col = index.column()

        if self.dof_info.columns[col] == 'Checked':
            value = True if value == 1 else False

            # change corresponding data in app storage
            self.app_data.reduced_space_dof.iat[row, col] = value
            self.app_data.reduced_space_dof_changed.emit()

            # update the entire row
            self.dataChanged.emit(index.sibling(row, 0),
                                  index.sibling(row, self.columnCount()))

            return True

        else:
            return False

    def flags(self, index: QModelIndex):
        row = index.row()
        col = index.column()

        if self.dof_info.columns[col] == 'Checked':
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | \
                Qt.ItemIsUserCheckable

        else:
            return ~Qt.ItemIsEditable | Qt.ItemIsSelectable


class ActiveCandidatesTableModel(QAbstractTableModel):

    def __init__(self, app_data: DataStorage, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)
        self.app_data = app_data
        self.load_data()

        self.app_data.active_candidates_changed.connect(self.load_data)

    def load_data(self):
        self.layoutAboutToBeChanged.emit()

        self.act_info = self.app_data.active_candidates

        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return self.act_info.shape[0]

    def columnCount(self, parent=None):
        return self.act_info.shape[1]

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self.act_info.columns[section]

            elif role == Qt.FontRole:
                df_font = QFont()
                df_font.setBold(True)
                return df_font

            else:
                return None

        elif orientation == Qt.Vertical:
            return None

        else:
            return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        value = self.act_info.iat[row, col]

        if role == Qt.DisplayRole:
            if self.act_info.columns[col] == 'Alias':
                return str(value)
            else:
                return None

        elif role == Qt.CheckStateRole:
            if self.act_info.column[col] == 'Checked':
                if value:
                    return Qt.Checked
                else:
                    return Qt.Unchecked
            else:
                return None

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.BackgroundRole:
            # if the number of checked cvs is greater than the number of
            # unchecked DOFS, turn the cell red
            doe_df_info = self.app_data.reduced_space_dof
            if self.act_info['Checked'].sum() > ~doe_df_info['Checked'].sum():
                return QBrush(Qt.red)

            else:
                return QBrush(self.parent().palette().brush(QPalette.Base))

        else:
            return None

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):
        if role != Qt.EditRole or not index.isValid():
            return False

        row = index.row()
        col = index.column()

        if self.act_info.columns[col] == 'Checked':
            value = True if value == 1 else False

            # change corresponding data in app storage
            self.app_data.active_candidates.iat[row, col] = value
            self.app_data.active_candidates_changed.emit()

            # update the entire row
            self.dataChanged.emit(index.sibling(row, 0),
                                  index.sibling(row, self.columnCount()))

            return True

        else:
            return False

    def flags(self, index: QModelIndex):
        row = index.row()
        col = index.column()

        if self.act_info.columns[col] == 'Checked':
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | \
                Qt.ItemIsUserCheckable

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
        doe_data = self.app_data.reduced_doe_sampled_data.copy(deep=True)

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


class ReducedSpaceTab(QWidget):
    bkp_filepath_changed = pyqtSignal()

    def __init__(self, application_database: DataStorage, parent_tab=None):
        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Form()
        parent_tab = parent_tab if parent_tab is not None else self
        self.ui.setupUi(parent_tab)

        # ------------------------ Internal Variables -------------------------
        self.application_database = application_database
        # ----------------------- Widget Initialization -----------------------
        self.ui.openSamplingPushButton.setEnabled(False)
        dof_table = self.ui.reducedSpaceDofTableView
        dof_model = ReducedSpaceDofTableModel(self.application_database,
                                              parent=dof_table)
        dof_table.setModel(dof_model)

        dof_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        self._check_delegate = CheckBoxDelegate()

        dof_table.setItemDelegateForColumn(1, self._check_delegate)

        act_table = self.ui.activeCandidatesTableView
        act_model = ActiveCandidatesTableModel(self.application_database,
                                               parent=act_table)

        act_table.setModel(act_model)

        act_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        self._act_check_delegate = CheckBoxDelegate()

        act_table.setItemDelegateForColumn(1, self._act_check_delegate)

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

        self.ui.loadSimulationPushButton.clicked.connect(
            self.open_simulation_file_dialog)
        self.bkp_filepath_changed.connect(self.update_simfilepath_display)

        self.ui.openSamplingPushButton.clicked.connect(
            self.open_sampling_assistant
        )
        # ---------------------------------------------------------------------

    @property
    def bkp_filepath(self):
        """The bkp_filepath property."""
        return self._bkp_filepath

    @bkp_filepath.setter
    def bkp_filepath(self, value):
        self._bkp_filepath = value
        self.bkp_filepath_changed.emit()

    def open_simulation_file_dialog(self):
        """Prompts the user to select Aspen Plus simulation files.
        """
        homedir = pathlib.Path().home()
        sim_filename, sim_filetype = QFileDialog.getOpenFileName(
            self, "Select Aspen Plus simulation files.",
            str(homedir),
            "BKP files (*.bkp);; Input files (*.inp)"
        )

        self.bkp_filepath = sim_filename

    def update_simfilepath_display(self):
        """Grabs the simulation file path and displays it on the linedit widget
        """
        browser = self.ui.redspaceSimFileLineEdit
        sim_file_name = self.bkp_filepath
        sim_file_ext = pathlib.Path(sim_file_name).suffix

        if sim_file_name == "" or \
                (sim_file_ext != ".bkp" and sim_file_ext != ".inp"):
            # user canceled the file dialog or selected an invalid file
            if browser.styleSheet() != "color: blue":
                # if there isn't an invalid path in display already
                browser.setText("Invalid or no file selected.")
                browser.setStyleSheet("color: red")

                # deactivate the open sampling assistant
                self.ui.openSamplingPushButton.setEnabled(False)

        else:
            # it's a valid file. Set its path as string and color.
            browser.setText(sim_file_name)
            browser.setStyleSheet("")

            # enable the load simulation tree button
            self.ui.openSamplingPushButton.setEnabled(True)

    def open_sampling_assistant(self):
        dialog = SamplingAssistantDialog(
            self.application_database, self.bkp_filepath)
        dialog.exec_()

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
