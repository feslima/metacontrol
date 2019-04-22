import csv
import numpy as np
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QCheckBox, QHBoxLayout, QWidget, QItemDelegate, \
    QComboBox, QMessageBox, QHeaderView
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QBrush

from gui.views.py_files.csv_editor import Ui_Dialog
from gui.models.data_storage import DataStorage


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
    def __init__(self, csv_filepath, alias_list):
        # ---------------------- dialog initialization ----------------------
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Window)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowState(Qt.WindowMaximized)

        # ---------------------- connections ----------------------
        self.ui.okPushButton.clicked.connect(self.okButtonPressed)

        # ---------------------- table initialization ----------------------
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

            # checkbox for first row of table
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

            # combo_box delegate for second row (alias setting)
            self.ui.csvTableWidget.setItem(1, j, QTableWidgetItem('Select Alias'))
            self.ui.csvTableWidget.item(1, j).setTextAlignment(Qt.AlignCenter)
            self.ui.csvTableWidget.item(1, j).setData(Qt.BackgroundRole, QBrush(Qt.red))
            self._combobox_delegates_dict[str(j)] = ComboBoxDelegate(alias_list)
            self.ui.csvTableWidget.setItemDelegateForRow(1, self._combobox_delegates_dict[str(j)])

            # insert the values
            for i in range(data_values.shape[0]):
                value_item = QTableWidgetItem(str(data_values[i, j]))
                value_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                value_item.setTextAlignment(Qt.AlignCenter)
                self.ui.csvTableWidget.setItem(2 + i, j, value_item)

        # column width adjustments
        self.ui.csvTableWidget.horizontalHeader().setMinimumSectionSize(80)
        self.ui.csvTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.csvTableWidget.horizontalHeader().setStretchLastSection(True)

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
            # TODO: (22/04/2019) Think about a proper way to store the selected columns names-checkflags pairs in the
            #   mtc extension.

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
    mock_storage.setDoeData(doe_table_data)
    mock_storage.setSimulationDataDictionary(simulation_data)
    mock_storage.setInputTableData(input_table_data)
    mock_storage.setOutputTableData(output_table_data)
    mock_storage.setExpressionTableData(expr_table_data)

    alias_list = [entry['Alias'] for entry in mock_storage.getInputTableData()
                  if entry['Type'] == 'Manipulated (MV)'] + \
                 [entry['Alias'] for entry in mock_storage.getOutputTableData()]

    csv_test = r"C:\Users\Felipe\csv_test.csv"
    # csv_test = mock_storage.getDoeData()['csv']['filepath']
    w = CsvEditorDialog(csv_test, alias_list)
    w.show()

    sys.exit(app.exec_())
