from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import QObject, pyqtSignal

import numpy as np

# FIXME: (23/04/2019) Find a proper way to store the sampled data to be implemented on samplingassistant and csveditor.

class DataStorage(QObject):
    """
    Application data storage. This is for reuse of application data such as tree models, simulation data, aliases,
    expressions, etc.

    For tables, initialize and store empty tables as empty list.
    For forms, dictionaries must be initialized and empty stored with empty strings as values.
    """

    # signals
    inputAliasDataChanged = pyqtSignal()
    outputAliasDataChanged = pyqtSignal()
    exprDataChanged = pyqtSignal()
    doeMvDataChanged = pyqtSignal()
    doeLhsDataChanged = pyqtSignal()
    doeCsvDataChanged = pyqtSignal()
    doeSampledDataChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._rigorous_model_file_path = ''
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
        self._doe_data = {'mv': [],
                          'lhs': {'n_samples': '', 'n_iter': '', 'inc_vertices': False},
                          'csv': {'active': True,
                                  'filepath': '',
                                  'pair_info': []},
                          'sampled': {'input_index': [],
                                      'constraint_index': [],
                                      'objective_index': [],
                                      'convergence_flag': [],
                                      'data': []}
                          }

    @property
    def rigorous_model_filepath(self):
        return self._rigorous_model_file_path

    @rigorous_model_filepath.setter
    def rigorous_model_filepath(self, filepath):
        if isinstance(filepath, str):
            self._rigorous_model_file_path = filepath
        else:
            raise TypeError('Rigorous model filepath must be a string.')

    @property
    def input_tree_model(self):
        return self._input_tree_model

    @input_tree_model.setter
    def input_tree_model(self, tree_model):

        if isinstance(tree_model, QStandardItemModel):
            self._input_tree_model = tree_model
        else:
            raise TypeError("Input must be a QStandardItemModel class object.")

    @property
    def output_tree_model(self):
        return self._output_tree_model

    @output_tree_model.setter
    def output_tree_model(self, tree_model):

        if isinstance(tree_model, QStandardItemModel):
            self._output_tree_model = tree_model
        else:
            raise TypeError("Input must be a QStandardItemModel class object.")

    @property
    def simulation_data(self):
        return self._simulation_data

    @ simulation_data.setter
    def simulation_data(self, simulation_dictionary):

        if isinstance(simulation_dictionary, dict):
            self._simulation_data = simulation_dictionary
        else:
            raise TypeError("Input must be a dictionary object.")

    @property
    def input_table_data(self):
        return self._input_table_data

    @input_table_data.setter
    def input_table_data(self, table_model):

        if isinstance(table_model, list):
            self._input_table_data = table_model

            # NOTE: this update is to ensure that the doe MV's are in conformity with alias inputs that are MV's
            # update mvs in doe data
            mv_input_list = [row['Alias'] for row in table_model if row['Type'] == 'Manipulated (MV)']
            mv_doe_list = [entry['name'] for entry in self._doe_data['mv']]

            # delete items from doe list that are not present in input list (this is for sanitation purposes)
            doe_to_remove = [doe for doe in mv_doe_list if doe not in mv_input_list]
            for k in doe_to_remove:
                [self._doe_data['mv'].pop(idx) for idx, entry in enumerate(self._doe_data['mv']) if
                 entry['name'] == k]

            # add items from input list that are not present in doe
            doe_to_insert = [inp for inp in mv_input_list if inp not in mv_doe_list]
            for k in doe_to_insert:
                self._doe_data['mv'].append({'name': k, 'lb': 0.0, 'ub': 1.0})
            self.inputAliasDataChanged.emit()

            if len(doe_to_remove) != 0 or len(doe_to_insert) != 0:
                # if there were changes in doe_data mvs, notify other objects
                self.doeMvDataChanged.emit()
        else:
            raise TypeError("Input must be a list.")

    @property
    def output_table_data(self):
        return self._output_table_data

    @output_table_data.setter
    def output_table_data(self, table_model):

        if isinstance(table_model, list):
            self._output_table_data = table_model
            self.outputAliasDataChanged.emit()
        else:
            raise TypeError("Input must be a list.")

    @property
    def expression_table_data(self):
        return self._expression_table_data

    @expression_table_data.setter
    def expression_table_data(self, expression_data):

        if isinstance(expression_data, list):
            self._expression_table_data = expression_data
            self.exprDataChanged.emit()
        else:
            raise TypeError("Input must be a list.")

    @property
    def doe_data(self):  # This property is read only (no setter)
        return self._doe_data

    @property
    def doe_mv_data(self):
        return self._doe_data['mv']

    @doe_mv_data.setter
    def doe_mv_data(self, mv_data):
        if isinstance(mv_data, list):
            self._doe_data['mv'] = mv_data
            self.doeMvDataChanged.emit()
        else:
            raise TypeError("Input must be a list")

    @property
    def doe_lhs_data(self):
        return self._doe_data['lhs']

    @doe_lhs_data.setter
    def doe_lhs_data(self, lhs_data):
        if isinstance(lhs_data, dict):
            self._doe_data['lhs'] = lhs_data
            self.doeLhsDataChanged.emit()
        else:
            raise TypeError("Input must be a dictionary object.")

    @property
    def doe_csv_data(self):
        return self._doe_data['csv']

    @doe_csv_data.setter
    def doe_csv_data(self, csv_data):
        if isinstance(csv_data, dict):
            self._doe_data['csv'] = csv_data
        else:
            raise TypeError('Input must be a dictionary object.')

    @property
    def doe_sampled_data(self):
        return self._doe_data['sampled']

    @doe_sampled_data.setter
    def doe_sampled_data(self, sampled_data_dict):
        # first element of each sublist (first column of array) must be flags for convergence
        if isinstance(sampled_data_dict, dict):
            self._doe_data['sampled'] = sampled_data_dict
            self.doeSampledDataChanged.emit()
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
    sim_info = gui_data_storage.simulation_data
    input_table_var = gui_data_storage.input_table_data
    output_table_var = gui_data_storage.output_table_data
    expr_table = gui_data_storage.expression_table_data
    doe_table = gui_data_storage.doe_data

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
    MVS:
        NAMES: {names}
        LOWER BOUNDS: {lower_bounds}
        UPPER BOUNDS: {upper_bounds}
    LHS:
        NUMBER OF SAMPLES: {n_samples}
        NUMBER OF ITERATIONS: {n_iter_lhs}
        INCLUDE VERTICES: {inc_vertices}
    CSV:
        ACTIVE: {csv_active}
        FILENAME: {csv_filename}
        PAIR INFO:
            ALIAS: {csv_pair_alias}
            STATUS: {csv_pair_status}
            INDEX: {csv_pair_index}
        SAMPLED:
            INPUT INDEX:
            CONSTRAINT INDEX:
            OBJECTIVE INDEX:
            CONVERGENCE FLAG:
            DATA:
