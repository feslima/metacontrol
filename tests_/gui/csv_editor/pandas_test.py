import pandas as pd
from PyQt5.QtCore import (QAbstractItemModel, QAbstractTableModel, QEvent,
                          QModelIndex, Qt, QVariant)
from PyQt5.QtGui import QBrush, QPainter, QPalette
from PyQt5.QtWidgets import (QApplication, QCheckBox, QHeaderView,
                             QItemDelegate, QStyleOptionViewItem, QTableView,
                             QWidget)

from gui.calls.base import ComboBoxDelegate

# NOTE: https://doc.qt.io/qt-5/qt.html#ItemDataRole-enum
#       https://doc.qt.io/qt-5/modelview.html
#       https://github.com/pyside/Examples/blob/master/examples/itemviews/addressbook/tablemodel.py
#       https://doc.qt.io/qt-5/qabstractitemmodel.html
#       https://doc.qt.io/qt-5/model-view-programming.html#model-subclassing-reference
#       https://stackoverflow.com/questions/44603119/how-to-display-a-pandas-data-frame-with-pyqt5/44605011


class CheckBoxDelegate(QItemDelegate):
    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        return None

    def paint(self, painter: QPainter, option: QStyleOptionViewItem,
              index: QModelIndex):
        self.drawCheck(painter, option, option.rect, Qt.Unchecked
                       if index.data(Qt.CheckStateRole) == Qt.Unchecked
                       else Qt.Checked)

    def editorEvent(self, event: QEvent, model: QAbstractItemModel,
                    option: QStyleOptionViewItem, index: QModelIndex):
        if not int(index.flags() & Qt.ItemIsEditable) > 0:
            return False

        if event.type() == QEvent.MouseButtonPress and \
                event.button() == Qt.LeftButton:
            self.setModelData(None, model, index)
            return True

        return False

    def setModelData(self, editor: QWidget, model: QAbstractItemModel,
                     index: QModelIndex):
        # change the state of the checkbox, i.e. if the current state is
        # unchecked send the value 1 to the model.setData, otherwise send 0
        model.setData(index, 1 if index.data(Qt.CheckStateRole) == Qt.Unchecked
                      else 0, Qt.EditRole)


class pandasModel(QAbstractTableModel):
    """Table model template to load pandas dataframes. The first row is where
    the user decides if it is to use extract from the dataframe through
    checkboxes.

    In the second row, the user selects which alias the column from
    the dataframe will be renamed through a combobox. This second row can only
    be defined if the checkbox in the first row is checked.

    Parameters
    ----------
    dataframe : pd.DataFrame
        The pandas dataframe to be displayed.
    pair_info : dict
        Dictionary that maps the header name of the dataframe to whether or not
        it is selected and which alias the user defined through the comboboxes.
    """
    _HEADER_ROW_OFFSET = 2

    def __init__(self, dataframe: pd.DataFrame, pair_info: dict = None,
                 parent=None):
        QAbstractTableModel.__init__(self, parent)

        self._data = dataframe

        if pair_info is None:
            # if no dictionary is defined, create a default
            pair_info = {}
            for header in self._data.columns.values:
                pair_info[header] = {'alias': 'Select alias',
                                     'status': False}

        self._pair_info = pair_info

    def rowCount(self, parent=None):
        return self._data.shape[0] + self._HEADER_ROW_OFFSET

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        row = index.row()
        col = index.column()

        pair_info_alias = self._pair_info[self._data.columns[col]]['alias']
        pair_info_status = self._pair_info[self._data.columns[col]]['status']

        df_rows, df_cols = self._data.shape

        if role == Qt.DisplayRole:
            if self._HEADER_ROW_OFFSET - 1 < row < df_rows + \
                    self._HEADER_ROW_OFFSET:
                # for rows above _HEADER_ROW_OFFSET, display the dataframe
                # values
                val = self._data.iloc[row - self._HEADER_ROW_OFFSET, col]
                if isinstance(val, float):
                    # if the value from csv is float, truncate 8 digits
                    val = "{0:.7f}".format(val)
                else:
                    val = str(val)

                return val

            elif row == 1:
                # the text will be displayed in the combo boxes
                return pair_info_alias

        elif role == Qt.CheckStateRole:
            if row == 0:
                if pair_info_status:
                    return Qt.Checked
                else:
                    return Qt.Unchecked

        elif role == Qt.BackgroundRole:
            if row == 1:
                # cell color behavior of the second row

                # get aliases that have their status true
                checked_data = [(self._pair_info[header]['alias'], col) for
                                col, header in enumerate(self._pair_info)
                                if self._pair_info[header]['status']]

                # get list of aliases that are checked
                aliases, col_num = list(zip(*checked_data)) \
                    if len(checked_data) != 0 else [[], []]

                is_duplicated = True if aliases.count(pair_info_alias) > 1 \
                    and pair_info_status else False

                if (pair_info_alias == 'Select alias' and pair_info_status) \
                        or is_duplicated:
                    return QBrush(Qt.red)
                else:
                    # original color repaint
                    return QBrush(self.parent().palette().brush(QPalette.Base))

        elif role == Qt.TextAlignmentRole:
            # Center align contents
            return Qt.AlignCenter

    def setData(self, index, value, role):
        row = index.row()
        col = index.column()

        if role == Qt.EditRole:
            if row == 0:
                self._pair_info[self._data.columns[col]]['status'] = True \
                    if value == 1 else False

                # emit the datachanged signal to update the table rows
                self.dataChanged.emit(index.sibling(row + 1, col),
                                      index.sibling(self.rowCount(), col))
                return True
            elif row == 1:
                self._pair_info[self._data.columns[col]]['alias'] = value
                return True

        return False

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            # headers names from dataframe/csv
            return self._data.columns[section]

        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            # show vertical headers only the case number
            if self._HEADER_ROW_OFFSET - 1 < section < self._data.shape[0] + \
                    self._HEADER_ROW_OFFSET:
                return self._data.index[section - self._HEADER_ROW_OFFSET]

        return None

    def flags(self, index: QModelIndex):
        row = index.row()
        col = index.column()

        if row == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | \
                Qt.ItemIsEditable
        else:
            if self._pair_info[self._data.columns[col]]['status']:
                if row == 1:
                    # enable editing so that the combobox delegate can act
                    return Qt.ItemIsEnabled | Qt.ItemIsEditable
                else:
                    return Qt.ItemIsEnabled | Qt.ItemIsSelectable
            else:
                # disable all the data rows
                return ~Qt.ItemIsEnabled | Qt.ItemIsSelectable


