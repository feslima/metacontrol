import pathlib
from PyQt5.QtWidgets import QApplication, QWidget, QHeaderView, QFileDialog, QTableWidgetItem, QItemDelegate, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QBrush

from gui.views.py_files.doetab import Ui_Form


class DoeTab(QWidget):
    def __init__(self, application_database, parent_widget=None):
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
        self.ui.openCsvFilePushButton.clicked.connect(self.openCsvFileDialog)
        self._lb_itemdelegate.closeEditor.connect(self.updateDoeStorage)
        self._ub_itemdelegate.closeEditor.connect(self.updateDoeStorage)

    def openCsvFileDialog(self):
        homedir = str(pathlib.Path.home())  # home directory (platform independent)
        sim_filename, _ = QFileDialog.getOpenFileName(self, "Select .csv containing DOE data", homedir,
                                                      "CSV files (*.csv)")
        if sim_filename != "":
            self.ui.lineEditCsvFilePath.setText(sim_filename)

    def loadInputVariables(self):
        # load the MV aliases into the variable table
        mv_alias_data = self.application_database.getDoeData()

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

        if is_bound_set:  # activate or deactivate the gen lhs button and paint/repaint cells
            self.ui.genLhsPushButton.setEnabled(True)

            org_color = table_view.palette().color(table_view.backgroundRole())

            for row in range(table_view.rowCount()):
                table_view.model().setData(table_view.model().index(row, 1), QBrush(org_color), Qt.BackgroundRole)
                table_view.model().setData(table_view.model().index(row, 2), QBrush(org_color), Qt.BackgroundRole)
        else:
            row_to_paint = [idx for idx, e in enumerate(flag_list) if e is False]
            for row in row_to_paint:
                table_view.model().setData(table_view.model().index(row, 1), QBrush(Qt.red), Qt.BackgroundRole)
                table_view.model().setData(table_view.model().index(row, 2), QBrush(Qt.red), Qt.BackgroundRole)
            self.ui.genLhsPushButton.setEnabled(False)

    # update the doe data storage
    def updateDoeStorage(self):
        table_view = self.ui.tableWidgetInputVariables
        mv_bound_info = []
        for row in range(table_view.rowCount()):
            mv_bound_info.append({'name': table_view.item(row, 0).text(),
                                  'lb': table_view.item(row, 1).text(),
                                  'ub': table_view.item(row, 2).text()})

        current_doe_data = self.application_database.getDoeData()

        current_doe_data['mv'] = mv_bound_info

        self.application_database.setDoeData(current_doe_data)


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

    app = QApplication(sys.argv)
    w = DoeTab(DataStorage())
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
