from tests_.gui.math_parser.math_autocomplete import Ui_Dialog
from PyQt5.QtWidgets import QApplication, QDialog, QCompleter
from PyQt5.QtCore import QStringListModel


class AutoCompleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # get all listwidget items
        items = []
        for index in range(self.ui.listWidget.count()):
            items.append(self.ui.listWidget.item(index).text())

        # set the completer
        completer = QCompleter()
        self.ui.lineEdit.setCompleter(completer)

        # set the model completer
        model = QStringListModel()
        completer.setModel(model)
        model.setStringList(items)  # populate de string completer


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = AutoCompleteDialog()
    w.show()


    def my_exception_hook(exctype, value, tback):
        # Print the error and traceback
        print(exctype, value, tback)
        # Call the normal Exception hook after
        sys.__excepthook__(exctype, value, tback)
        sys.exit()

        # Back up the reference to the exceptionhook


    sys._excepthook = sys.excepthook

    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook

    sys.exit(app.exec_())
