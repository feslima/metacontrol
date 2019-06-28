import numpy as np
import pandas as pd
from py_expression_eval import Parser

from tests_.mock_data import DOE_TAB_MOCK_DS

samp_data = pd.DataFrame(DOE_TAB_MOCK_DS.doe_sampled_data)
print(samp_data.head(5))

expr_table = DOE_TAB_MOCK_DS.expression_table_data
expr_names = [row['Name'] for row in expr_table]
expr_df = pd.DataFrame(columns=expr_names)

print(expr_df)

parser = Parser()

for idx, row in samp_data.iterrows():
    row_val_dict = row.to_dict()
    expr_row_values = {}
    for expr in expr_table:
        expr_to_parse = parser.parse(expr['Expr'])
        var_list = expr_to_parse.variables()
        expr_row_values[expr['Name']] = expr_to_parse.evaluate(row_val_dict)

    expr_df = expr_df.append(expr_row_values, ignore_index=True)

print(expr_df.head(10))

samp_data = samp_data.merge(expr_df, left_index=True, right_index=True)
print(samp_data.head(10))
