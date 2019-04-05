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


def is_expression_valid(expression, alias_list):
    """
    Check if a mathematical string expression is valid by attempting to parse it and checking if all the variables in it
    exist in the aliases list

    Parameters
    ----------
    expression : str
        String containing mathematical expression
    alias_list : list
        List of strings containing all the aliases in display

    Returns
    -------
    bool
        True for valid expression, otherwise its false.
    """
    parser = Parser()

    try:
        expr_var = parser.parse(expression).variables()
        return all(item in alias_list for item in expr_var)
    except Exception:
        return False
