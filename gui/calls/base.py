import sys
import traceback

from PyQt5.QtCore import QAbstractItemModel, QEvent, QModelIndex, QRegExp, Qt
from PyQt5.QtGui import QBrush, QDoubleValidator, QPainter, QRegExpValidator
from PyQt5.QtWidgets import (QComboBox, QItemDelegate, QLineEdit, QMessageBox,
                             QSizePolicy, QSpacerItem, QStyleOptionViewItem,
                             QWidget, QTextEdit)

# TODO: Check entire alias column for duplicates and implement behavior for the
# entire column instead of only the current cell.


class DoubleEditorDelegate(QItemDelegate):
    """Base item delegate for inserting double values throughout application.

    """

    def createEditor(self, parent, option, index):
        line_editor = QLineEdit(parent)
        double_validator = QDoubleValidator(parent=line_editor)
        line_editor.setValidator(double_validator)

        return line_editor

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
    alias_item_model : QAbstractItemModel (optional)
        If the user wants to compare the current aliases in table against
        another list of aliases, he just needs to provide a list of strings
        containing the aliases to be compared besides the ones in parent table.

    """

    def __init__(self, max_characters: int = 10,
                 alias_item_model: QAbstractItemModel = None,
                 parent=None):
        QItemDelegate.__init__(self, parent)
        self.max_char = max_characters
        self.alias_item_model = alias_item_model

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

        # check if the alias is duplicated
        current_aliases = [model.data(model.index(row, index.column()))
                           for row in range(model.rowCount())]

        if current_aliases.count(text) > 1:
            # duplicated alias found, set the background color to red
            model.setData(index, QBrush(Qt.red), Qt.BackgroundRole)
        else:
            # no duplicate found. Ensure the background color to be the same as
            # the model view behind the item delegate
            orig_back_color = editor.palette().color(editor.backgroundRole())
            model.setData(index, QBrush(orig_back_color), Qt.BackgroundRole)

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

        # paints the cell background back to original color
        orig_bck_color = combo_box.palette().color(combo_box.backgroundRole())
        model.setData(index, QBrush(orig_bck_color), Qt.BackgroundRole)

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


def my_exception_hook(exctype, value, tback):
    """Exception hook to catch exceptions from PyQt and show the error message
    as a dialog box.
    """
    # Show the dialog
    error_dialog = ErrorMessageBox(QMessageBox.Critical, "Application ERROR!",
                                   traceback.format_exception(
                                       exctype, value, tback)[-1],
                                   QMessageBox.NoButton, None,
                                   Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)

    error_dialog.setDetailedText(
        ''.join(traceback.format_exception(exctype, value, tback)))

    error_dialog.exec_()

    # Call the normal Exception hook after
    sys.__excepthook__(exctype, value, tback)
