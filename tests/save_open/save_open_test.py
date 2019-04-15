import pathlib
from gui.models.data_storage import DataStorage

mock = DataStorage()
simulation_data = {'components': ['PROPANE', 'PROPENE'],
                   'therm_method': ['PENG-ROB'],
                   'blocks': ['TOWER'],
                   'streams': ['B', 'D', 'F'],
                   'reactions': [''],
                   'sens_analysis': ['S-1'],
                   'calculators': ['C-1'],
                   'optimizations': ['O-1'],
                   'design_specs': ['']}

input_table_data = [{'Path': r"\Data\Blocks\TOWER\Output\MOLE_RR", 'Alias': 'rr', 'Type': 'Manipulated (MV)'},
                    {'Path': r"\Data\Blocks\TOWER\Output\MOLE_DFR", 'Alias': 'df', 'Type': 'Manipulated (MV)'}]

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

doe_table_data = {'lb': [7., 0.1],
                  'ub': [25., 0.9],
                  'lhs': {'n_samples': 50, 'n_iter': 100, 'inc_vertices': False},
                  'csv': {'active': True,
                          'filepath': r'C:\Users\Felipe\PycharmProjects\metacontrol\tests\gui\csv_editor\column.csv',
                          'check_flags': [False, False, True, True, True, True, True, True, True, True, True, True],
                          'alias_index': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}}

mock.setSimulationDataDictionary(simulation_data)
mock.setInputTableData(input_table_data)
mock.setOutputTableData(output_table_data)
mock.setExpressionTableData(expr_table_data)
mock.setDoeData(doe_table_data)

sim_file_name = r'C:\Users\Felipe\Desktop\GUI\python\infill.bkp'
out_file = pathlib.Path(__file__).parent / "test_file.mtc"


def write_data(output_file_path, sim_file_path, gui_data_storage):
    sim_info = gui_data_storage.getSimulationDataDictionary()
    input_table_var = gui_data_storage.getInputTableData()
    output_table_var = gui_data_storage.getOutputTableData()
    expr_table = gui_data_storage.getExpressionTableData()
    doe_table = gui_data_storage.getDoeData()

    template_str = """// LOAD SIMULATION //
SIM FILENAME: {sim_filename}

SIM INFO:
    COMPONENTS: {components}
    THERMODEL: {therm_model}
    BLOCKS: {blocks}
    STREAMS: {streams}
    REACTIONS: {reactions}
    SENSITIVITY ANALYSIS: {sens_analysis}
    CALCULATORS: {calculators}
    OPTIMIZATIONS: {optimizations}
    DESIGN SPECS: {des_specs}

PWC VARIABLES:
    INPUT:
        ALIAS: {aliases_input}
        PATH: {paths_input}
        TYPE: {types_input}
    OUTPUT:
        ALIAS: {aliases_output}
        PATH: {paths_output}
        TYPE: {types_output}

USER EXPRESSIONS:
    NAME: {expr_names}
    EXPR: {expr_str}
    TYPE: {expr_types}

// SAMPLING //
INPUT SETTINGS:
    LOWER BOUNDS: {lower_bounds}
    UPPER BOUNDS: {upper_bounds}
    LHS:
        NUMBER OF SAMPLES: {n_samples}
        NUMBER OF ITERATIONS: {n_iter_lhs}
        INCLUDE VERTICES: {inc_vertices}
    CSV:
        ACTIVE: {csv_active}
        FILENAME: {csv_filename}
        CHECK FLAGS: {csv_check_flags}
        ALIAS INDEX: {csv_alias_index}""".format(
        sim_filename=sim_file_path, components='|'.join(sim_info['components']),
        therm_model=sim_info['therm_method'][0], blocks='|'.join(sim_info['blocks']),
        streams='|'.join(sim_info['streams']), reactions='|'.join(sim_info['reactions']),
        sens_analysis='|'.join(sim_info['sens_analysis']), calculators='|'.join(sim_info['calculators']),
        optimizations='|'.join(sim_info['optimizations']), des_specs='|'.join(sim_info['design_specs']),
        aliases_input='|'.join([entry['Alias'] for entry in input_table_var]),
        paths_input='|'.join([entry['Path'] for entry in input_table_var]),
        types_input='|'.join([entry['Type'] for entry in input_table_var]),
        aliases_output='|'.join([entry['Alias'] for entry in output_table_var]),
        paths_output='|'.join([entry['Path'] for entry in output_table_var]),
        types_output='|'.join([entry['Type'] for entry in output_table_var]),
        expr_names='|'.join([entry['Name'] for entry in expr_table]),
        expr_str='|'.join([entry['Expr'] for entry in expr_table]),
        expr_types='|'.join([entry['Type'] for entry in expr_table]),
        lower_bounds='|'.join((map(str, doe_table['lb']))),
        upper_bounds='|'.join((map(str, doe_table['ub']))),
        n_samples=doe_table['lhs']['n_samples'], n_iter_lhs=doe_table['lhs']['n_iter'],
        inc_vertices=doe_table['lhs']['inc_vertices'], csv_active=doe_table['csv']['active'],
        csv_filename=doe_table['csv']['filepath'],
        csv_check_flags='|'.join(map(str, doe_table['csv']['check_flags'])),
        csv_alias_index='|'.join(map(str, doe_table['csv']['alias_index']))
    )

    with open(output_file_path, 'w') as file:
        file.write(template_str)


