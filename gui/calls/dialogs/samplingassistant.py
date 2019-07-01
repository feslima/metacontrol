import numpy as np
import pandas as pd
import pathlib
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import (QApplication, QDialog, QHeaderView, QMessageBox,
                             QStatusBar, QTableWidgetItem, QFileDialog)

from gui.calls.base import my_exception_hook
from gui.calls.dialogs.lhssettings import LhsSettingDialog
from gui.models.data_storage import DataStorage
from gui.models.sampling import SamplerThread, lhs
from gui.views.py_files.samplingassistant import Ui_Dialog

# FIXME: Implement MVC pattern


class SamplingAssistantDialog(QDialog):
    input_design_changed = pyqtSignal()

    # CONSTANTS
    _INPUT_COL_OFFSET = 2
    _HEADER_ROW_OFFSET = 2

    def __init__(self, application_database: DataStorage):
        # ------------------------ Internal Variables -------------------------
        self.app_data = application_database
        self._input_design = None

        # load internal headers names
        input_alias = [row['Alias'] for row in self.app_data.input_table_data
                       if row['Type'] == 'Manipulated (MV)']
        output_alias = [row['Alias']
                        for row in self.app_data.output_table_data]
        aliases = input_alias + output_alias

        self._sampled_data = pd.DataFrame(columns=aliases)

        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowFlags(Qt.Window)
        # ----------------------- Widget Initialization -----------------------
        # status bar
        self.statBar = QStatusBar(self)
        self.ui.horizontalLayout.addWidget(self.statBar)

        results_view = self.ui.samplerDisplayTableWidget

        # set the results table headerview to stretch
        results_view.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        results_view.horizontalHeader().setMinimumSectionSize(50)

        # place the headers
        results_view.setRowCount(self._HEADER_ROW_OFFSET)
        results_view.setColumnCount(self._INPUT_COL_OFFSET + len(aliases))

        # case number header
        case_num_item = QTableWidgetItem('Case Number')
        case_num_item.setTextAlignment(Qt.AlignCenter)
        results_view.setSpan(0, 0, self._HEADER_ROW_OFFSET, 1)
        results_view.setItem(0, 0, case_num_item)

        # case status header
        case_status_item = QTableWidgetItem('Status')
        case_status_item.setTextAlignment(Qt.AlignCenter)
        results_view.setSpan(0, 1, self._HEADER_ROW_OFFSET, 1)
        results_view.setItem(0, 1, case_status_item)

        # Inputs section header
        inputs_item = QTableWidgetItem('Inputs')
        inputs_item.setTextAlignment(Qt.AlignCenter)
        results_view.setSpan(0, self._INPUT_COL_OFFSET, 1, len(input_alias))
        results_view.setItem(0, self._INPUT_COL_OFFSET, inputs_item)

        # Outputs section header
        outputs_item = QTableWidgetItem('Outputs')
        outputs_item.setTextAlignment(Qt.AlignCenter)
        results_view.setSpan(0, self._INPUT_COL_OFFSET +
                             self._INPUT_COL_OFFSET, 1, len(output_alias))
        results_view.setItem(0, self._INPUT_COL_OFFSET +
                             self._INPUT_COL_OFFSET, outputs_item)

        # place the subheaders
        for col, alias in enumerate(aliases):
            item = QTableWidgetItem(alias)
            item.setTextAlignment(Qt.AlignCenter)

            results_view.setItem(1, col + self._INPUT_COL_OFFSET, item)

        # --------------------------- Signals/Slots ---------------------------
        # generate lhs and lhs settings
        self.ui.genLhsPushButton.clicked.connect(self.generate_lhs)
        self.ui.lhsSettingsPushButton.clicked.connect(self.open_lhs_settings)

        # update the input design display and enables/disable sampling button
        self.input_design_changed.connect(self.update_input_design_display)
        self.input_design_changed.connect(self.enable_sampling_button)

        # starts sampling when pressing sample data button
        self.ui.sampDataPushButton.clicked.connect(self.sample_data)

        # aborts sampling when pressing button
        self.ui.abortSamplingPushButton.clicked.connect(
            self.abort_sampling_thread)

        # closes the dialog when cancel buttons is pressed
        self.ui.cancelPushButton.clicked.connect(self.close)

        # stores sampled data and closes dialog when user is done sampling
        self.ui.donePushButton.clicked.connect(self.on_sampling_done)

        # exports data in display to csv when pressing button
        self.ui.exportCsvPushButton.clicked.connect(self.export_csv)
        # ---------------------------------------------------------------------

    @property
    def input_design(self):
        """The design of experiments matrix (input design)."""
        return self._input_design

    @input_design.setter
    def input_design(self, value: np.ndarray):
        self._input_design = value
        self.input_design_changed.emit()
        self.ui.displayProgressBar.setMaximum(value.shape[0])

    # -------------------------------------------------------------------------
    def on_sampling_done(self):
        """When the user is done sampling and presses the done button, store
        the sampled data if it exists and closes the dialog.
        """
        if not self._sampled_data.empty:
            self.app_data.doe_sampled_data = self._sampled_data.to_dict('list')

        self.close()

    def open_lhs_settings(self):
        """Opens the dialog to configure the LHS parameters.
        """
        dialog = LhsSettingDialog(self.app_data)
        dialog.exec_()

    def generate_lhs(self):
        """Generate LHS matrix and make it available to the GUI.
        """
        reply = QMessageBox.No
        if self.input_design is not None:
            # there is data already in display in the table, warn the user
            msg_str = ("By clicking yes ALL data, including input and "
                       "output already sampled will be deleted! Proceed at "
                       "your own risk.")
            reply = QMessageBox().question(self, "Renew input design?",
                                           msg_str, QMessageBox.Yes,
                                           QMessageBox.No)

        if reply == QMessageBox.Yes or self.input_design is None:
            mv_bnds = self.app_data.doe_mv_bounds
            lhs_settings = self.app_data.doe_lhs_settings

            lb_list, ub_list = map(
                list, zip(*[(row['lb'], row['ub']) for row in mv_bnds]))

            lhs_table = lhs(lhs_settings['n_samples'], lb_list, ub_list,
                            lhs_settings['n_iter'],
                            lhs_settings['inc_vertices'])

            self.input_design = lhs_table

    def update_input_design_display(self):
        """Updates the input design display in the GUI.
        """
        sampler_view = self.ui.samplerDisplayTableWidget
        lhs_table = self.input_design

        if lhs_table is not None:
            n_samples = lhs_table.shape[0]

            # clear the table values and initialize rows
            sampler_view.setRowCount(self._HEADER_ROW_OFFSET)
            sampler_view.setRowCount(n_samples + self._HEADER_ROW_OFFSET)

            # clear the progress bar
            self.ui.displayProgressBar.setValue(0)

            # set values
            for row in range(n_samples):
                case_num_item = QTableWidgetItem(str(row + 1))
                case_num_item.setTextAlignment(Qt.AlignCenter)

                sampler_view.setItem(self._HEADER_ROW_OFFSET + row,
                                     0,
                                     case_num_item)

                for col in range(lhs_table.shape[1]):
                    item = QTableWidgetItem(str(lhs_table[row, col]))
                    item.setTextAlignment(Qt.AlignCenter)

                    sampler_view.setItem(self._HEADER_ROW_OFFSET + row,
                                         self._INPUT_COL_OFFSET + col,
                                         item)

    def enable_sampling_button(self):
        """Enables or disable sampling button based on input_design values.
        """
        if self.input_design is not None:
            self.ui.sampDataPushButton.setEnabled(True)
        else:
            self.ui.sampDataPushButton.setEnabled(False)

    def sample_data(self):
        """Starts the sampling of the DOE in display.
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

        # create thread
        self.sampler = SamplerThread(self.input_design, self.app_data)
        self.sampler.case_sampled.connect(self.on_case_sampled)
        self.sampler.started.connect(self.statBar.clearMessage)
        self.sampler.finished.connect(self.on_sampling_finished)
        self.sampler.start()

    def on_case_sampled(self, row: int, sampled_values: dict):
        """Slot that performs the simulation and displays data in the table.

        Parameters
        ----------
        row : int
            Row number.
        sampled_values : dict
            Dictionary containing the sampled data
        """
        sampler_view = self.ui.samplerDisplayTableWidget
        output_offset = self.input_design.shape[1] + self._INPUT_COL_OFFSET

        # place the convergence flag
        flag_item = QTableWidgetItem(sampled_values['success'])
        flag_item.setTextAlignment(Qt.AlignCenter)
        sampler_view.setItem(1 + row, 1, flag_item)

        # delete the success key
        del sampled_values['success']

        for col, value in enumerate(sampled_values.values()):
            value_item = QTableWidgetItem(str(value))
            value_item.setTextAlignment(Qt.AlignCenter)
            sampler_view.setItem(1 + row, output_offset + col, value_item)

        self.ui.displayProgressBar.setValue(row)

    def on_sampling_finished(self):
        """Clean up routine executed when the sampling is finished.
        """
        # enable gen lhs, sample and export buttons
        self.ui.genLhsPushButton.setEnabled(True)
        self.ui.sampDataPushButton.setEnabled(True)
        self.ui.exportCsvPushButton.setEnabled(True)
        self.ui.donePushButton.setEnabled(True)
        self.ui.cancelPushButton.setEnabled(True)

        # disable the abort button and sample data
        self.ui.abortSamplingPushButton.setEnabled(False)

        # update the internal dataframe variable
        self._sampled_data = self.get_current_data_in_display()

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
            df = self.get_current_data_in_display()

            df.to_csv(path_or_buf=csv_filepath, sep=',', index=False)

    def get_current_data_in_display(self) -> pd.DataFrame:
        """Returns the sampled data in display as a pandas DataFrame
        """
        sampler_view = self.ui.samplerDisplayTableWidget

        headers = ['case', 'status'] + \
            [sampler_view.item(1, col).text()
             for col in range(self._INPUT_COL_OFFSET,
                              sampler_view.columnCount())]

        n_rows = sampler_view.rowCount() - self._HEADER_ROW_OFFSET
        n_cols = sampler_view.columnCount()

        data = np.zeros((n_rows, n_cols), dtype=object)
        for row in range(n_rows):
            for col in range(n_cols):
                data_txt = sampler_view.item(
                    self._HEADER_ROW_OFFSET + row, col).text()

                data[row, col] = float(data_txt) if col != 1 else data_txt

        return pd.DataFrame(data=data, columns=headers)

    def resizeEvent(self, e: QResizeEvent):
        """Override to automatically resize column widths.
        """
        results_view = self.ui.samplerDisplayTableWidget
        results_horz_headers = results_view.horizontalHeader()

        # set header view to strecth
        results_horz_headers.setSectionResizeMode(QHeaderView.Stretch)

        # store the columns width values
        col_widths = [results_horz_headers.sectionSize(col)
                      for col in range(results_view.columnCount())]

        if results_view.rowCount() > self._HEADER_ROW_OFFSET:
            # if the table is not empty, resize the columns
            results_horz_headers.setSectionResizeMode(QHeaderView.Interactive)

            # resize the columns to the width stored
            [results_horz_headers.resizeSection(col, value)
             for col, value in enumerate(col_widths)]


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook
    from tests_.mock_data import DOE_TAB_MOCK_DS

    app = QApplication(sys.argv)
    ds = DOE_TAB_MOCK_DS
    w = SamplingAssistantDialog(application_database=ds)
    w.show()

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
