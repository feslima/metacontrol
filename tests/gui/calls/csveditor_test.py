from PyQt5.QtWidgets import QApplication
from gui.calls.callcsveditor import CsvEditorDialog

if __name__ == '__main__':
    import sys
    import pathlib
    import csv
    import qdarkstyle

    base_path = pathlib.Path(__file__).parent.parent
    file_path = base_path / "csv_editor/cumene_csv.csv"

    alias_list_test = ['Select Alias', 'xd', 'xb', 'rr', 'df', 'j', 'vf', 'd', 'f']

    app = QApplication(sys.argv)

    w = CsvEditorDialog(file_path, alias_list_test)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

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
