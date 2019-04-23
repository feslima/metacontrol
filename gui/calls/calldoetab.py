import pathlib
from PyQt5.QtWidgets import QApplication, QWidget, QHeaderView, QFileDialog, QTableWidgetItem, QItemDelegate, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QBrush

from gui.views.py_files.doetab import Ui_Form
from gui.calls.callsamplingassistant import SamplingAssistantDialog
from gui.models.data_storage import DataStorage
from gui.calls.callcsveditor import CsvEditorDialog


class DoeTab(QWidget):
    def __init__(self, application_database: DataStorage, parent_widget=None):
        # ------------------------------ Form Initialization ----------------------------
        super().__init__()
        self.ui = Ui_Form()
        parent_widget = parent_widget if parent_widget is not None else self
        self.ui.setupUi(parent_widget)

        self.application_database = application_database

        # ------------------------------ WidgetInitialization ------------------------------
        self.ui.tableWidgetInputVariables.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tableWidgetResultsDoe.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self._lb_itemdelegate = BoundEditorDelegate()
        self._ub_itemdelegate = BoundEditorDelegate()
        self.ui.tableWidgetInputVariables.setItemDelegateForColumn(1, self._lb_itemdelegate)
        self.ui.tableWidgetInputVariables.setItemDelegateForColumn(2, self._ub_itemdelegate)

        # ------------------------------ Signals/Slots ------------------------------
        self.application_database.doeDataChanged.connect(self.loadInputVariables)
        self.application_database.inputAliasDataChanged.connect(self.loadResultsTable)
        self.application_database.outputAliasDataChanged.connect(self.loadResultsTable)
        self.application_database.exprDataChanged.connect(self.loadResultsTable)
        self.ui.openCsvFilePushButton.clicked.connect(self.openCsvFileDialog)
        self._lb_itemdelegate.closeEditor.connect(self.updateDoeStorage)
        self._ub_itemdelegate.closeEditor.connect(self.updateDoeStorage)
        self.ui.openSamplerPushButton.clicked.connect(self.openSamplingAssistant)
        self.ui.csvEditorRadioButton.toggled['bool'].connect(self.updateDoeCsvStorage)
        self.ui.csvEditorPushButton.clicked.connect(self.openCsvEditorDialog)

        # ------------------------------ Internal variables ------------------------------
        self._doe_results_table = None

    def openSamplingAssistant(self):
        samp_dialog = SamplingAssistantDialog(self.application_database)

        if samp_dialog.exec_():
            self.application_database.sampled_data = samp_dialog.sampled_data

    def openCsvFileDialog(self):
        homedir = str(pathlib.Path.home())  # home directory (platform independent)
        csv_filename, _ = QFileDialog.getOpenFileName(self, "Select .csv containing DOE data", homedir,
                                                      "CSV files (*.csv)")
        if csv_filename != "":
            self.ui.lineEditCsvFilePath.setText(csv_filename)
            # enable the CSV Editor button
            self.ui.csvEditorPushButton.setEnabled(True)

            csv_doe_data = self.application_database.doe_data['csv']
            csv_doe_data['filepath'] = csv_filename

    def openCsvEditorDialog(self):
        alias_list = [entry['Alias'] for entry in self.application_database.input_table_data
                      if entry['Type'] == 'Manipulated (MV)'] + \
            [entry['Alias'] for entry in self.application_database.output_table_data]

        csv_editor_dialog = CsvEditorDialog(self.ui.lineEditCsvFilePath.text(), alias_list)
        csv_editor_dialog.exec_()

    def loadInputVariables(self):
        # load the MV aliases into the variable table
        mv_alias_data = self.application_database.doe_data

        mv_alias_list, lb_list, ub_list = zip(*[row.values() for row in mv_alias_data['mv']])

        table_view = self.ui.tableWidgetInputVariables

        # clear the table rows
        table_view.setRowCount(0)

        # insert the aliases and validators
        for row in range(len(mv_alias_list)):
            table_view.insertRow(row)
            alias_item = QTableWidgetItem(mv_alias_list[row])
            alias_item.setTextAlignment(Qt.AlignCenter)
            alias_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # disable the edit

            table_view.setItem(row, 0, alias_item)

            table_view.setItem(row, 1, QTableWidgetItem(str(lb_list[row])))
            table_view.item(row, 1).setTextAlignment(Qt.AlignCenter)
            table_view.setItem(row, 2, QTableWidgetItem(str(ub_list[row])))
            table_view.item(row, 2).setTextAlignment(Qt.AlignCenter)

        self.inputTableCheck()

    def loadResultsTable(self):
        # load the headers
        results_table_view = self.ui.tableWidgetResultsDoe
        input_alias_list = [row['Alias'] for row in self.application_database.input_table_data
                            if row['Type'] == 'Manipulated (MV)']
        output_alias_list = [row['Alias'] for row in self.application_database.output_table_data]

        expr_list = [row['Name'] for row in self.application_database.expression_table_data]

        # clear the table
        results_table_view.setColumnCount(0)
        results_table_view.setRowCount(0)

        # place the headers in the first and second rows
        results_table_view.setRowCount(2)
        results_table_view.setColumnCount(len(input_alias_list + output_alias_list + expr_list))
        results_table_view.setSpan(0, 0, 1, len(input_alias_list))
        results_table_view.setItem(0, 0, QTableWidgetItem('Inputs'))
        results_table_view.item(0, 0).setTextAlignment(Qt.AlignCenter)
        results_table_view.setSpan(0, 2, 1, len(output_alias_list + expr_list))
        results_table_view.setItem(0, 2, QTableWidgetItem('Outputs'))
        results_table_view.item(0, 2).setTextAlignment(Qt.AlignCenter)

        # place the subheaders (alias) in the second row
        all_alias = input_alias_list + output_alias_list + expr_list
        for j in range(len(all_alias)):
            item_place_holder = QTableWidgetItem(all_alias[j])
            results_table_view.setItem(1, j, item_place_holder)
            item_place_holder.setTextAlignment(Qt.AlignCenter)

        if self._doe_results_table is not None:
            results_table_view.setRowCount(self._doe_results_table.shape[0] + 2)  # expand the rows

            for row in range(self._doe_results_table.shape[0]):
                for col in range(self._doe_results_table.shape[1]):
                    item_place_holder = QTableWidgetItem(str(self._doe_results_table[row, col]))
                    results_table_view.setItem(2 + row, col, item_place_holder)
                    item_place_holder.setTextAlignment(Qt.AlignCenter)

        # results_table_view.setHorizontalHeaderLabels(alias_list + expr_list)

    # check the input variables table
    def inputTableCheck(self):
        table_view = self.ui.tableWidgetInputVariables

        lb_list = []
        ub_list = []
        flag_list = []
        for row in range(table_view.rowCount()):
            lb_list.append(float(table_view.item(row, 1).text()))
            ub_list.append(float(table_view.item(row, 2).text()))
            flag_list.append(lb_list[row] < ub_list[row])

        is_bound_set = all(flag_list)

        if is_bound_set:  # paint/repaint cells

            org_color = table_view.palette().color(table_view.backgroundRole())

            for row in range(table_view.rowCount()):
                table_view.model().setData(table_view.model().index(row, 1), QBrush(org_color), Qt.BackgroundRole)
                table_view.model().setData(table_view.model().index(row, 2), QBrush(org_color), Qt.BackgroundRole)
        else:
            row_to_paint = [idx for idx, e in enumerate(flag_list) if e is False]
            for row in row_to_paint:
                table_view.model().setData(table_view.model().index(row, 1), QBrush(Qt.red), Qt.BackgroundRole)
                table_view.model().setData(table_view.model().index(row, 2), QBrush(Qt.red), Qt.BackgroundRole)

    # update the doe data storage
    def updateDoeStorage(self):
        table_view = self.ui.tableWidgetInputVariables
        mv_bound_info = []
        for row in range(table_view.rowCount()):
            mv_bound_info.append({'name': table_view.item(row, 0).text(),
                                  'lb': table_view.item(row, 1).text(),
                                  'ub': table_view.item(row, 2).text()})

        current_doe_data = self.application_database.doe_data

        current_doe_data['mv'] = mv_bound_info

        self.application_database.doe_data = current_doe_data

    def updateDoeCsvStorage(self):
        csv_doe_data = self.application_database.doe_data['csv']

        csv_doe_data['active'] = True if self.ui.csvEditorRadioButton.isChecked() else False


class BoundEditorDelegate(QItemDelegate):

    def createEditor(self, parent, option, index):
        line_editor = QLineEdit(parent)
        double_validator = QDoubleValidator(line_editor)
        line_editor.setValidator(double_validator)

        return line_editor

    def setModelData(self, editor, model, index):
        text = editor.text()

        model.setData(index, text, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


if __name__ == "__main__":
    import sys
    from gui.models.data_storage import DataStorage
    from tests_.gui.mock_data import simulation_data, input_table_data, output_table_data, expr_table_data, \
        doe_table_data

    app = QApplication(sys.argv)

    mock_storage = DataStorage()
    mock_storage.doe_data = doe_table_data
    mock_storage.simulation_data = simulation_data
    mock_storage.input_table_data = input_table_data
    mock_storage.output_table_data = output_table_data
    mock_storage.expression_table_data = expr_table_data

    w = DoeTab(mock_storage)
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
