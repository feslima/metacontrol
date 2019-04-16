from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import QObject, pyqtSignal


class DataStorage(QObject):
    """
    Application data storage. This is for reuse of application data such as tree models, simulation data, aliases,
    expressions, etc.

    For tables, initialize and store empty tables as empty list.
    For forms, dictionaries must be initialized and empty stored with empty strings as values.
    """

    # signals
    aliasDataChanged = pyqtSignal()
    exprDataChanged = pyqtSignal()

    # FIXME: Fix structure storage for empty (remove None initialization) application and non-empty.
    def __init__(self):
        super().__init__()
        self._input_tree_model = QStandardItemModel()
        self._output_tree_model = QStandardItemModel()
        self._simulation_data = {'components': '',
                                 'therm_method': [''],
                                 'blocks': '',
                                 'streams': '',
                                 'reactions': '',
                                 'sens_analysis': '',
                                 'calculators': '',
                                 'optimizations': '',
                                 'design_specs': ''}
        self._input_table_data = []
        self._output_table_data = []
        self._expression_table_data = []
        self._doe_data = {'lb': [''],
                          'ub': [''],
                          'lhs': {'n_samples': '', 'n_iter': '', 'inc_vertices': False},
                          'csv': {'active': True,
                                  'filepath': '',
                                  'check_flags': [False],
                                  'alias_index': ['']}}

    def getInputTreeModel(self):
        return self._input_tree_model

    def setInputTreeModel(self, tree_model):

        if isinstance(tree_model, QStandardItemModel):
            self._input_tree_model = tree_model
        else:
            raise TypeError("Input must be a QStandardItemModel class object.")

    def getOutputTreeModel(self):
        return self._output_tree_model

    def setOutputTreeModel(self, tree_model):

        if isinstance(tree_model, QStandardItemModel):
            self._output_tree_model = tree_model
        else:
            raise TypeError("Input must be a QStandardItemModel class object.")

    def getSimulationDataDictionary(self):
        return self._simulation_data

    def setSimulationDataDictionary(self, simulation_dictionary):

        if isinstance(simulation_dictionary, dict):
            self._simulation_data = simulation_dictionary
        else:
            raise TypeError("Input must be a dictionary object.")

    def getInputTableData(self):
        return self._input_table_data

    def setInputTableData(self, table_model):

        if isinstance(table_model, list):
            self._input_table_data = table_model
            self.aliasDataChanged.emit()
        else:
            raise TypeError("Input must be a list.")

    def getOutputTableData(self):
        return self._output_table_data

    def setOutputTableData(self, table_model):

        if isinstance(table_model, list):
            self._output_table_data = table_model
            self.aliasDataChanged.emit()
        else:
            raise TypeError("Input must be a list.")

    def getExpressionTableData(self):
        return self._expression_table_data

    def setExpressionTableData(self, expression_data):

        if isinstance(expression_data, list):
            self._expression_table_data = expression_data
            self.exprDataChanged.emit()
        else:
            raise TypeError("Input must be a list.")

    def getDoeData(self):
        return self._doe_data

    def setDoeData(self, doe_data):

        if isinstance(doe_data, dict):
            self._doe_data = doe_data
        else:
            raise TypeError("Input must be a dictionary object.")


def write_data(output_file_path, sim_file_path, gui_data_storage):
    """
    Writes custom template of .mtc file based on the current instance of the application.

    Parameters
    ----------
    output_file_path: str
        Output file path string to where the user wants the file to be stored.
    sim_file_path: str
        File path of simulation file (e.g. .bkp, .hsc, etc.) currently in use.
    gui_data_storage : DataStorage
        Application data storage object. This is the source of info to write.
    """
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


def read_data(mtc_file_path, gui_data_storage):
    import re

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
                'optimizations': lambda_re_fun('OPTIMIZATIONS'),
                'design_specs': lambda_re_fun('DESIGN SPECS')}

    # check if the fields are empty and replace them properly
    sim_info = {key: ('' if isinstance(value, list) and value[0] == '' and key != 'therm_method' else value)
                for key, value in sim_info.items()}

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
    if len(input_alias_list) == 1 and input_alias_list[0] == '':  # list of single element and the element is ''
        pass
    else:
        for row in range(len(input_alias_list)):
            inpt_table_var.append({'Path': input_path_list[row],
                                   'Alias': input_alias_list[row],
                                   'Type': input_type_list[row]})

    outpt_table_var = []
    if len(output_alias_list) == 1 and output_alias_list[0] == '':
        pass
    else:
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
    if len(expr_name_list) == 1 and expr_name_list[0] == '':  # list of single element and the element is ''
        pass
    else:
        for row in range(len(expr_name_list)):
            expr_table.append({'Name': expr_name_list[row],
                               'Expr': expr_str_list[row],
                               'Type': expr_type_list[row]})

    gui_data_storage.setExpressionTableData(expr_table)

    # -------------------------- SAMPLING --------------------------
    # TODO: (14/04/2019) Implement sampling (DOE) tab load data.

    return sim_file_name
