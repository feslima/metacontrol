import csv
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QCheckBox, QHBoxLayout, QWidget, QItemDelegate, \
    QComboBox, QMessageBox, QHeaderView, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush

from gui.views.py_files.csv_editor import Ui_Dialog
from gui.models.data_storage import DataStorage
from gui.calls.callconvergenceselector import ConvergenceSelectorDialog

import numpy as np
import pathlib

# FIXME: (25/04/2019) ask the user to set which column in the csv is the convergence flag one

class ComboBoxDelegate(QItemDelegate):

    def __init__(self, item_list, parent=None):
        QItemDelegate.__init__(self, parent)
        self.item_list = item_list

    def createEditor(self, parent, option, index):
        combo_box = QComboBox(parent)
        combo_box.addItems(self.item_list)

        return combo_box

    def setEditorData(self, editor, index):
        editor.showPopup()

    def setModelData(self, editor, model, index):
        value = editor.itemText(editor.currentIndex())
        model.setData(index, value, Qt.EditRole)

        # check if the selected value is repeated
        aliases = [model.data(model.index(1, col)) for col in range(model.columnCount())]

        if aliases.count(value) > 1:
            # value is present, paint the cell red
            model.setData(index, QBrush(Qt.red), Qt.BackgroundRole)

            # change the tooltip to warn the user
            if value != 'Select Alias':
                model.parent().item(index.row(), index.column()).setToolTip('Alias already in use!')
            else:
                model.parent().item(index.row(), index.column()).setToolTip('Select an alias for this variable!')
        else:
            original_backgrd_color = editor.palette().color(editor.backgroundRole())
            model.setData(index, QBrush(original_backgrd_color), Qt.BackgroundRole)

            # rest the tooltip
            model.parent().item(index.row(), index.column()).setToolTip('')

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class CsvEditorDialog(QDialog):
    def __init__(self, application_data: DataStorage):
        # ---------------------- dialog initialization ----------------------
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Window)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowState(Qt.WindowMaximized)

        self.application_data = application_data

        # ---------------------- connections ----------------------
        # self.ui.okPushButton.clicked.connect(self.okButtonPressed)
        self.ui.openCsvFilePushButton.clicked.connect(self.openCsvFileDialog)

        # ---------------------- table initialization ----------------------
        csv_filepath = self.application_data.csv_filepath

        with open(csv_filepath, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            headers = csv_reader.fieldnames

        # read the numbers
        data_values = np.genfromtxt(csv_filepath, delimiter=',', skip_header=1,
                                    converters={1: lambda x: 1. if x == b"OK" or x == b"ok" else 0.})
        col_count = len(headers)
        self.ui.csvTableWidget.setColumnCount(col_count)
        self._combobox_delegates_dict = {}

        # add 2 rows (first for checkboxes, second one for combo_boxes
        self.ui.csvTableWidget.setRowCount(data_values.shape[0] + 2)
        for j in range(col_count):
            # create the column headers
            item = QTableWidgetItem(headers[j])

            # create checkboxes for first row of table
            item_check_widget_ph = QWidget()
            item_check = QCheckBox()
            item_check.setChecked(True)
            item_check.stateChanged.connect(self._checkbox_changed)  # connect the signal
            item_check_layout = QHBoxLayout(item_check_widget_ph)
            item_check_layout.addWidget(item_check)
            item_check_layout.setAlignment(Qt.AlignCenter)
            item_check_layout.setContentsMargins(0, 0, 0, 0)
            self.ui.csvTableWidget.setHorizontalHeaderItem(j, item)
            self.ui.csvTableWidget.setCellWidget(0, j, item_check_widget_ph)

            # insert the values
            for i in range(data_values.shape[0]):
                value_item = QTableWidgetItem(str(data_values[i, j]))
                value_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                value_item.setTextAlignment(Qt.AlignCenter)
                self.ui.csvTableWidget.setItem(2 + i, j, value_item)

        self.readPairInfoFromStorage()

        # column width adjustments
        self.ui.csvTableWidget.horizontalHeader().setMinimumSectionSize(80)
        self.ui.csvTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.csvTableWidget.horizontalHeader().setStretchLastSection(True)

    def openCsvFileDialog(self):
        homedir = str(pathlib.Path.home())  # home directory (platform independent)
        csv_filename, _ = QFileDialog.getOpenFileName(self, "Select .csv containing DOE data", homedir,
                                                      "CSV files (*.csv)")

        # if the csv is valid
        if csv_filename != "":
            self.ui.lineEditCsvFilePath.setText(csv_filename)
            # ask the user which header is the convergence flag

            with open(csv_filename, mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file)

                headers = csv_reader.fieldnames

            conv_dialog = ConvergenceSelectorDialog(headers)

            status_index = None
            if conv_dialog.exec():
                status_index = headers.index()

            # self.ui.loadFilePushButton.setEnabled(True)


    def readPairInfoFromStorage(self):
        pair_info = self.application_data.csv_pair_info

        table_view = self.ui.csvTableWidget

        alias_list = [entry['Alias'] for entry in self.application_data.input_table_data
                      if entry['Type'] == 'Manipulated (MV)'] + \
                     [entry['Alias'] for entry in self.application_data.output_table_data]

        table_view.setItemDelegateForRow(1, ComboBoxDelegate(alias_list))

        if len(pair_info) == 0:  # no pair info defined, set every thing to default (Select Alias - red)
            for col in range(table_view.columnCount()):
                # combo_box delegate for second row (alias setting)
                alias_default_item = QTableWidgetItem('Select Alias')
                alias_default_item.setTextAlignment(Qt.AlignCenter)
                alias_default_item.setData(Qt.BackgroundRole, QBrush(Qt.red))
                table_view.setItem(1, col, alias_default_item)

        else:  # pair defined
            for pair in pair_info:
                alias_item = QTableWidgetItem(pair['alias'])
                alias_item.setTextAlignment(Qt.AlignCenter)
                if pair['alias'] == 'Select Alias':
                    alias_item.setData(Qt.BackgroundRole, QBrush(Qt.red))
                else:
                    alias_item.setData(Qt.BackgroundRole, QBrush(table_view.item(2, 0).background()))
                table_view.setItem(1, pair['index'], alias_item)

                # update checkboxes
                table_view.cellWidget(0, pair['index']).findChild(QCheckBox).setChecked(pair['status'])

    def okButtonPressed(self):
        table_view = self.ui.csvTableWidget
        table_model = table_view.model()

        # warn the user if the aliases are not properly set
        aliases = [table_model.data(table_model.index(1, col)) for col in range(table_model.columnCount())
                   if table_view.cellWidget(0, col).findChild(QCheckBox).isChecked()]

        if len(aliases) != len(set(aliases)) or 'Select Alias' in aliases:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText("Some aliases set were found to be duplicated or not selected!")
            msg_box.setWindowTitle("Duplicated alias")
            msg_box.setStandardButtons(QMessageBox.Ok)

            msg_box.exec()

        else:
            # get status flags and aliases from combo boxes
            pair_info = []
            for col in range(table_model.columnCount()):
                pair_info.append({'status': table_view.cellWidget(0, col).findChild(QCheckBox).isChecked(),
                                  'alias': table_model.data(table_model.index(1, col)),
                                  'index': col})

            # set the app storage
            self.application_data.csv_pair_info = pair_info

            input_alias_list = [row['Alias'] for row in self.application_data.input_table_data
                                if row['Type'] == 'Manipulated (MV)']
            output_alias_list = [row['Alias'] for row in self.application_data.output_table_data]

            # store the raw checked numbers as np array
            raw_data = []
            for row in range(2, table_view.rowCount()):
                raw_data.append([float(table_view.item(row, col).text()) for col in range(table_view.columnCount())])

            raw_np = np.asarray(raw_data)
            # raw_np = raw_np[:, [flag['status'] for flag in pair_info]]  # extract checked columns

            # find the column indexes of inputs and outputs
            input_indexes = [table_view.findItems(alias, Qt.MatchExactly)[0].column() for alias in input_alias_list]
            output_indexes = [table_view.findItems(alias, Qt.MatchExactly)[0].column() for alias in output_alias_list]

            # reorganize the data to set inputs before outputs (the order is the same as input/output table data
            reorg_data = raw_np[:, input_indexes + output_indexes].tolist()
            self.accept()

    def _checkbox_changed(self):
        chk_handle = self.sender()

        # get the column number where the checkbox was changed
        col_number = self.ui.csvTableWidget.indexAt(chk_handle.parent().pos()).column()

        # disable the column if the checkbox was unchecked
        if not chk_handle.isChecked():
            for row in range(1, self.ui.csvTableWidget.rowCount()):
                self.ui.csvTableWidget.item(row, col_number).setFlags(
                    self.ui.csvTableWidget.item(row, col_number).flags() & ~Qt.ItemIsEnabled & ~Qt.ItemIsSelectable)
        else:
            self.ui.csvTableWidget.item(1, col_number).setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
            for row in range(2, self.ui.csvTableWidget.rowCount()):
                self.ui.csvTableWidget.item(row, col_number).setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)


