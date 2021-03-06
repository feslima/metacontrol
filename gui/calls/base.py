import sys
import traceback

from PyQt5.QtCore import QAbstractItemModel, QEvent, QModelIndex, QRegExp, Qt
from PyQt5.QtGui import (QBrush, QDoubleValidator, QIntValidator, QPainter,
                         QRegExpValidator)
from PyQt5.QtWidgets import (QComboBox, QItemDelegate, QLineEdit, QMessageBox,
                             QSizePolicy, QSpacerItem, QStyleOptionViewItem,
                             QTextEdit, QWidget)


class DoubleEditorDelegate(QItemDelegate):
    """Base item delegate for inserting double values throughout application.

    """

    def createEditor(self, parent, option, index):
        line_editor = QLineEdit(parent)
        line_editor.setAlignment(Qt.AlignCenter)
        double_validator = QDoubleValidator(parent=line_editor)
        line_editor.setValidator(double_validator)

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


class IntegerEditorDelegate(QItemDelegate):
    """Base item delegate for inserting integer values throughout application.
    """

    def createEditor(self, parent, option, index):
        line_editor = QLineEdit(parent)
        line_editor.setAlignment(Qt.AlignCenter)
        int_validator = QIntValidator(parent=line_editor)
        line_editor.setValidator(int_validator)

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

    def setEditorData(self, editor, index):
        # Sets the data to be displayed and edited by the editor from the data
        # model item specified by the model index.
        current_text = index.data(role=Qt.DisplayRole)

        if isinstance(editor, QComboBox):
            combo_index = editor.findData(current_text, role=Qt.DisplayRole)

            editor.setCurrentIndex(combo_index)
        pass

    def setModelData(self, combo_box, model, index):
        # Gets data from the editor widget and stores it in the specified model
        # at the item index.
        value = combo_box.itemText(combo_box.currentIndex())

        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        # Updates the editor for the item specified by index according to the
        # style option given.
        editor.setGeometry(option.rect)


class CheckBoxDelegate(QItemDelegate):
    """Base class used to create checbox delegates to be placed inside table
    models.
    """

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


class ErrorMessageBox(QMessageBox):
    def __init__(self, icon, title, text, buttons, parent, flags):
        super().__init__(icon, title, text, buttons, parent, flags)

    def resizeEvent(self, a0):
        result = super().resizeEvent(a0)

        details_box = self.findChild(QTextEdit)

        if details_box is not None:
            details_box.setFixedSize(details_box.sizeHint())

        return result


def warn_the_user(msg_text: str, msg_title: str) -> None:
    """Function to display warnings to the user.

    Parameters
    ----------
    msg_text : str
        Text body of the message dialog to be displayed.
    msg_title : str
        Title of the message dialog.
    """
    msg_box = QMessageBox(
        QMessageBox.Warning,
        msg_title,
        msg_text,
        buttons=QMessageBox.Ok,
        parent=None
    )
    msg_box.exec_()


class CustomErrorMessageBox(ErrorMessageBox):
    def __init__(self, icon, title, text, buttons, parent, flags, width):
        super().__init__(icon, title, text, buttons, parent, flags)
        self.fixed_width = width

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        self.setFixedWidth(self.fixed_width)


def my_exception_hook(exctype, value, tback):
    """Exception hook to catch exceptions from PyQt and show the error message
    as a dialog box.
    """
    str_error_msg = ''.join(traceback.format_exception(exctype, value, tback))

    # Show the dialog
    error_dialog = CustomErrorMessageBox(
        QMessageBox.Critical,
        "Application ERROR!",
        str_error_msg,
        QMessageBox.NoButton, None,
        Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint,
        600
    )

    error_dialog.exec_()

    # Call the normal Exception hook after
    sys.__excepthook__(exctype, value, tback)
