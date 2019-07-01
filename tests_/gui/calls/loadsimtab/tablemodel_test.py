from PyQt5.QtCore import (QAbstractItemModel, QAbstractTableModel, QEvent,
                          QModelIndex, QPersistentModelIndex, Qt, pyqtSignal)
from PyQt5.QtGui import QBrush, QColor, QIcon, QPalette, QPixmap, QPainter
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QDialog,
                             QHeaderView, QItemDelegate, QPushButton,
                             QTableView, QStyleOptionViewItem, QStyleOptionButton, QStyle, QWidget, QStyledItemDelegate)

from gui.models.data_storage import DataStorage
from gui.models.math_check import is_expression_valid
from tests_.gui.calls.simulationtree.modeltest import Ui_Form


class deleteButtonDelegate(QItemDelegate):
    # signals that emits the row number of the clicked button
    buttonClicked = pyqtSignal(int)

    def __init__(self, parent: QTableView):
        QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        button = QPushButton(parent)
        button.setIcon(button.style().standardIcon(
            QStyle.SP_DialogCancelButton))
        button.clicked.connect(self.emit_row_number)

        return button

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def emit_row_number(self):
        row_number = self.parent().indexAt(self.sender().pos()).row()
        self.buttonClicked.emit(row_number)


class expressionTableModel(QAbstractTableModel):
    """Table model used to handle expression data display/editing.

    Parameters
    ----------
    application_data : DataStorage
        Application data storage object.
    parent : QTableView
        Parent TableView which the model will be attached.
    """
    _EXPR_DELETE_COL = 0
    _EXPR_NAME_COL = 1
    _EXPR_EXPR_COL = 2
    _EXPR_TYPE_COL = 3

    def __init__(self, application_data: DataStorage, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)
        self.app_data = application_data
        self.expr_data = self.app_data.expression_table_data

    def rowCount(self, parent=None):
        return len(self.expr_data)

    def columnCount(self, parent=None):
        return 4

    def insertRows(self, row: int, count: int = 1,
                   parent: QModelIndex = QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)

        # create empty rows
        new_rows = [{'Name': 'expr_' + str(self.rowCount()),
                     'Expr': 'Type a expression',
                     'Type': 'Choose a type'}]

        if row == 0:
            new_rows.extend(self.expr_data)
            self.expr_data = new_rows
        elif row == self.rowCount():
            self.expr_data.extend(new_rows)
        else:
            self.expr_data = self.expr_data[:row] + new_rows + \
                self.expr_data[row:]

        self.endInsertRows()
        return True

    def removeRows(self, row: int, count: int = 1,
                   parent: QModelIndex = QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)

        del self.expr_data[row: (row + count)]

        self.endRemoveRows()
        return True

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            if section == self._EXPR_DELETE_COL:
                return "Delete"
            elif section == self._EXPR_NAME_COL:
                return "Alias"
            elif section == self._EXPR_EXPR_COL:
                return "Expression"
            else:
                return "Type"
        else:
            return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        expr_data = self.expr_data[row]

        if role == Qt.BackgroundRole or role == Qt.ToolTipRole:
            aliases = [row['Alias']
                       for row in self.app_data.input_table_data +
                       self.app_data.output_table_data] + \
                [row['Name'] for row in self.expr_data]

        if role == Qt.DisplayRole:
            if col == self._EXPR_NAME_COL:
                return str(expr_data['Name'])
            elif col == self._EXPR_EXPR_COL:
                return str(expr_data['Expr'])
            elif col == self._EXPR_TYPE_COL:
                return str(expr_data['Type'])
            elif col == self._EXPR_DELETE_COL:
                # to always display the delete button
                self.parent().openPersistentEditor(self.index(row, 0))
                return None
            else:
                return None

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.BackgroundRole:
            if col == self._EXPR_NAME_COL:
                # paints red if the current expression name is already an
                # variable alias
                if aliases.count(expr_data['Name']) > 1:
                    return QBrush(Qt.red)
                else:
                    return QBrush(self.parent().palette().brush(QPalette.Base))

            elif col == self._EXPR_EXPR_COL:
                # paints red if the expression is invalid
                if is_expression_valid(expr_data['Expr'], aliases):
                    return QBrush(self.parent().palette().brush(QPalette.Base))
                else:
                    return QBrush(QColor("#f6989d"))

            elif col == self._EXPR_TYPE_COL:
                if expr_data['Type'] == 'Choose a type':
                    return QBrush(Qt.red)
                else:
                    return QBrush(self.parent().palette().brush(QPalette.Base))

            else:
                return None

        elif role == Qt.ToolTipRole:
            # tooltip strings to display
            if col == self._EXPR_NAME_COL:
                if aliases.count(expr_data['Name']) > 1:
                    return "Name already in use!"
                else:
                    return ""

            elif col == self._EXPR_EXPR_COL:
                if is_expression_valid(expr_data['Expr'], aliases):
                    return ""
                else:
                    return ("Invalid mathematical expression! "
                            "Either using a nonexistent variable or "
                            "invalid math operation.")

            else:
                return ""

        else:
            return None

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):
        if role != Qt.EditRole or not index.isValid():
            return False

        row = index.row()
        col = index.column()

        expr_data = self.expr_data[row]

        if col == self._EXPR_NAME_COL:
            expr_data['Name'] = value
        elif col == self._EXPR_EXPR_COL:
            expr_data['Expr'] = value
        elif col == self._EXPR_TYPE_COL:
            expr_data['Type'] = value
        else:
            return False

        self.app_data.expr_data_changed.emit()
        self.dataChanged.emit(index.sibling(0, 0),
                              index.sibling(self.rowCount(),
                                            self.columnCount()))
        return True

    def flags(self, index: QModelIndex):
        if index.column() != 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | ~Qt.ItemIsEditable


class testView(QDialog):
    def __init__(self, application_data: DataStorage, parent=None):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.app_data = application_data
        model = expressionTableModel(application_data=self.app_data,
                                     parent=self.ui.tableView)

        self.ui.tableView.setModel(model)
        self.ui.tableView.horizontalHeader().setStretchLastSection(True)
        self.ui.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.ui.tableView.setColumnWidth(2, 600)

        self._btn_delegate = deleteButtonDelegate(parent=self.ui.tableView)
        self._btn_delegate.buttonClicked.connect(self.del_row)
        self.ui.tableView.setItemDelegateForColumn(0, self._btn_delegate)

        self.ui.addRowPushButton.clicked.connect(self.add_new_row)
        self.ui.removeRowPushButton.clicked.connect(self.del_selected_rows)

    def add_new_row(self):
        model = self.ui.tableView.model()
        model.insertRow(model.rowCount())

    def del_selected_rows(self):
        model = self.ui.tableView.model()
        selection_model = self.ui.tableView.selectionModel()

        indexes = [QPersistentModelIndex(index)
                   for index in selection_model.selectedRows()]

        for index in indexes:
            model.removeRow(index.row())

    def del_row(self, row):
        model = self.ui.tableView.model()
        model.removeRow(row)


if __name__ == "__main__":
    import sys
    from tests_.mock_data import LOADSIM_SAMPLING_MOCK_DS

    app = QApplication(sys.argv)

    ds = LOADSIM_SAMPLING_MOCK_DS

    w = testView(application_data=ds)
    w.show()

    sys.exit(app.exec_())