if __name__ == "__main__":
    import sys
    from tests_.mock_data import TESTS_FOLDER_PATH

    csv_path = TESTS_FOLDER_PATH / "gui/csv_editor/column.csv"
    app = QApplication(sys.argv)

    w = QTableView()
    w.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    w.horizontalHeader().setMinimumSectionSize(80)

    pair_info = {'Case': {'alias': 'Select alias', 'status': False},
                 'Status': {'alias': 'Select alias', 'status': False},
                 'RR': {'alias': 'rr', 'status': True},
                 'DF': {'alias': 'Select alias', 'status': False},
                 'D': {'alias': 'Select alias', 'status': False},
                 'XB': {'alias': 'Select alias', 'status': False},
                 'B': {'alias': 'Select alias', 'status': False},
                 'QR': {'alias': 'Select alias', 'status': False},
                 'L': {'alias': 'Select alias', 'status': False},
                 'V': {'alias': 'Select alias', 'status': False},
                 'F': {'alias': 'Select alias', 'status': False},
                 'XD': {'alias': 'Select alias', 'status': False}}

    pair_info_alldeact = {'B': {'alias': 'b', 'status': False},
                          'Case': {'alias': 'Select alias', 'status': False},
                          'D': {'alias': 'd', 'status': False},
                          'DF': {'alias': 'df', 'status': False},
                          'F': {'alias': 'f', 'status': False},
                          'L': {'alias': 'l', 'status': False},
                          'QR': {'alias': 'qr', 'status': False},
                          'RR': {'alias': 'rr', 'status': False},
                          'Status': {'alias': 'Select alias', 'status': False},
                          'V': {'alias': 'v', 'status': False},
                          'XB': {'alias': 'xb', 'status': False},
                          'XD': {'alias': 'xd', 'status': False}}

    pair_info_allact = {'B': {'alias': 'b', 'status': True},
                        'Case': {'alias': 'Select alias', 'status': True},
                        'D': {'alias': 'd', 'status': True},
                        'DF': {'alias': 'df', 'status': True},
                        'F': {'alias': 'f', 'status': True},
                        'L': {'alias': 'l', 'status': True},
                        'QR': {'alias': 'qr', 'status': True},
                        'RR': {'alias': 'rr', 'status': True},
                        'Status': {'alias': 'Select alias', 'status': True},
                        'V': {'alias': 'v', 'status': True},
                        'XB': {'alias': 'xb', 'status': True},
                        'XD': {'alias': 'xd', 'status': True}}
    df = pd.read_csv(csv_path)
    model = pandasModel(
        dataframe=df, pair_info=None, parent=w)

    w.setModel(model)

    check_delegate = CheckBoxDelegate()

    alias_list = ['case', 'status', 'rr', 'df',
                  'd', 'xb', 'b', 'qr', 'l', 'v', 'f', 'xd']
    combo_delegate = ComboBoxDelegate(item_list=alias_list)

    w.setItemDelegateForRow(0, check_delegate)
    w.setItemDelegateForRow(1, combo_delegate)

    w.show()

    sys.exit(app.exec_())
