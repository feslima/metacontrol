import pathlib

import numpy as np
from PyQt5.QtCore import (QAbstractTableModel, QModelIndex,
                          QPersistentModelIndex, QStringListModel, Qt,
                          pyqtSignal)
from PyQt5.QtGui import QBrush, QColor, QFont, QIcon, QPalette, QPixmap
from PyQt5.QtWidgets import (QApplication, QCompleter, QFileDialog,
                             QHeaderView, QItemDelegate, QLineEdit,
                             QPushButton, QTableView, QWidget)

from gui.calls.base import AliasEditorDelegate, ComboBoxDelegate
from gui.calls.dialogs.simulationtree import LoadSimulationTreeDialog
from gui.models.data_storage import DataStorage
from gui.models.math_check import ValidMathStr, is_expression_valid
from gui.views.py_files.loadsimtab import Ui_Form


class DeleteButtonDelegate(QItemDelegate):
    # signals that emits the row number of the clicked button
    buttonClicked = pyqtSignal(int)

    def __init__(self, parent: QTableView):
        QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        icon = QIcon()
        icon.addPixmap(QPixmap(":/loadsim/delete_icon.svg"),
                       QIcon.Normal, QIcon.Off)

        button = QPushButton(parent)
        button.setIcon(icon)
        button.clicked.connect(self.emit_row_number)

        return button

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def emit_row_number(self):
        row_number = self.parent().indexAt(self.sender().pos()).row()
        self.buttonClicked.emit(row_number)


