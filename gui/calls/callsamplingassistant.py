from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal

from gui.views.py_files.samplingassistant import Ui_Dialog
from gui.calls.calllhssettings import LhsSettingsDialog
from gui.models.sampling import SamplerThread, lhs
from gui.models.data_storage import DataStorage


# TODO: (21/04/2016)  return sampled values to the doetab

class SamplingAssistantDialog(QDialog):
    inputDesignChanged = pyqtSignal()

    def __init__(self, application_database: DataStorage):
        # ------------------------------ Form Initialization ----------------------------
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowFlags(Qt.Window)
        # self.setWindowState(Qt.WindowMaximized)

        self.application_database = application_database

        # ------------------------------ WidgetInitialization ------------------------------
        # load the internal headers
        results_table_view = self.ui.samplerDisplayTableWidget
        results_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        results_table_view.horizontalHeader().setMinimumSectionSize(50)

        input_alias_list = [row['Alias'] for row in self.application_database.getInputTableData()
                            if row['Type'] == 'Manipulated (MV)']
        output_alias_list = [row['Alias'] for row in self.application_database.getOutputTableData()]

        expr_list = [row['Name'] for row in self.application_database.getExpressionTableData()]

        # place the headers in the first and second rows
        results_table_view.setRowCount(2)
        results_table_view.setColumnCount(1 + len(input_alias_list + output_alias_list + expr_list))
        results_table_view.setSpan(0, 0, 2, 1)
        results_table_view.setItem(0, 0, QTableWidgetItem('Case Number'))
        results_table_view.item(0, 0).setTextAlignment(Qt.AlignCenter)

        results_table_view.setSpan(0, 1, 1, len(input_alias_list))
        results_table_view.setItem(0, 1, QTableWidgetItem('Inputs'))
        results_table_view.item(0, 1).setTextAlignment(Qt.AlignCenter)

        results_table_view.setSpan(0, 3, 1, len(output_alias_list + expr_list))
        results_table_view.setItem(0, 3, QTableWidgetItem('Outputs'))
        results_table_view.item(0, 3).setTextAlignment(Qt.AlignCenter)

        # place the subheaders (alias) in the second row
        all_alias = input_alias_list + output_alias_list + expr_list
        for j in range(len(all_alias)):
            item_place_holder = QTableWidgetItem(all_alias[j])
            results_table_view.setItem(1, j + 1, item_place_holder)
            item_place_holder.setTextAlignment(Qt.AlignCenter)

        # ------------------------------ Signals/Slots ------------------------------
        self.ui.sampDataPushButton.clicked.connect(self.sampleData)
        self.ui.genLhsPushButton.clicked.connect(self.generateLhsPressed)
        self.ui.lhsSettingsPushButton.clicked.connect(self.openLhsSettingsDialog)
        self.ui.cancelPushButton.clicked.connect(self.reject)
        self.ui.abortSamplingPushButton.clicked.connect(self.abortButtonPressed)

        self.inputDesignChanged.connect(self.enableSampleDataButton)
        self.inputDesignChanged.connect(self.displayInputDesignData)

        # ------------------------------ Internal variables ------------------------------
        self._input_design = None

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
            doe_app_data = self.application_database.getDoeData()
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
            sampler_table_view.setRowCount(2)  # flush the table
            self.ui.displayProgressBar.setValue(0)  # flush the progress bar
            sampler_table_view.setRowCount(lhs_table.shape[0] + 2)  # expand the rows

            for row in range(lhs_table.shape[0]):
                case_num_item_placeholder = QTableWidgetItem(str(row + 1))
                sampler_table_view.setItem(2 + row, 0, case_num_item_placeholder)
                case_num_item_placeholder.setTextAlignment(Qt.AlignCenter)
                for col in range(lhs_table.shape[1]):
                    item_place_holder = QTableWidgetItem(str(lhs_table[row, col]))
                    sampler_table_view.setItem(2 + row, 1 + col, item_place_holder)
                    item_place_holder.setTextAlignment(Qt.AlignCenter)

    def sampleData(self):
        # TODO: Remember to disable all other buttons that generate new input designs until the sampling is finished
        # disable buttons
        self.onSamplingStarted()

        # create the thread object
        self.sampler = SamplerThread(self._getInputDesing(), self.application_database)
        self.sampler.caseSampled.connect(self.onCaseSampled)
        self.sampler.finished.connect(self.onSamplingFinished)
        self.sampler.start()

        # self.accept()

    def onSamplingStarted(self):
        # disable gen lhs and sample buttons
        self.ui.genLhsPushButton.setEnabled(False)
        self.ui.sampDataPushButton.setEnabled(False)

        # enable the abort button
        self.ui.abortSamplingPushButton.setEnabled(True)

    def onSamplingFinished(self):
        # enable gen lhs and sample buttons
        self.ui.genLhsPushButton.setEnabled(True)
        self.ui.sampDataPushButton.setEnabled(True)

        # disable the abort button
        self.ui.abortSamplingPushButton.setEnabled(False)

    def onCaseSampled(self, row, sampled_values):
        # receives single case sampled data and row to place it in the output columns of the display table
        self.ui.displayProgressBar.setValue(row)

        sampler_table_view = self.ui.samplerDisplayTableWidget
        input_offset = self._getInputDesing().shape[1] + 1
        for col_idx, col in enumerate(sampled_values.values()):
            sampled_values_placeholder = QTableWidgetItem(str(col))
            sampler_table_view.setItem(1 + row, input_offset + col_idx, sampled_values_placeholder)
            sampled_values_placeholder.setTextAlignment(Qt.AlignCenter)

    def abortButtonPressed(self):
        # stops the thread execution
        self.sampler.requestInterruption()


if __name__ == "__main__":
    import sys
    from gui.models.data_storage import DataStorage

    from tests.gui.mock_data import simulation_data, input_table_data, output_table_data, expr_table_data, \
        doe_table_data, sim_file_name

    app = QApplication(sys.argv)

    mock_storage = DataStorage()
    mock_storage.setSimulationFilePath(sim_file_name)
    mock_storage.setSimulationDataDictionary(simulation_data)
    mock_storage.setInputTableData(input_table_data)
    mock_storage.setOutputTableData(output_table_data)
    mock_storage.setExpressionTableData(expr_table_data)
    mock_storage.setDoeData(doe_table_data)

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

    sys.exit(app.exec_())
