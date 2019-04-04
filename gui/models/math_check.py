from PyQt5.QtGui import QValidator
from py_expression_eval import Parser


class ValidMathStr(QValidator):
    def __init__(self, parent=None):
        QValidator.__init__(self, parent)
        self.parser = Parser()

    def validate(self, string, pos):
        # print('validate(): ', type(string), type(pos), string, pos)
        try:
            self.parser.parse(string)
            self.parent().setStyleSheet('QLineEdit { background-color: #c4df9b; }')  # green
            return QValidator.Acceptable, string, pos
        except Exception:
            self.parent().setStyleSheet('QLineEdit { background-color: #f6989d; }')  # red
            return QValidator.Intermediate, string, pos