class ExpressionEditorDelegate(QItemDelegate):
    def __init__(self, gui_data: DataStorage, parent=None):
        QItemDelegate.__init__(self, parent)
        self.gui_data = gui_data

    def createEditor(self, parent, option, index):
        line_editor = QLineEdit(parent)
        line_editor.setAlignment(Qt.AlignCenter)

        completer = QCompleter()
        line_editor.setCompleter(completer)

        # TODO: Implement match for multivariables
        model = QStringListModel()
        completer.setModel(model)
        completer.setFilterMode(Qt.MatchContains)

        # get aliases in display and set them to the completer
        aliases_in_display = [row['Alias'] for row in
                              self.gui_data.input_table_data +
                              self.gui_data.output_table_data]

        model.setStringList(aliases_in_display)

        # insert the math validator
        exp_validator = ValidMathStr(line_editor)
        line_editor.setValidator(exp_validator)

        return line_editor

    def setEditorData(self, editor, index):
        row = index.row()
        col = index.column()
        current_text = index.data(role=Qt.DisplayRole)

        if isinstance(editor, QLineEdit):
            editor.setText(current_text)

    def setModelData(self, editor, model, index):
        text = editor.text()
        model.setData(index, text, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class ExpressionTypeDelegate(ComboBoxDelegate):
    def __init__(self, item_list=None, parent=None):
        type_list = ["Objective function (J)", "Constraint function",
                     "Candidate (CV)"]
        super().__init__(type_list, parent=parent)


class ExpressionTableModel(QAbstractTableModel):
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
        self.load_data()

    def load_data(self):
        self.layoutAboutToBeChanged.emit()
        self.expr_data = self.app_data.expression_table_data
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return len(self.expr_data)

    def columnCount(self, parent=None):
        return 4

    def insertRows(self, row: int, count: int = 1,
                   parent: QModelIndex = QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)

        # create empty rows
        new_rows = [{'Alias': 'expr_' + str(self.rowCount()),
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
        self.app_data.expression_table_data = self.expr_data
        self.app_data.expr_data_changed.emit()
        return True

    def removeRows(self, row: int, count: int = 1,
                   parent: QModelIndex = QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)

        del self.expr_data[row: (row + count)]

        self.endRemoveRows()
        self.app_data.expression_table_data = self.expr_data
        self.app_data.expr_data_changed.emit()
        return True

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == self._EXPR_DELETE_COL:
                    return "Delete"
                elif section == self._EXPR_NAME_COL:
                    return "Alias"
                elif section == self._EXPR_EXPR_COL:
                    return "Expression"
                else:
                    return "Type"

            elif orientation == Qt.Vertical:
                return str(section + 1)

            else:
                return None

        elif role == Qt.FontRole:
            if orientation == Qt.Horizontal:
                df_font = QFont()
                df_font.setBold(True)
                return df_font
            else:
                return None
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
                [row['Alias'] for row in self.expr_data]

        if role == Qt.DisplayRole:
            if col == self._EXPR_NAME_COL:
                return str(expr_data['Alias'])
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
                if aliases.count(expr_data['Alias']) > 1:
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
                if aliases.count(expr_data['Alias']) > 1:
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
            expr_data['Alias'] = value
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


class SelectedAliasesTableModel(QAbstractTableModel):
    def __init__(self, application_data: DataStorage, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.app_data = application_data
        self.headers = ['Selected alias', 'Type']
        self.load_data()

    def load_data(self):
        self.layoutAboutToBeChanged.emit()
        self.alias_data = self.app_data.input_table_data + \
            self.app_data.output_table_data
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return len(self.alias_data)

    def columnCount(self, parent=None):
        return len(self.headers)

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.headers[section]

            elif orientation == Qt.Vertical:
                return str(section + 1)

            else:
                return None

        elif role == Qt.FontRole:
            if orientation == Qt.Horizontal:
                df_font = QFont()
                df_font.setBold(True)
                return df_font
            else:
                return None
        else:
            return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        alias_data = self.alias_data[row]

        if role == Qt.DisplayRole:
            if col == 0:
                return str(alias_data['Alias'])
            elif col == 1:
                return str(alias_data['Type'])
            else:
                return None

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        else:
            return None


class SimulationInfoTableModel(QAbstractTableModel):
    def __init__(self, application_data: DataStorage, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.app_data = application_data
        self.load_data()
        self.info_headers = ['Property', 'Quantity']
        self.headers_map = {'components': "Components",
                            'therm_method': "Thermodynamic model",
                            'blocks': "Blocks",
                            'streams': "Streams",
                            'reactions': "Reactions",
                            'sens_analysis': "Sensitivity Analysis",
                            'calculators': "Calculators",
                            'optimizations': "Optimizations",
                            'design_specs': "Design Specifications"}

    def load_data(self):
        self.layoutAboutToBeChanged.emit()
        self.sim_info = self.app_data.simulation_data
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        # number of rows to present is the number of frame columns
        return self.sim_info.shape[1]

    def columnCount(self, parent=None):
        return len(self.info_headers)

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.info_headers[section]

            else:
                return None

        elif role == Qt.FontRole:
            if orientation == Qt.Horizontal:
                df_font = QFont()
                df_font.setBold(True)
                return df_font
            else:
                return None
        else:
            return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole:
            df_col = self.sim_info.columns[row]
            if col == 0:
                # first column, return df header name
                return self.headers_map[self.sim_info.columns[row]]
            else:
                # quantity column
                if df_col == 'therm_method':
                    # return thermodynamic method name
                    therm_method = self.sim_info[df_col].dropna()
                    return None if therm_method.empty else therm_method[0]
                else:
                    # return number of elements
                    if self.sim_info[df_col].isna().all():
                        # all elements are NaN
                        return "0"
                    else:
                        # return count of non nan elements
                        return str(self.sim_info[df_col].notna().sum())

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        else:
            return None


class SimulationDescriptionTableModel(SimulationInfoTableModel):
    def __init__(self, application_data: DataStorage, parent=None):
        super().__init__(application_data, parent=parent)

    def rowCount(self, parent=None):
        return self.sim_info.shape[0]

    def columnCount(self, parent=None):
        return self.sim_info.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                df_col = self.sim_info.columns[section]
                return self.headers_map[df_col]

            else:
                return None

        elif role == Qt.FontRole:
            if orientation == Qt.Horizontal:
                df_font = QFont()
                df_font.setBold(True)
                return df_font
            else:
                return None
        else:
            return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        value = self.sim_info.iat[row, col]

        if role == Qt.DisplayRole:
            if isinstance(value, str):
                return value
            else:
                return None if np.isnan(value) else str(value)

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        else:
            return None


class LoadSimTab(QWidget):

    def __init__(self, application_database: DataStorage,
                 parent_tab=None):
        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Form()
        parent_tab = parent_tab if parent_tab is not None else self
        self.ui.setupUi(parent_tab)

        # ------------------------ Internal Variables -------------------------
        self.application_database = application_database

        # ----------------------- Widget Initialization -----------------------
        expr_table = self.ui.tableViewExpressions
        expr_model = ExpressionTableModel(self.application_database,
                                          parent=expr_table)
        expr_table.setModel(expr_model)
        expr_table.setColumnWidth(expr_model._EXPR_EXPR_COL, 600)

        alias_table = self.ui.tableViewAliasDisplay
        alias_model = SelectedAliasesTableModel(self.application_database,
                                                parent=alias_table)
        alias_table.setModel(alias_model)

        sim_info_table = self.ui.tableViewSimulationInfo
        sim_info_model = SimulationInfoTableModel(self.application_database,
                                                  parent=sim_info_table)
        sim_info_table.setModel(sim_info_model)

        sim_data_table = self.ui.tableViewSimulationDescription
        sim_data_model = SimulationDescriptionTableModel(self.application_database,
                                                         parent=sim_data_table)
        sim_data_table.setModel(sim_data_model)

        alias_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        sim_info_table.horizontalHeader().setMinimumSectionSize(80)
        sim_info_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        sim_data_table.horizontalHeader().setMinimumSectionSize(80)
        sim_data_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        # set the delegates of the expression table
        self._expr_delete_delegate = DeleteButtonDelegate(parent=expr_table)
        self._expr_name_delegate = AliasEditorDelegate()

        self._expr_math_delegate = ExpressionEditorDelegate(
            self.application_database)

        self._expr_type_delegate = ExpressionTypeDelegate()

        expr_table.setItemDelegateForColumn(expr_model._EXPR_DELETE_COL,
                                            self._expr_delete_delegate)
        expr_table.setItemDelegateForColumn(expr_model._EXPR_NAME_COL,
                                            self._expr_name_delegate)
        expr_table.setItemDelegateForColumn(expr_model._EXPR_EXPR_COL,
                                            self._expr_math_delegate)
        expr_table.setItemDelegateForColumn(expr_model._EXPR_TYPE_COL,
                                            self._expr_type_delegate)

        # --------------------------- Signals/Slots ---------------------------
        # open simulation file dialog
        self.ui.buttonOpenSimFile.clicked.connect(
            self.open_simulation_file_dialog)

        # open simulation variables tree dialog
        self.ui.buttonLoadVariables.clicked.connect(
            self.open_simulation_tree_dialog)

        # update the filename text browser
        self.application_database.simulation_file_changed.connect(
            self.update_simfilepath_display)

        # inserts a new row into the expression table
        self.ui.buttonAddExpr.clicked.connect(self.insert_new_expression)

        # deteles a row from expression table
        self._expr_delete_delegate.buttonClicked.connect(
            self.delete_expression_row)

        # update models when underlying data changes
        self.application_database.alias_data_changed.connect(
            alias_model.load_data)
        self.application_database.alias_data_changed.connect(
            expr_model.load_data)

        self.application_database.simulation_info_changed.connect(
            sim_data_model.load_data)
        self.application_database.simulation_info_changed.connect(
            sim_info_model.load_data)

        self.application_database.expr_data_changed.connect(
            expr_model.load_data)

    # -------------------------------------------------------------------------
    def insert_new_expression(self):
        """Inserts a new default row into the expression table and updates the
        expression data storage.
        """
        model = self.ui.tableViewExpressions.model()
        model.insertRow(model.rowCount())

    def delete_expression_row(self, row: int):
        """Deletes the row where the delete button was clicked and updates the
        application data storage.

        Parameters
        ----------
        row : int
            Row number to be deleted.
        """
        model = self.ui.tableViewExpressions.model()
        model.removeRow(row)
        self.ui.tableViewExpressions.selectionModel().clearSelection()

    def open_simulation_file_dialog(self):
        """Prompts the user to select Aspen Plus simulation files.
        """
        homedir = pathlib.Path().home()
        sim_filename, sim_filetype = QFileDialog.getOpenFileName(
            self, "Select Aspen Plus simulation files.",
            str(homedir),
            "BKP files (*.bkp);; Input files (*.inp)"
        )

        self.application_database.simulation_file = sim_filename

    def open_simulation_tree_dialog(self):
        """Opens a new dialog where the user can select input/output variables
        from the simulation tree.
        """
        dialog = LoadSimulationTreeDialog(self.application_database)
        dialog.exec_()
        self.application_database.alias_data_changed.emit()

    def update_simfilepath_display(self):
        """Grabs the simulation file path from app_storage and displays it on
        the text browser widget.
        """
        browser = self.ui.textBrowserSimFile
        sim_file_name = self.application_database.simulation_file
        sim_file_ext = pathlib.Path(sim_file_name).suffix

        if sim_file_name == "" or \
                (sim_file_ext != ".bkp" and sim_file_ext != ".inp"):
            # user canceled the file dialog or selected an invalid file
            if browser.styleSheet() != "color: blue":
                # if there isn't an invalid path in display already
                browser.setText("Invalid or no file selected.")
                browser.setStyleSheet("color: red")

                # deactivate the load simulation tree button
                self.ui.buttonLoadVariables.setEnabled(False)

        else:
            # it's a valid file. Set its path as string and color.
            browser.setText(sim_file_name)
            browser.setStyleSheet("")

            # enable the load simulation tree button
            self.ui.buttonLoadVariables.setEnabled(True)


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook
    from tests_.mock_data import loadsim_mock

    # LOADSIM_SAMPLING_MOCK_DS = loadsim_mock()

    app = QApplication(sys.argv)
    ds = DataStorage()
    # ds = LOADSIM_SAMPLING_MOCK_DS
    w = LoadSimTab(application_database=ds)
    ds.simulation_file_changed.emit()
    w.show()

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
