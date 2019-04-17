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

        self.lb_itemdelegate = BoundEditorDelegate()
        self.ub_itemdelegate = BoundEditorDelegate()
        self.ui.tableWidgetInputVariables.setItemDelegateForColumn(1, self.lb_itemdelegate)
        self.ui.tableWidgetInputVariables.setItemDelegateForColumn(2, self.ub_itemdelegate)

        # ------------------------------ Signals/Slots ------------------------------
        self.ui.openCsvFilePushButton.clicked.connect(self.openCsvFileDialog)
        # FIXME: (16/04/2019) connect closeEditor signal of inputVariables table to update the DOE storage.

    def openCsvFileDialog(self):
        homedir = str(pathlib.Path.home())  # home directory (platform independent)
        sim_filename, _ = QFileDialog.getOpenFileName(self, "Select .csv containing DOE data", homedir,
                                                      "CSV files (*.csv)")
        if sim_filename != "":
            self.ui.lineEditCsvFilePath.setText(sim_filename)

    def loadInputVariables(self):
        # load the MV aliases in the variable table
        input_alias_data = self.application_database.getInputTableData()

        mv_alias_list = [row['Alias'] for row in input_alias_data if row['Type'] == 'Manipulated (MV)']

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

            # FIXME: (16/04/2019) read default values from data storage. If storage value is empty, set defaults 0 and 1
            table_view.setItem(row, 1, QTableWidgetItem('0.0'))
            table_view.item(row, 1).setTextAlignment(Qt.AlignCenter)
            table_view.setItem(row, 2, QTableWidgetItem('1.0'))
            table_view.item(row, 2).setTextAlignment(Qt.AlignCenter)


class BoundEditorDelegate(QItemDelegate):

    def createEditor(self, parent, option, index):
        line_editor = QLineEdit(parent)
        double_validator = QDoubleValidator(line_editor)
        line_editor.setValidator(double_validator)

        return line_editor

    def setModelData(self, editor, model, index):
        text = editor.text()

        model.setData(index, text, Qt.EditRole)

        # check if bounds are set correctly
        if float(model.data(model.index(index.row(), 1))) >= float(model.data(model.index(index.row(), 2))) or \
                float(model.data(model.index(index.row(), 2))) <= float(model.data(model.index(index.row(), 1))):
            model.setData(model.index(index.row(), 1), QBrush(Qt.red), Qt.BackgroundRole)
            model.setData(model.index(index.row(), 2), QBrush(Qt.red), Qt.BackgroundRole)
            model.parent().item(index.row(), 1).setToolTip('Lower bound must be less than upper bound!')
            model.parent().item(index.row(), 2).setToolTip('Upper bound must be greater than lower bound!')
        else:
            original_backgrd_color = editor.palette().color(editor.backgroundRole())
            model.setData(model.index(index.row(), 1), QBrush(original_backgrd_color), Qt.BackgroundRole)
            model.setData(model.index(index.row(), 2), QBrush(original_backgrd_color), Qt.BackgroundRole)
            model.parent().item(index.row(), 1).setToolTip('')
            model.parent().item(index.row(), 2).setToolTip('')

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
