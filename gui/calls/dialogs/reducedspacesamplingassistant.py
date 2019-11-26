import pathlib

import numpy as np
import pandas as pd
from PyQt5.QtCore import (QAbstractTableModel, QModelIndex, QSize, Qt,
                          pyqtSignal)
from PyQt5.QtGui import QBrush, QFont, QPalette, QResizeEvent
from PyQt5.QtWidgets import (
    QAbstractItemView, QApplication, QDialog, QFileDialog, QHeaderView,
    QMessageBox, QStatusBar, QTableView)

from gui.calls.base import DoubleEditorDelegate, my_exception_hook
from gui.calls.dialogs.reducedlhssettings import LhsSettingDialog
from gui.models.data_storage import DataStorage
from gui.models.sampling import ReducedSamplerThread, lhs
from gui.views.py_files.samplingassistant import Ui_Dialog


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


class SampledDataView(QTableView):
    def setModel(self, model: QAbstractTableModel):
        super().setModel(model)
        for row in range(model.rowCount()):
            for col in range(model.columnCount()):
                span = model.span(model.index(row, col))
                if span.height() > 1 or span.width() > 1:
                    self.setSpan(row, col, span.height(), span.width())


class SampledDataTableModel(QAbstractTableModel):

    input_design_changed = pyqtSignal(bool)

    # CONSTANTS
    _INPUT_COL_OFFSET = 2
    _HEADER_ROW_OFFSET = 2

    def __init__(self, application_data: DataStorage, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)
        self.app_data = application_data
        self.load_data()

    @property
    def input_design(self):
        """The input_design property."""
        if not hasattr(self, '_input_design'):
            # create empty input design and sample data dataframe on init
            self._input_design = pd.DataFrame({})

        self.is_input_design_generated = False

        return self._input_design

    @input_design.setter
    def input_design(self, value: pd.DataFrame):
        if not value.equals(self.input_design):
            # if dataframe is diferent from the current one in display, warn
            # the about layout changes, and reset case number and status cols
            self.layoutAboutToBeChanged.emit()

            self._input_design = value
            self.dataChanged.emit(self.index(0, 0),
                                  self.index(self.rowCount(),
                                             self.columnCount()))
            self.is_input_design_generated = False \
                if value.isnull().all(axis=None) else True
            self.input_design_changed.emit(self.is_input_design_generated)

            self.layoutChanged.emit()

            # number of experiments
            n_samp = self.app_data.reduced_doe_lhs_settings['n_samples']
            if self.app_data.reduced_doe_lhs_settings['inc_vertices']:
                n_samp += 2 ** len(self._input_alias)  # include vertices

            # create empty dataframes with NaN values
            self._case_num = pd.DataFrame({'case': np.arange(1, n_samp + 1)})
            self._status_sim = pd.DataFrame({'status': [''] * n_samp},
                                            dtype=object)

            # reset sampled data as well
            self.samp_data = pd.DataFrame(np.nan, index=range(n_samp),
                                          columns=self._output_alias,
                                          dtype=float)

    @property
    def samp_data(self):
        """The samp_data property."""
        if not hasattr(self, '_samp_data'):
            # create empty sample data dataframe on init
            self._samp_data = pd.DataFrame({})

        return self._samp_data

    @samp_data.setter
    def samp_data(self, value: pd.DataFrame):
        if not value.equals(self._samp_data):
            self._samp_data = value
            self.dataChanged.emit(self.index(0, 0),
                                  self.index(self.rowCount(),
                                             self.columnCount()))

    def load_data(self):
        # load internal headers names
        inp_data = self.app_data.input_table_data
        out_data = self.app_data.output_table_data
        self._input_alias = self.app_data.reduced_doe_d_bounds.loc[
            :, 'name'
        ].tolist()

        output_mvs = inp_data.loc[~inp_data['Alias'].isin(self._input_alias), 'Alias']

        self._output_alias = pd.concat([out_data.loc[:, 'Alias'],
                   output_mvs], ignore_index=True,
                  axis='index', sort=False).tolist()

        # self._output_alias = out_data.loc[:, 'Alias'].tolist()

        # number of experiments
        n_samp = self.app_data.reduced_doe_lhs_settings['n_samples']
        self.input_design = pd.DataFrame(np.nan, index=range(n_samp),
                                         columns=self._input_alias,
                                         dtype=float)

    def get_doe_data(self) -> pd.DataFrame:
        """Returns the sampled DOE data as a pandas DataFrame
        """
        if self.samp_data.isnull().all(axis=None):
            # if no sampling is done, return empty dataframe
            return pd.DataFrame({})
        else:
            df = self._case_num.merge(self._status_sim, left_index=True,
                                      right_index=True)
            df = df.merge(self.input_design, left_index=True, right_index=True)
            df = df.merge(self.samp_data, left_index=True, right_index=True)

            return df

    def generate_lhs(self):
        """Generate LHS matrix and make it available to the GUI.
        """
        reply = QMessageBox.No
        if self.is_input_design_generated:
            # there is data already in display in the table, warn the user
            msg_str = ("By clicking yes ALL data, including input and "
                       "output already sampled will be deleted! Proceed at "
                       "your own risk.")
            reply = QMessageBox().question(self.parent(),
                                           "Renew input design?",
                                           msg_str, QMessageBox.Yes,
                                           QMessageBox.No)

        if reply == QMessageBox.Yes or not self.is_input_design_generated:
            mv_bnds = self.app_data.reduced_doe_d_bounds
            lhs_settings = self.app_data.reduced_doe_lhs_settings

            names_list = mv_bnds['name'].tolist()
            lb_list = mv_bnds['lb'].tolist()
            ub_list = mv_bnds['ub'].tolist()

            lhs_table = lhs(lhs_settings['n_samples'], lb_list, ub_list,
                            lhs_settings['n_iter'],
                            lhs_settings['inc_vertices'])

            self.input_design = pd.DataFrame(lhs_table, columns=names_list)

    def on_case_sampled(self, case_num: int, sampled_values: dict):
        """Slot that performs the simulation and displays data in the table.

        Parameters
        ----------
        case_num : int
            Case number.
        sampled_values : dict
            Dictionary containing the sampled data
        """
        # place the convergence flag and case number
        self._status_sim.iat[case_num - 1, 0] = sampled_values['success']
        self._case_num.iat[case_num - 1, 0] = case_num

        # delete the success key
        del sampled_values['success']

        # set output values
        self.samp_data.iloc[case_num - 1] = sampled_values

        # emit data changed signal
        self.dataChanged.emit(
            self.index(case_num - 1 + self._HEADER_ROW_OFFSET, 0),
            self.index(case_num - 1 + self._HEADER_ROW_OFFSET,
                       self.columnCount()))

    def on_sampling_done(self):
        """Stores the sampled data in the application storage.
        """
        self.app_data.reduced_doe_sampled_data = self.get_doe_data()

    def rowCount(self, parent=None):
        return self._HEADER_ROW_OFFSET + self.input_design.shape[0]

    def columnCount(self, parent=None):
        return self._INPUT_COL_OFFSET + self.input_design.shape[1] + \
            self.samp_data.shape[1]

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        df_rows, inp_cols = self.input_design.shape
        _, samp_cols = self.samp_data.shape
        rowoffset = self._HEADER_ROW_OFFSET
        coloffset = self._INPUT_COL_OFFSET

        if role == Qt.DisplayRole:
            if rowoffset - 1 < row < df_rows + rowoffset:
                if coloffset - 1 < col < inp_cols + coloffset:
                    # numeric data display of input design
                    val = self.input_design.iat[row - rowoffset,
                                                col - coloffset]
                    return "{0:.7f}".format(val) if not np.isnan(val) else None

                elif inp_cols + coloffset - 1 < col < inp_cols + samp_cols + \
                        coloffset:
                    # numeric data display of sampled data
                    val = self.samp_data.iat[row - rowoffset,
                                             col - (inp_cols + coloffset)]
                    return "{0:.7f}".format(val) if not np.isnan(val) else None

                elif col == 0:
                    # case number
                    return str(int(self._case_num.iat[row - rowoffset, 0]))

                elif col == 1:
                    # status
                    status = self._status_sim.iat[row - rowoffset, 0]
                    return str(status)

                else:
                    return None

            elif row == 0:
                # first row headers
                if col == 0:
                    return "Case Number"
                elif col == 1:
                    return "Status"
                elif col == coloffset:
                    return "Inputs"
                elif col == coloffset + len(self._input_alias):
                    return "Outputs"
                else:
                    return None

            elif row == 1:
                # second row headers
                if coloffset - 1 < col < inp_cols + coloffset:
                    return str(self.input_design.columns[col - coloffset])
                elif inp_cols + coloffset - 1 < col < inp_cols + samp_cols + \
                        coloffset:
                    return str(self.samp_data.columns[col -
                                                      inp_cols - coloffset])
                else:
                    return None

        elif role == Qt.FontRole:
            if row == 0 or row == 1:
                df_font = QFont()
                df_font.setBold(True)
                return df_font
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        else:
            return None

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
                # inputs
                return QSize(len(self._input_alias), 1)
            elif col == coloffset + len(self._input_alias):
                # outputs
                return QSize(len(self._output_alias), 1)

            else:
                return super().span(index)
        else:
            return super().span(index)


