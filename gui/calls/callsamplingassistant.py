from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem, QHeaderView, QMessageBox, QStatusBar, \
    QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QResizeEvent

from gui.views.py_files.samplingassistant import Ui_Dialog
from gui.calls.calllhssettings import LhsSettingsDialog
from gui.models.sampling import SamplerThread, lhs
from gui.models.data_storage import DataStorage

import csv
import pathlib


class SamplingAssistantDialog(QDialog):
    inputDesignChanged = pyqtSignal()

    # consts
    INPUT_COL_OFFSET = 2
    HEADER_OFFSET = 2

    def __init__(self, application_database: DataStorage):
        # ------------------------------ Form Initialization ----------------------------
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowFlags(Qt.Window)
        # self.setWindowState(Qt.WindowMaximized)

        self.application_database = application_database

        # ------------------------------ WidgetInitialization ------------------------------
        # status bar
        self.statBar = QStatusBar(self)
        self.ui.horizontalLayout.addWidget(self.statBar)

        results_table_view = self.ui.samplerDisplayTableWidget

        # set the table results headerview to stretch
        results_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        results_table_view.horizontalHeader().setMinimumSectionSize(50)

        # load the internal headers
        input_alias_list = [row['Alias'] for row in self.application_database.input_table_data
                            if row['Type'] == 'Manipulated (MV)']
        output_alias_list = [row['Alias'] for row in self.application_database.output_table_data]

        # place the headers in the first and second rows
        results_table_view.setRowCount(self.HEADER_OFFSET)
        results_table_view.setColumnCount(self.INPUT_COL_OFFSET + len(input_alias_list + output_alias_list))
        results_table_view.setSpan(0, 0, self.HEADER_OFFSET, 1)
        results_table_view.setItem(0, 0, QTableWidgetItem('Case Number'))
        results_table_view.item(0, 0).setTextAlignment(Qt.AlignCenter)

        results_table_view.setSpan(0, 1, self.HEADER_OFFSET, 1)
        results_table_view.setItem(0, 1, QTableWidgetItem('Status'))
        results_table_view.item(0, 1).setTextAlignment(Qt.AlignCenter)

        results_table_view.setSpan(0, self.INPUT_COL_OFFSET, 1, len(input_alias_list))
        results_table_view.setItem(0, self.INPUT_COL_OFFSET, QTableWidgetItem('Inputs'))
        results_table_view.item(0, self.INPUT_COL_OFFSET).setTextAlignment(Qt.AlignCenter)

        results_table_view.setSpan(0, self.INPUT_COL_OFFSET + self.HEADER_OFFSET, 1, len(output_alias_list))
        results_table_view.setItem(0, self.INPUT_COL_OFFSET + self.HEADER_OFFSET, QTableWidgetItem('Outputs'))
        results_table_view.item(0, self.INPUT_COL_OFFSET + self.HEADER_OFFSET).setTextAlignment(Qt.AlignCenter)

        # place the subheaders (alias) in the second row
        all_alias = input_alias_list + output_alias_list
        for j in range(len(all_alias)):
            item_place_holder = QTableWidgetItem(all_alias[j])
            results_table_view.setItem(1, j + self.INPUT_COL_OFFSET, item_place_holder)
            item_place_holder.setTextAlignment(Qt.AlignCenter)

        # ------------------------------ Signals/Slots ------------------------------
        self.ui.sampDataPushButton.clicked.connect(self.sampleData)
        self.ui.donePushButton.clicked.connect(self.doneButtonPressed)
        self.ui.cancelPushButton.clicked.connect(self.reject)
        self.ui.exportCsvPushButton.clicked.connect(self.exportCsv)
        self.ui.genLhsPushButton.clicked.connect(self.generateLhsPressed)
        self.ui.lhsSettingsPushButton.clicked.connect(self.openLhsSettingsDialog)
        self.ui.abortSamplingPushButton.clicked.connect(self.abortButtonPressed)

        self.inputDesignChanged.connect(self.enableSampleDataButton)
        self.inputDesignChanged.connect(self.displayInputDesignData)

        # ------------------------------ Internal variables ------------------------------
        self._input_design = None
        self.sampled_data = []

    def doneButtonPressed(self):
        # store the sampled data
        self.application_database.sampled_data = self.sampled_data

        self.accept()

    def _setInputDesign(self, input_design):
        # input design values setter to allow signal emission
        self._input_design = input_design
        self.inputDesignChanged.emit()

    def _getInputDesing(self):
        return self._input_design

    def enableSampleDataButton(self):
        if self._getInputDesing() is not None:
            self.ui.sampDataPushButton.setEnabled(True)  # if the lhs data is not empty, enable the sample button
        else:
            self.ui.sampDataPushButton.setEnabled(False)

    def openLhsSettingsDialog(self):
        dialog = LhsSettingsDialog(self.application_database)
        dialog.exec_()

    def generateLhsPressed(self):
        """
Generate the lhs data and make it available to the GUI
        """
        reply = QMessageBox.No
        if self._getInputDesing() is not None:
            # warn the user if there is data in the table
            reply = QMessageBox().question(self, 'Renew input design?',
                                           'By clicking Yes ALL data, including input and output already sampled, will '
                                           'be deleted!',
                                           QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes or self._getInputDesing() is None:
            doe_app_data = self.application_database.doe_data
            mv_app_data = doe_app_data['mv']
            lhs_app_data = doe_app_data['lhs']

            lb_list = [entry['lb'] for entry in mv_app_data]
            ub_list = [entry['ub'] for entry in mv_app_data]

            lhs_table = lhs(lhs_app_data['n_samples'], lb_list, ub_list, lhs_app_data['n_iter'],
                            lhs_app_data['inc_vertices'])

            self._setInputDesign(lhs_table)  # store the data and fire the signal
            self.ui.displayProgressBar.setMaximum(lhs_table.shape[0])

    def displayInputDesignData(self):
        """
Grabs the input design table stored in the GUI and displays it
        """
        sampler_table_view = self.ui.samplerDisplayTableWidget
        lhs_table = self._getInputDesing()

        if lhs_table is not None:
            sampler_table_view.setRowCount(self.HEADER_OFFSET)  # flush the table
            self.ui.displayProgressBar.setValue(0)  # flush the progress bar
            sampler_table_view.setRowCount(lhs_table.shape[0] + self.HEADER_OFFSET)  # expand the rows

            for row in range(lhs_table.shape[0]):
                case_num_item_placeholder = QTableWidgetItem(str(row + 1))
                sampler_table_view.setItem(self.HEADER_OFFSET + row, 0, case_num_item_placeholder)
                case_num_item_placeholder.setTextAlignment(Qt.AlignCenter)
                for col in range(lhs_table.shape[1]):
                    item_place_holder = QTableWidgetItem(str(lhs_table[row, col]))
                    sampler_table_view.setItem(self.HEADER_OFFSET + row, self.INPUT_COL_OFFSET + col, item_place_holder)
                    item_place_holder.setTextAlignment(Qt.AlignCenter)

    def sampleData(self):
        # disable buttons
        self.onSamplingStarted()

        # change status bar text
        self.statBar.showMessage('Opening connection to simulator engine...')

        # reset progress bar value
        self.ui.displayProgressBar.setValue(0)

        # create the thread object
        self.sampler = SamplerThread(self._getInputDesing(), self.application_database)
        self.sampler.caseSampled.connect(self.onCaseSampled)
        self.sampler.started.connect(self.statBar.clearMessage)
        self.sampler.finished.connect(self.onSamplingFinished)
        self.sampler.start()

    def onSamplingStarted(self):
        # disable gen lhs, sample and export buttons
        self.ui.genLhsPushButton.setEnabled(False)
        self.ui.sampDataPushButton.setEnabled(False)
        self.ui.exportCsvPushButton.setEnabled(False)

        # enable the abort button
        self.ui.abortSamplingPushButton.setEnabled(True)

    def onSamplingFinished(self):
        # enable gen lhs, sample and export buttons
        self.ui.genLhsPushButton.setEnabled(True)
        self.ui.sampDataPushButton.setEnabled(True)
        self.ui.exportCsvPushButton.setEnabled(True)

        # disable the abort button and sample data
        self.ui.abortSamplingPushButton.setEnabled(False)

    def onCaseSampled(self, row, sampled_values):
        # receives single case sampled data and row to place it in the output columns of the display table
        sampler_table_view = self.ui.samplerDisplayTableWidget
        output_offset = self._getInputDesing().shape[1] + self.INPUT_COL_OFFSET

        # place the convergence flag
        sampled_values_placeholder = QTableWidgetItem(sampled_values['success'])
        sampler_table_view.setItem(1 + row, 1, sampled_values_placeholder)
        sampled_values_placeholder.setTextAlignment(Qt.AlignCenter)

        # delete the dict key
        del sampled_values['success']

        for col_idx, col in enumerate(sampled_values.values()):
            sampled_values_placeholder = QTableWidgetItem(str(col))
            sampler_table_view.setItem(1 + row, output_offset + col_idx, sampled_values_placeholder)
            sampled_values_placeholder.setTextAlignment(Qt.AlignCenter)

        self.sampled_data.append([sampler_table_view.item(1 + row, 1).text()] +
                                 [float(sampler_table_view.item(1 + row, col).text())
                                  for col in range(self.INPUT_COL_OFFSET, sampler_table_view.columnCount())])

        self.ui.displayProgressBar.setValue(row)

    def abortButtonPressed(self):
        # stops the thread execution
        self.sampler.requestInterruption()

    def exportCsv(self):
        # query the user to save the file
        csv_file_name, _ = QFileDialog.getSaveFileName(self, "Select where to save the .csv file",
                                                       str(pathlib.Path.home()), "Comma Separated Values files (*.csv)")
        if csv_file_name == '':
            # user canceled the dialog
            pass
        else:
            sampler_table_view = self.ui.samplerDisplayTableWidget

            # get the headers names
            headers = ['case', 'status'] + [sampler_table_view.item(1, col).text()
                                            for col in range(self.INPUT_COL_OFFSET, sampler_table_view.columnCount())]

            # read the data from the table
            csv_data = []
            with open(csv_file_name, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(headers)

                for row in range(self.HEADER_OFFSET, sampler_table_view.rowCount()):
                    row_txt_list = [sampler_table_view.item(row, col).text()
                                    for col in range(sampler_table_view.columnCount())]
                    csv_data.append(row_txt_list)
                    csv_writer.writerow(row_txt_list)

    def resizeEvent(self, e: QResizeEvent):
        results_table_view = self.ui.samplerDisplayTableWidget

        # set the table results headerview to stretch
        results_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # store the column width values
        col_widths = [results_table_view.horizontalHeader().sectionSize(j)
                      for j in range(results_table_view.columnCount())]

        if results_table_view.rowCount() > 2:  # if the table is not empty, resize the columns
            # set the mode to interactive
            results_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

            # resize the columns to the widths stored
            [results_table_view.horizontalHeader().resizeSection(j, value) for j, value in enumerate(col_widths)]


if __name__ == "__main__":
    import sys
    from gui.models.data_storage import DataStorage

    from tests_.gui.mock_data import simulation_data, input_table_data, output_table_data, expr_table_data, \
        doe_table_data, sim_file_name

    app = QApplication(sys.argv)

    mock_storage = DataStorage()
    mock_storage.rigorous_model_filepath = sim_file_name
    mock_storage.simulation_data = simulation_data
    mock_storage.input_table_data = input_table_data
    mock_storage.output_table_data = output_table_data
    mock_storage.expression_table_data = expr_table_data
    mock_storage.doe_data = doe_table_data

    w = SamplingAssistantDialog(mock_storage)
    w.show()


    def my_exception_hook(exctype, value, tback):
        # Print the error and traceback
        print(exctype, value, tback)
        # Call the normal Exception hook after
        sys.__excepthook__(exctype, value, tback)
        sys.exit()


    sys._excepthook = sys.excepthook

    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook

    if w.exec():
        print(w.sampled_data)

    sys.exit(app.exec_())