def read_data(mtc_file_path):
    import re
    from gui.models.data_storage import DataStorage

    # Initialize the data storage
    gui_data_storage = DataStorage()

    # read the file
    with open(mtc_file_path, 'r') as fp:
        mtc_str = fp.read()

    # -------------------------- bkp file name --------------------------
    sim_file_name = re.search('SIM FILENAME: (.*)\n', mtc_str).group(1)

    # -------------------------- simulation info data --------------------------
    sim_raw_str_block = re.search('SIM INFO:\n(.*\n*)PWC VARIABLES:', mtc_str, flags=re.DOTALL)
    lambda_re_fun = lambda x: re.search('{0}: (.*)\n'.format(x), sim_raw_str_block.group(1)).group(1).split('|')
    sim_info = {'components': lambda_re_fun('COMPONENTS'),
                'therm_method': lambda_re_fun('THERMODEL'),
                'blocks': lambda_re_fun('BLOCKS'),
                'streams': lambda_re_fun('STREAMS'),
                'reactions': lambda_re_fun('REACTIONS'),
                'sens_analysis': lambda_re_fun('SENSITIVITY ANALYSIS'),
                'calculators': lambda_re_fun('CALCULATORS'),
                'optimizations': lambda_re_fun('CALCULATORS'),
                'design_specs': lambda_re_fun('DESIGN SPECS')}

    gui_data_storage.setSimulationDataDictionary(sim_info)

    # -------------------------- variables (alias + path) info data --------------------------
    pwc_var_raw_str_block = re.search('PWC VARIABLES:\n(.*\n*)USER EXPRESSIONS:', mtc_str, flags=re.DOTALL)
    var_input_raw_str_block = re.search('INPUT:\n(.*\n*)OUTPUT:', pwc_var_raw_str_block.group(1), flags=re.DOTALL)
    var_output_raw_str_block = re.search('OUTPUT:\n(.*\n*)', pwc_var_raw_str_block.group(1), flags=re.DOTALL)
    input_alias_list = re.search('ALIAS: (.*)\n', var_input_raw_str_block.group(1)).group(1).split('|')
    input_path_list = re.search('PATH: (.*)\n', var_input_raw_str_block.group(1)).group(1).split('|')
    input_type_list = re.search('TYPE: (.*)\n', var_input_raw_str_block.group(1)).group(1).split('|')

    output_alias_list = re.search('ALIAS: (.*)\n', var_output_raw_str_block.group(1)).group(1).split('|')
    output_path_list = re.search('PATH: (.*)\n', var_output_raw_str_block.group(1)).group(1).split('|')
    output_type_list = re.search('TYPE: (.*)\n', var_output_raw_str_block.group(1)).group(1).split('|')

    inpt_table_var = []
    for row in range(len(input_alias_list)):
        inpt_table_var.append({'Path': input_path_list[row],
                               'Alias': input_alias_list[row],
                               'Type': input_type_list[row]})

    outpt_table_var = []
    for row in range(len(output_alias_list)):
        outpt_table_var.append({'Path': output_path_list[row],
                                'Alias': output_alias_list[row],
                                'Type': output_type_list[row]})

    gui_data_storage.setInputTableData(inpt_table_var)
    gui_data_storage.setOutputTableData(outpt_table_var)

    # -------------------------- expression table data --------------------------
    expr_raw_str_data = re.search('USER EXPRESSIONS:\n(.*\n*)// SAMPLING //', mtc_str, flags=re.DOTALL)
    expr_name_list = re.search('NAME: (.*)\n', expr_raw_str_data.group(1)).group(1).split('|')
    expr_str_list = re.search('EXPR: (.*)\n', expr_raw_str_data.group(1)).group(1).split('|')
    expr_type_list = re.search('TYPE: (.*)\n', expr_raw_str_data.group(1)).group(1).split('|')

    expr_table = []
    for row in range(len(expr_name_list)):
        expr_table.append({'Name': expr_name_list[row],
                           'Expr': expr_str_list[row],
                           'Type': expr_type_list[row]})

    gui_data_storage.setExpressionTableData(expr_table)

    # -------------------------- SAMPLING --------------------------
    # TODO: (14/04/2019) Implement sampling (DOE) tab load data.


# write_data(out_file, sim_file_name, mock)
read_data(out_file)
