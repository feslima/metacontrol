from PyQt5.QtCore import (QAbstractItemModel, QAbstractTableModel, QModelIndex,
                          QPersistentModelIndex, QRegExp, Qt)
from PyQt5.QtGui import QBrush, QPalette, QRegExpValidator
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QDialog,
                             QHeaderView, QItemDelegate, QLineEdit, QTableView,
                             QComboBox)

from gui.models.data_storage import DataStorage
from tests_.gui.calls.simulationtree.modeltest import Ui_Form


class AliasEditorDelegate(QItemDelegate):
    """Item delegate for line edit widgets used in alias definitions in tables
    through out the application.

    Parameters
    ----------
    max_characters : int (optional)
        Maximum number of characters allowed in the editor.
        Default max of 10 characters.
    """

    def __init__(self, max_characters: int = 10, parent=None):
        QItemDelegate.__init__(self, parent)
        self.max_char = max_characters

    def createEditor(self, parent, option, index):
        line_editor = QLineEdit(parent)
        reg_ex = QRegExp(
            "^[a-z$][a-z_$0-9]{{,{0}}}$".format(self.max_char - 1))
        input_validator = QRegExpValidator(reg_ex, line_editor)
        line_editor.setValidator(input_validator)

        return line_editor

    def setModelData(self, editor, model, index):
        text = editor.text()

        model.setData(index, text, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class ComboBoxDelegate(QItemDelegate):
    """Base class for combo box item delegates to use throughout the
    application.

    Parameters
    ----------
    item_list : list
        List of items (strings) to be displayed in the combo box popup menu.
    """

    def __init__(self, item_list: list, parent=None):
        QItemDelegate.__init__(self, parent)
        self.item_list = item_list

    def createEditor(self, parent, option, index):
        # Returns the widget used to edit the item specified by index for
        # editing. The parent widget and style option are used to control how
        # the editor widget appears.
        combo_box = QComboBox(parent)

        combo_box.addItems(self.item_list)
        return combo_box

    def setEditorData(self, combo_box, index):
        # Sets the data to be displayed and edited by the editor from the data
        # model item specified by the model index.
        combo_box.showPopup()

    def setModelData(self, combo_box, model, index):
        # Gets data from the editor widget and stores it in the specified model
        # at the item index.
        value = combo_box.itemText(combo_box.currentIndex())

        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        # Updates the editor for the item specified by index according to the
        # style option given.
        editor.setGeometry(option.rect)


class variableTableModel(QAbstractTableModel):
    """Table model used to manipulate input/output definitions of variables
    chosen through the variable trees.

    Parameters
    ----------
    application_data : DataStorage
        Application data storage object.
    mode : str {'input', 'output'}
        Which mode the table should assume for the type of variables.
        Default is 'input'
    """

    def __init__(self, application_data: DataStorage, mode: str = 'input',
                 parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.app_data = application_data
        if mode == 'input':
            self.variable_data = self.app_data.input_table_data
            self.data_changed_signal = self.app_data.input_alias_data_changed
        elif mode == 'output':
            self.variable_data = self.app_data.output_table_data
            self.data_changed_signal = self.app_data.output_alias_data_changed
        else:
            raise ValueError("Invalid table mode.")

    def rowCount(self, parent=None):
        return len(self.variable_data)

    def columnCount(self, parent=None):
        return 3

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if index.isValid():
            row = index.row()
            col = index.column()

            if role == Qt.DisplayRole:
                if col == 0:
                    return str(self.variable_data[row]['Path'])
                elif col == 1:
                    return str(self.variable_data[row]['Alias'])
                else:
                    return str(self.variable_data[row]['Type'])

            if role == Qt.TextAlignmentRole:
                if col >= 1:
                    return Qt.AlignCenter

            if role == Qt.BackgroundRole:
                if col == 1:
                    # paints red if duplicates are found between input/output
                    aliases = [row['Alias']
                               for row in self.app_data.input_table_data +
                               self.app_data.output_table_data]

                    if aliases.count(self.variable_data[row]['Alias']) > 1:
                        return QBrush(Qt.red)
                    else:
                        return QBrush(self.parent().palette().brush(
                            QPalette.Base))

                if col == 2:
                    if self.variable_data[row]['Type'] == 'Choose a type':
                        return QBrush(Qt.red)
                    else:
                        return QBrush(self.parent().palette().brush(
                            QPalette.Base))

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):
        if role != Qt.EditRole:
            return False

        if index.isValid():
            row = index.row()
            col = index.column()

            if col == 0:
                self.variable_data[row]['Path'] = value
            elif col == 1:
                self.variable_data[row]['Alias'] = value
            elif col == 2:
                self.variable_data[row]['Type'] = value
            else:
                return False

            self.data_changed_signal.emit()
            self.dataChanged.emit(index.sibling(0, col),
                                  index.sibling(self.rowCount(), col))
            return True

        return False

    def insertRows(self, row: int, count: int = 1,
                   parent: QModelIndex = QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        # create the empty rows
        new_rows = [{'Path': '', 'Alias': 'alias_' + str(self.rowCount()),
                     'Type': 'Choose a type'} for i in range(count)]
        if row == 0:
            # prepend rows
            new_rows.extend(self.variable_data)
            self.variable_data = new_rows
        elif row == self.rowCount():
            # append rows
            self.variable_data.extend(new_rows)
        else:
            self.variable_data = self.variable_data[:row] + new_rows + \
                self.variable_data[row:]

        self.endInsertRows()
        return True

    def removeRows(self, row: int, count: int = 1,
                   parent: QModelIndex = QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)

        del self.variable_data[row: (row + count)]

        self.endRemoveRows()
        return True

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    return "Variable path"
                elif section == 1:
                    return "Alias"
                else:
                    return "Type"

    def flags(self, index: QModelIndex):

        row = index.row()
        col = index.column()

        if col == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | ~Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable


class testView(QDialog):
    def __init__(self, application_data: DataStorage, parent=None):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        # self.setWindowFlags(Qt.Window)

        self.ui.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableView.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.app_data = application_data

        model = variableTableModel(self.app_data, parent=self.ui.tableView)

        self.ui.tableView.setModel(model)

        # delegates
        input_combo_list = ["Manipulated (MV)", "Disturbance (d)", "Auxiliary"]
        self._input_alias_delegate = AliasEditorDelegate(max_characters=13)
        self._input_combo_delegate = ComboBoxDelegate(input_combo_list)

        self.ui.tableView.setItemDelegateForColumn(1,
                                                   self._input_alias_delegate)
        self.ui.tableView.setItemDelegateForColumn(2,
                                                   self._input_combo_delegate)

        # ------------------------------ signals ------------------------------
        self.ui.addRowPushButton.clicked.connect(self.add_new_row)
        self.ui.removeRowPushButton.clicked.connect(self.del_selected_row)

    def add_new_row(self):
        model = self.ui.tableView.model()

        model.insertRow(model.rowCount())

        model.setData(model.index(model.rowCount() - 1, 0),
                      'TestPAth', Qt.EditRole)

    def del_selected_row(self):
        table_model = self.ui.tableView.model()
        selection_model = self.ui.tableView.selectionModel()
        indexes = [QPersistentModelIndex(index)
                   for index in selection_model.selectedRows()]

        for index in indexes:
            table_model.removeRow(index.row())
            self.ui.tableView.clearSelection()


if __name__ == "__main__":
    import sys
    from tests_.mock_data import LOADSIM_SAMPLING_MOCK_DS

    app = QApplication(sys.argv)

    ds = LOADSIM_SAMPLING_MOCK_DS
    w = testView(application_data=ds)

    w.show()

    sys.exit(app.exec_())