class SamplingAssistantDialog(QDialog):

    def __init__(self, application_database: DataStorage, bkp_filepath: str):
        # ------------------------ Internal Variables -------------------------
        self.app_data = application_database
        self.bkp_filepath = bkp_filepath

        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowFlags(Qt.Window)
        # ----------------------- Widget Initialization -----------------------
        var_table = self.ui.tableViewInputVariables
        var_model = RangeOfDisturbanceTableModel(self.app_data,
                                                 parent=var_table)
        var_table.setModel(var_model)

        var_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # bounds double value delegate
        self._lb_delegate = DoubleEditorDelegate()
        self._ub_delegate = DoubleEditorDelegate()

        var_table.setItemDelegateForColumn(1, self._lb_delegate)
        var_table.setItemDelegateForColumn(2, self._ub_delegate)

        results_table = SampledDataView(parent=self.ui.groupBox_3)
        results_model = SampledDataTableModel(self.app_data,
                                              parent=results_table)
        results_table.setModel(results_model)

        results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.gridLayout_4.removeWidget(self.ui.displayProgressBar)
        self.ui.gridLayout_4.addWidget(results_table, 1, 0, 1, 1)
        self.ui.gridLayout_4.addWidget(self.ui.displayProgressBar, 2, 0, 1, 1)
        results_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        results_table.verticalHeader().hide()

        self.results_table = results_table

        # status bar
        self.statBar = QStatusBar(self)
        self.ui.horizontalLayout.addWidget(self.statBar)

        # --------------------------- Signals/Slots ---------------------------
        # generate lhs and lhs settings
        self.ui.genLhsPushButton.clicked.connect(results_model.generate_lhs)
        self.ui.lhsSettingsPushButton.clicked.connect(self.open_lhs_settings)

        # enables/disable sampling button and updates progress bar
        results_model.input_design_changed.connect(self.enable_sampling_button)
        results_model.input_design_changed.connect(
            self.on_input_design_changed)

        # starts sampling when pressing sample data button
        self.ui.sampDataPushButton.clicked.connect(self.sample_data)

        # aborts sampling when pressing button
        self.ui.abortSamplingPushButton.clicked.connect(
            self.abort_sampling_thread)

        # closes the dialog when cancel buttons is pressed
        self.ui.cancelPushButton.clicked.connect(self.close)

        # closes dialog when user is done sampling
        self.ui.donePushButton.clicked.connect(self.on_sampling_done)

        # exports data in display to csv when pressing button
        self.ui.exportCsvPushButton.clicked.connect(self.export_csv)

        self.app_data.reduced_d_bounds_changed.connect(
            self.on_reduced_d_bounds_changed
        )
        # ---------------------------------------------------------------------

    # -------------------------------------------------------------------------
    def on_reduced_d_bounds_changed(self):
        # check if the bounds are properly set. If so, enable the radio buttons
        bnd_df = self.app_data.reduced_doe_d_bounds

        if bnd_df['lb'].ge(bnd_df['ub']).any() or \
                bnd_df['nominal'].lt(bnd_df['lb']).any() or \
            bnd_df['nominal'].gt(bnd_df['ub']).any():
            self.ui.genLhsPushButton.setEnabled(False)
            self.ui.lhsSettingsPushButton.setEnabled(False)
        else:
            self.ui.genLhsPushButton.setEnabled(True)
            self.ui.lhsSettingsPushButton.setEnabled(True)

    def on_sampling_done(self):
        """Stores the sampling in the application storage and closes the dialog
        """
        model = self.results_table.model()
        model.on_sampling_done()
        self.close()

    def open_lhs_settings(self):
        """Opens the dialog to configure the LHS parameters.
        """
        dialog = LhsSettingDialog(self.app_data)
        dialog.exec_()

    def enable_sampling_button(self, is_enabled: bool):
        """Enables or disable sampling button based on input_design values.
        """
        if is_enabled:
            self.ui.sampDataPushButton.setEnabled(True)
        else:
            self.ui.sampDataPushButton.setEnabled(False)

    def on_input_design_changed(self, is_enabled: bool):
        """Update the progress bar maximum value.
        """
        model = self.results_table.model()
        inp_design = model.input_design
        self.ui.displayProgressBar.setValue(0)
        self.ui.displayProgressBar.setMaximum(inp_design.shape[0])

    def sample_data(self):
        """View changes when the users starts the sampling.
        """
        # disable the generate lhs, sample and export buttons
        self.ui.genLhsPushButton.setEnabled(False)
        self.ui.sampDataPushButton.setEnabled(False)
        self.ui.exportCsvPushButton.setEnabled(False)
        self.ui.donePushButton.setEnabled(False)
        self.ui.cancelPushButton.setEnabled(False)

        # enable the abort button
        self.ui.abortSamplingPushButton.setEnabled(True)

        # change the status bar text
        self.statBar.showMessage("Opening the simulation engine...")

        # reset progress bar value
        self.ui.displayProgressBar.setValue(0)

        # start sampling
        model = self.results_table.model()
        inp_design = model.input_design

        self.sampler = ReducedSamplerThread(inp_design, self.app_data,
                                            self.bkp_filepath)
        self.sampler.case_sampled.connect(self.on_case_sampled)
        self.sampler.started.connect(self.statBar.clearMessage)
        self.sampler.finished.connect(self.on_sampling_finished)
        self.sampler.start()

    def on_case_sampled(self, row: int, sampled_values: dict):
        """Slot that updates the progress bar values.

        Parameters
        ----------
        row : int
            Row number.
        sampled_values : dict
            Dictionary containing the sampled data
        """
        model = self.results_table.model()
        model.on_case_sampled(row, sampled_values)
        self.ui.displayProgressBar.setValue(row)

    def on_sampling_finished(self):
        """View changes when the sampling is finished.
        """
        # enable gen lhs, sample and export buttons
        self.ui.genLhsPushButton.setEnabled(True)
        self.ui.sampDataPushButton.setEnabled(True)
        self.ui.exportCsvPushButton.setEnabled(True)
        self.ui.donePushButton.setEnabled(True)
        self.ui.cancelPushButton.setEnabled(True)

        # disable the abort button and sample data
        self.ui.abortSamplingPushButton.setEnabled(False)

    def abort_sampling_thread(self):
        """Aborts the sampling procedure.
        """
        self.sampler.requestInterruption()

    def export_csv(self):
        """Exports current data in display into a .csv file
        """
        dialog_title = "Select where to save the .csv file."
        homedir = str(pathlib.Path().home())
        filetype = "Comma Separated Values files (*.csv)"

        csv_filepath, _ = QFileDialog.getSaveFileName(self,
                                                      dialog_title,
                                                      homedir,
                                                      filetype)

        if csv_filepath != '':
            model = self.results_table.model()
            df = model.get_doe_data()

            df.to_csv(path_or_buf=csv_filepath, sep=',', index=False)