if __name__ == '__main__':
    import sys
    from tests_.gui.mock_data import simulation_data, input_table_data, output_table_data, expr_table_data, \
        doe_table_data

    app = QApplication(sys.argv)

    mock_storage = DataStorage()
    mock_storage.doe_data = doe_table_data
    mock_storage.simulation_data = simulation_data
    mock_storage.input_table_data = input_table_data
    mock_storage.output_table_data = output_table_data
    mock_storage.expression_table_data = expr_table_data

    pair_info_empty = []

    pair_info_scrambled = [{'status': False, 'alias': 'Select Alias', 'index': 0},
                           {'status': False, 'alias': 'Select Alias', 'index': 1},
                           {'status': True, 'alias': 'df', 'index': 2},
                           {'status': True, 'alias': 'b', 'index': 3},
                           {'status': True, 'alias': 'd',  'index': 4},
                           {'status': True, 'alias': 'rr',  'index': 5},
                           {'status': True, 'alias': 'xb', 'index': 6},
                           {'status': True, 'alias': 'qr', 'index': 7},
                           {'status': True, 'alias': 'l',  'index': 8},
                           {'status': True, 'alias': 'v',  'index': 9},
                           {'status': True, 'alias': 'f',  'index': 10},
                           {'status': True, 'alias': 'xd', 'index': 11}]

    mock_storage.csv_pair_info = pair_info_scrambled

    w = CsvEditorDialog(mock_storage)
    w.show()

    sys.exit(app.exec_())
