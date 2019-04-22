simulation_data = {'components': ['PROPANE', 'PROPENE'],
                   'therm_method': ['PENG-ROB'],
                   'blocks': ['TOWER'],
                   'streams': ['B', 'D', 'F'],
                   'reactions': [''],
                   'sens_analysis': ['S-1'],
                   'calculators': ['C-1'],
                   'optimizations': ['O-1'],
                   'design_specs': ['']}

input_table_data = [{'Path': r"\Data\Blocks\TOWER\Input\BASIS_RR", 'Alias': 'rr', 'Type': 'Manipulated (MV)'},
                    {'Path': r"\Data\Blocks\TOWER\Input\D:F", 'Alias': 'df', 'Type': 'Manipulated (MV)'}]

output_table_data = [{'Path': r"\Data\Streams\D\Output\TOT_FLOW", 'Alias': 'd', 'Type': 'Auxiliary'},
                     {'Path': r"\Data\Streams\B\Output\MOLEFRAC\MIXED\PROPENE", 'Alias': 'xb',
                      'Type': 'Candidate (CV)'},
                     {'Path': r"\Data\Streams\B\Output\TOT_FLOW", 'Alias': 'b', 'Type': 'Auxiliary'},
                     {'Path': r"\Data\Blocks\TOWER\Output\REB_DUTY", 'Alias': 'qr', 'Type': 'Auxiliary'},
                     {'Path': r"\Data\Blocks\TOWER\Output\MOLE_L1", 'Alias': 'l', 'Type': 'Auxiliary'},
                     {'Path': r"\Data\Blocks\TOWER\Output\MOLE_VN", 'Alias': 'v', 'Type': 'Auxiliary'},
                     {'Path': r"\Data\Streams\FEED\Output\TOT_FLOW", 'Alias': 'f', 'Type': 'Auxiliary'},
                     {'Path': r"\Data\Streams\D\Output\MOLEFRAC\MIXED\PROPENE", 'Alias': 'xd',
                      'Type': 'Candidate (CV)'}]

expr_table_data = [{'Name': 'lf', 'Expr': 'l / f', 'Type': 'Candidate (CV)'},
                   {'Name': 'vf', 'Expr': 'v / f', 'Type': 'Candidate (CV)'},
                   {'Name': 'c1', 'Expr': 'qr - 80', 'Type': 'Constraint function'},
                   {'Name': 'c2', 'Expr': '0.995 - xd', 'Type': 'Constraint function'},
                   {'Name': 'j', 'Expr': '-(20*d + (10 - 20*xb)*b - 70*qr)', 'Type': 'Objective function (J)'}]

doe_table_data = {'mv': [{'name': 'rr', 'lb': 7., 'ub': 25.0},
                         {'name': 'df', 'lb': 0.1, 'ub': 0.9}],
                  'lhs': {'n_samples': 50, 'n_iter': 10, 'inc_vertices': False},
                  'csv': {'active': False,
                          'filepath': r'C:\Users\Felipe\PycharmProjects\metacontrol\tests\gui\csv_editor\column.csv',
                          'check_flags': [False, False, True, True, True, True, True, True, True, True, True, True],
                          'alias_list': ['rr', 'df', 'd', 'xb', 'b', 'qr', 'l', 'v', 'f', 'xd']}
                  }

sim_file_name = r'C:\Users\Felipe\Desktop\GUI\python\infill.bkp'