""".format(
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
        names='|'.join([entry['name'] for entry in doe_table['mv']]),
        lower_bounds='|'.join([str(entry['lb']) for entry in doe_table['mv']]),
        upper_bounds='|'.join([str(entry['ub']) for entry in doe_table['mv']]),
        n_samples=doe_table['lhs']['n_samples'], n_iter_lhs=doe_table['lhs']['n_iter'],
        inc_vertices=doe_table['lhs']['inc_vertices'], csv_active=doe_table['csv']['active'],
        csv_filename=doe_table['csv']['filepath'],
        csv_pair_alias='|'.join([entry['alias'] for entry in doe_table['csv']['pair_info']]),
        csv_pair_status='|'.join([str(entry['status']) for entry in doe_table['csv']['pair_info']]),
        csv_pair_index='|'.join([str(entry['index'])for entry in doe_table['csv']['pair_info']])
    )

    with open(output_file_path, 'w') as file:
        file.write(template_str)


def read_data(mtc_file_path, gui_data_storage: DataStorage):
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

    gui_data_storage.simulation_data = sim_info

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

    gui_data_storage.blockSignals(True)
    gui_data_storage.input_table_data = inpt_table_var
    gui_data_storage.blockSignals(False)

    gui_data_storage.output_table_data = outpt_table_var

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

    gui_data_storage.expression_table_data = expr_table

    # -------------------------- SAMPLING --------------------------
    samp_raw_str_block = re.search('// SAMPLING //\n(.*\n*)', mtc_str, flags=re.DOTALL)
    samp_mv_raw_str_block = re.search('MVS:\n(.*\n*)LHS:', samp_raw_str_block.group(1), flags=re.DOTALL)
    samp_mv_alias_list = re.search('NAMES: (.*)\n', samp_mv_raw_str_block.group(1)).group(1).split('|')
    samp_mv_lb_list = re.search('LOWER BOUNDS: (.*)\n', samp_mv_raw_str_block.group(1)).group(1).split('|')
    samp_mv_ub_list = re.search('UPPER BOUNDS: (.*)\n', samp_mv_raw_str_block.group(1)).group(1).split('|')

    mv_info = []
    if len(samp_mv_alias_list) == 1 and samp_mv_alias_list[0] == '':
        pass
    else:
        for idx, mv in enumerate(samp_mv_alias_list):
            mv_info.append({'name': mv, 'lb': float(samp_mv_lb_list[idx]), 'ub': float(samp_mv_ub_list[idx])})

    samp_lhs_raw_str_block = re.search('LHS:\n(.*\n*)CSV:', samp_raw_str_block.group(1), flags=re.DOTALL)
    lhs_n_samples = int(re.search('NUMBER OF SAMPLES: (.*)\n', samp_lhs_raw_str_block.group(1)).group(1))
    lhs_n_iter = int(re.search('NUMBER OF ITERATIONS: (.*)\n', samp_lhs_raw_str_block.group(1)).group(1))
    lhs_inc_vert = 'True' == re.search('INCLUDE VERTICES: (.*)\n', samp_lhs_raw_str_block.group(1)).group(1)

    lhs_info = {'n_samples': lhs_n_samples, 'n_iter': lhs_n_iter, 'inc_vertices': lhs_inc_vert}

    samp_csv_raw_str_block = re.search('CSV:\n(.*\n*)', samp_raw_str_block.group(1), flags=re.DOTALL)
    csv_active = 'True' == re.search('ACTIVE: (.*)\n', samp_csv_raw_str_block.group(1)).group(1)
    csv_filepath = re.search('FILENAME: (.*)\n', samp_csv_raw_str_block.group(1)).group(1)

    csv_pair_raw_str_block = re.search('PAIR INFO:\n(.*\n*)', samp_csv_raw_str_block.group(1), flags=re.DOTALL)
    csv_pair_info_alias = re.search('ALIAS: (.*)\n', csv_pair_raw_str_block.group(1)).group(1).split('|')
    csv_pair_info_status = re.search('STATUS: (.*)\n', csv_pair_raw_str_block.group(1)).group(1).split('|')
    csv_pair_info_index = re.search('INDEX: (.*)\n', csv_pair_raw_str_block.group(1)).group(1).split('|')

    csv_pair_info = []
    if len(csv_pair_info_alias) == 1 and csv_pair_info_alias[0] == '':
        pass
    else:
        for row in range(len(csv_pair_info_alias)):
            csv_pair_info.append({'alias': csv_pair_info_alias[row],
                                  'status': 'True' == csv_pair_info_status[row],
                                  'index': int(csv_pair_info_index[row])})

    csv_info = {'active': csv_active,
                'filepath': csv_filepath,
                'pair_info': csv_pair_info}

    doe_table = {'mv': mv_info,
                 'lhs': lhs_info,
                 'csv': csv_info}

    gui_data_storage.doe_data = doe_table

    return sim_file_name
