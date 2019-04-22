from gui.models.math_check import is_expression_valid
from py_expression_eval import Parser

alias_list_test = ['xd', 'xb', 'rr', 'df', 'j', 'vf', 'd', 'f']

expr1 = 'xd + xb*(0.02*d + 0.5*f)'  # correct
expr2 = 'bf / rr'  # wrong
expr3 = 'b ^ 2'  # wrong

print(is_expression_valid(expr1, alias_list_test))
print(is_expression_valid(expr2, alias_list_test))
print(is_expression_valid(expr3, alias_list_test))


# parser = Parser()
#
# expr1_var = parser.parse(expr1).variables()
# expr2_var = parser.parse(expr2).variables()
# expr3_var = parser.parse(expr3).variables()
#
# print(expr1_var)
# print(expr2_var)
# print(expr3_var)
#
#
# def is_expr_var_in_alias(expr, alias_list):
#     return all(item in alias_list for item in expr)
#
#
# print(is_expr_var_in_alias(expr1_var, alias_list_test))
# print(is_expr_var_in_alias(expr2_var, alias_list_test))
# print(is_expr_var_in_alias(expr3_var, alias_list_test))


