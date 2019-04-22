import re

from tests_.gui.math_parser.math_parser import Ui_Dialog
from PyQt5.QtWidgets import QDialog, QApplication

from gui.models.math_check import ValidMathStr


class ParserDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.validator = ValidMathStr(self.ui.lineEdit)
        self.ui.lineEdit.setValidator(self.validator)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = ParserDialog()
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


def is_balanced(expression):
    """
    Checks if string expression containing only parenthesis is balanced (matching).

    Parameters
    ----------
    expression : str
        Expression string
    """

    opening = '('
    closing = ')'

    mapping = dict(zip(opening, closing))
    queue = []

    for letter in expression:
        if letter in opening:
            queue.append(mapping[letter])
        elif letter in closing:
            if not queue or letter != queue.pop():
                return False
    return not queue


def get_par_from_str(expression):
    """
    Extracts all parentheses from expression.

    Parameters
    ----------
    expression : str
        String expression to extract parentheses.

    Returns
    -------
    str
       String containing all parentheses in expression.

    """
    # get opening and closing parentheses indexes
    open_par_ocurrences = [open_par.start() for open_par in re.finditer(r'\(', expression)]
    close_par_ocurrences = [open_par.start() for open_par in re.finditer(r'\)', expression)]

    # concatenate and sort their positions
    par_ocurrences = open_par_ocurrences + close_par_ocurrences
    par_ocurrences.sort()

    return ''.join([expression[par_idx] for par_idx in par_ocurrences])