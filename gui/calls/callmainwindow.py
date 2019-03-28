import pathlib
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QTableWidgetItem
from PyQt5.QtCore import Qt
from gui.views.py_files.mainwindow import *
from gui.calls.callsimulationtree import LoadSimulationTreeDialog
from gui.models.data_storage import DataStorage


class MainWindow(QMainWindow):

    def __init__(self):
        # initialization
        self.streams_file = None  # for when the tree txt files are specified
        self.blocks_file = None

        # AbstractItem rows database initialization for tree view in load simulation variables dialog
        self.application_database = DataStorage()

        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # internal variables initialization
        self.sim_filename = ""

        # signal/socket connections
        self.ui.buttonOpenSimFile.clicked.connect(self.openSimFileDialog)
        self.ui.buttonLoadVariables.clicked.connect(self.openSimTreeDialog)

        # some widget initializations

    # open simulation file
    def openSimFileDialog(self):
        homedir = str(pathlib.Path.home())  # home directory (platform independent)
        sim_filename, sim_filetype = QFileDialog.getOpenFileName(self, "Select .bkp simulation file", homedir,
                                                                 "BKP files (*.bkp);; Input files (*.inp)")

        if sim_filename == "" or (sim_filetype != "BKP files (*.bkp)" and sim_filetype != "Input files (*.inp)"):
            # user canceled the file dialog or selected invalid file
            if self.ui.textBrowserSimFile.styleSheet() != "color: blue":  # if there isn't an invalid path already
                self.ui.textBrowserSimFile.setText("Invalid or no file selected.")
                self.ui.textBrowserSimFile.setStyleSheet("color: red")
                self.ui.buttonLoadVariables.setEnabled(False)  # deactivate load button

        else:
            # it's a valid file. Set its path as string and color. Also make its filepath available to the ui
            self.sim_filename = sim_filename
            self.ui.textBrowserSimFile.setText(sim_filename)
            self.ui.buttonLoadVariables.setEnabled(True)  # deactivate load button

    # open simulationtree dialog
    def openSimTreeDialog(self):
        if self.sim_filename != "":
            dialog = LoadSimulationTreeDialog(self.sim_filename, self.application_database,
                                              streams_file_txt_path=self.streams_file,
                                              blocks_file_txt_path=self.blocks_file)

            if dialog.exec_():
                # the ok button was pressed, get the variables the user selected and update other ui items
                vars_list = [self.application_database.getInputTableData(),
                             self.application_database.getOutputTableData()]

                simulation_form_data = self.application_database.getSimulationDataDictionary()

                # set the simulation form data
                self.ui.lineEditComponents.setText(str(len(simulation_form_data['components'])))
                self.ui.lineEditBlocks.setText(str(len(simulation_form_data['blocks'])))
                self.ui.lineEditStreams.setText(str(len(simulation_form_data['streams'])))
                self.ui.lineEditMethodName.setText(str(simulation_form_data['therm_method']))
                self.ui.lineEditReactions.setText(str(len(simulation_form_data['reactions'])))
                self.ui.lineEditSensAnalysis.setText(str(len(simulation_form_data['sens_analysis'])))
                self.ui.lineEditCalculators.setText(str(len(simulation_form_data['calculators'])))
                self.ui.lineEditOptimizations.setText(str(len(simulation_form_data['optimizations'])))
                self.ui.lineEditDesSpecs.setText(str(len((simulation_form_data['design_specs']))))

                # set alias table data
                alias_table_view = self.ui.tableWidgetAliasDisplay

                new_aliases_to_insert = []
                new_types_to_insert = []

                for input_row in vars_list[0]:
                    new_aliases_to_insert.append(input_row[1])
                    new_types_to_insert.append(input_row[2])

                for output_row in vars_list[1]:
                    new_aliases_to_insert.append(output_row[1])
                    new_types_to_insert.append("Candidate (CV)")

                num_rows_alias = alias_table_view.rowCount()

                if num_rows_alias != 0:  # alias table is not empty
                    alias_table_view.setRowCount(0)  # delete all the present rows

                for i in range(len(new_aliases_to_insert)):
                    alias_table_view.insertRow(i)

                    alias_table_item_name = QTableWidgetItem(new_aliases_to_insert[i])
                    alias_table_item_type = QTableWidgetItem(new_types_to_insert[i])

                    alias_table_item_name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    alias_table_item_type.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

                    alias_table_view.setItem(i, 0, alias_table_item_name)
                    alias_table_view.setItem(i, 1, alias_table_item_type)

    def setTreeTxtFilesPath(self, streams_file, blocks_file):
        self.streams_file = streams_file
        self.blocks_file = blocks_file


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()

    sys.exit(app.exec_())
