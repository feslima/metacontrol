from PyQt5.QtGui import QValidator
from py_expression_eval import Parser


class ValidMathStr(QValidator):
    def __init__(self, parent=None):
        QValidator.__init__(self, parent)
        self.parser = Parser()

    def validate(self, string, pos):
        try:
            self.parser.parse(string)
            self.parent().setStyleSheet('border: 3px solid green')  # green
            return QValidator.Acceptable, string, pos
        except Exception:
            self.parent().setStyleSheet('border: 3px solid red')  # red
            return QValidator.Intermediate, string, pos


def is_expression_valid(expression):
    parser = Parser()

    try:
        parser.parse(expression)
        return True
    except Exception:
        return False
