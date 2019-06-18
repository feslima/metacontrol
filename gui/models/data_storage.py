import pathlib
import json
from PyQt5.QtCore import QObject, pyqtSignal


class DataStorage(QObject):
    """Application data storage. This is for reuse of application data such as
    tree models, simulation data, aliases,
    expressions, etc.

    For tables, initialize and store empty tables as empty list.
    For forms, dictionaries must be initialized and empty stored with empty
    strings as values.
    """

    # signals to be fired when an attribute changes
    inputAliasDataChanged = pyqtSignal()
    outputAliasDataChanged = pyqtSignal()
    exprDataChanged = pyqtSignal()
    doeMvBoundsChanged = pyqtSignal()
    doeSampledDataChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._simulation_file = ''
        self._tree_model_input = {}
        self._tree_model_output = {}
        self._simulation_data = {'components': [''],
                                 'therm_method': [''],
                                 'blocks': [''],
                                 'streams': [''],
                                 'reactions': [''],
                                 'sens_analysis': [''],
                                 'calculators': [''],
                                 'optimizations': [''],
                                 'design_specs': ['']}
        self._input_table_data = []
        self._output_table_data = []
        self._expression_table_data = []
        self._doe_data = {'mv_bounds': [],
                          'lhs': {'n_samples': '',
                                  'n_iter': '',
                                  'inc_vertices': False},
                          'csv': {'active': True,
                                  'filepath': '',
                                  'pair_info': []},
                          'sampled': {'input_index': [],
                                      'constraint_index': [],
                                      'objective_index': [],
                                      'convergence_flag': [],
                                      'data': []}
                          }

    # ------------------------------ PROPERTIES ------------------------------
    @property
    def simulation_file(self):
        """The absolute path string to the simulation file.
        """
        return self._simulation_file

    @simulation_file.setter
    def simulation_file(self, filepath: str):
        if isinstance(filepath, str):
            if pathlib.Path(filepath).is_file() or filepath == '':
                self._simulation_file = filepath
            else:
                raise FileNotFoundError("{0} is not a valid file path."
                                        .format(filepath))
        else:
            raise TypeError('Simulation file path must be a string.')

    @property
    def tree_model_input(self):
        """Input variable tree model of the simulation. JSON compatible
        dictionary.
        """
        return self._tree_model_input

    @tree_model_input.setter
    def tree_model_input(self, value: dict):
        if isinstance(value, dict):
            self._tree_model_input = value
        else:
            raise TypeError("Input tree model must be a dict.")

    @property
    def tree_model_output(self):
        """Output variable tree model of the simulation. JSON compatible
        dictionary.
        """
        return self._tree_model_output

    @tree_model_output.setter
    def tree_model_output(self, value: dict):
        if isinstance(value, dict):
            self._tree_model_output = value
        else:
            raise TypeError("Output tree model must be a dict.")

    @property
    def simulation_data(self):
        """Dictionary containing the following keys -- values pairs:
            'components'    --  Components in simulation (list);
            'therm_method'  --  Thermodynamic model set in simulation (list);
            'blocks'        --  Blocks in simulation (list);
            'streams'       --  Streams in simulation (list);
            'reactions'     --  Reactions in simulation (list);
            'sens_analysis' --  Sensitivity analysis in simulation (list);
            'calculators'   --  Calculators in simulation (list);
            'optimizations' --  Optimizations in simulation (list);
            'design_specs'  --  Design Specifications in simulation (list);
        """
        return self._simulation_data

    @simulation_data.setter
    def simulation_data(self, dictionary: dict):
        if isinstance(dictionary, dict):
            # check if the keys are properly set.
            key_list = ['components', 'therm_method', 'blocks', 'streams',
                        'reactions', 'sens_analysis', 'calculators',
                        'optimizations', 'design_specs']

            self._check_keys(key_list, dictionary, self._simulation_data)
        else:
            raise KeyError("Simulation data must be a dictionary object.")

    @property
    def input_table_data(self):
        """List of dicts containing the input variables aliases, paths and
        types. Keys are: 'Alias', 'Path', 'Type'."""
        return self._input_table_data

    @input_table_data.setter
    def input_table_data(self, table_model: list):
        if isinstance(table_model, list):
            self._input_table_data = table_model

            # NOTE: this update is to ensure that the doe MV's are in
            # conformity with alias inputs that are MV's.
            mv_input_list = [row['Alias']
                             for row in table_model if
                             row['Type'] == 'Manipulated (MV)']
            mv_doe_list = [entry['name']
                           for entry in self._doe_data['mv_bounds']]

            # TODO: Implement list comparison in doe_mv_data setter from
            # https://stackoverflow.com/a/9845430. Check if the current is
            # different from the one to be inserted to emit the mv bound
            # changed signal.

            # delete items from doe list that are not present in input list
            # (this is for sanitation purposes)
            doe_to_remove = [
                doe for doe in mv_doe_list if doe not in mv_input_list]
            for k in doe_to_remove:
                [self._doe_data['mv_bounds'].pop(idx) for idx, entry in
                 enumerate(self._doe_data['mv_bounds']) if
                 entry['name'] == k]

            # add items from input list that are not present in doe
            doe_to_insert = [
                inp for inp in mv_input_list if inp not in mv_doe_list]
            for k in doe_to_insert:
                self._doe_data['mv_bounds'].append(
                    {'name': k, 'lb': 0.0, 'ub': 1.0})
            self.inputAliasDataChanged.emit()

            if len(doe_to_remove) != 0 or len(doe_to_insert) != 0:
                # if there were changes in doe_data mvs, notify other objects
                self.doeMvBoundsChanged.emit()
        else:
            raise TypeError("Input table data must be a list.")

    @property
    def output_table_data(self):
        """List of dicts containing the output variables aliases, paths and
        types. Keys are: 'Alias', 'Path', 'Type'."""
        return self._output_table_data

    @output_table_data.setter
    def output_table_data(self, value: list):
        if isinstance(value, list):
            self._output_table_data = value
            self.outputAliasDataChanged.emit()
        else:
            raise TypeError("Output table data must be a list.")

    @property
    def expression_table_data(self):
        """List of dicts containing the expressions names, equations and
        types. Keys are: 'Name', 'Expr', 'Type'."""
        return self._expression_table_data

    @expression_table_data.setter
    def expression_table_data(self, value: list):
        if isinstance(value, list):
            self._expression_table_data = value
            self.exprDataChanged.emit()
        else:
            raise TypeError("Expression table data must be a list.")

    @property
    def doe_mv_bounds(self):
        """List of dicts containing the MVs and its bounds to be displayed
        or modified in doetab. Keys are: 'name', 'lb', 'ub'."""
        return self._doe_data['mv_bounds']

    @doe_mv_bounds.setter
    def doe_mv_bounds(self, value: list):
        if isinstance(value, list):
            self._doe_data['mv_bounds'] = value
            self.doeMvBoundsChanged.emit()
        else:
            raise TypeError("MV bounds table data must be a list.")

    @property
    def doe_lhs_data(self):
        """LHS info (dict) to read/write into LHS settings dialog.
        Keys are: 'n_samples', 'n_iter', 'inc_vertices'."""
        return self._doe_data['lhs']

    @doe_lhs_data.setter
    def doe_lhs_data(self, value: dict):
        if isinstance(value, dict):
            key_list = ['n_samples', 'n_iter', 'inc_vertices']
            self._check_keys(key_list, value, self._doe_data['lhs'])
        else:
            raise KeyError("LHS info data must be a dictionary object.")

    # ---------------------------- PRIVATE METHODS ---------------------------
    def _check_keys(self, key_list: list, value_dict: dict, prop: dict) \
            -> None:
        """Check if all the keys in `key_list` are present in `value_dict`. If
        so, the `prop` dict is updated with the values from `value_dict`.
        Otherwise, a KeyError exception is thrown.

        Parameters
        ----------
        key_list : list
            List containing the keys to be checked against.

        value_dict : dict
            Dictionary containing the new values to be updated.
        prop : dict
            Dictionary currently stored in the class that will be updated.
        """
        if all(k in value_dict for k in key_list):
            prop.update(value_dict)
        else:
            raise KeyError("All the following keys must be specified: " +
                           str(key_list))

    # ---------------------------- PUBLIC METHODS ----------------------------
    def save(self, output_path: str) -> None:
        """Saves the current data storage in a .mtc file.

        Parameters
        ----------
        output_path : str
            Output file path string to where the user wants the file to be
            stored.
        """
        # prepare the data to be dumped
        # primary keys corresponding to each tab/dialog attribute
        # secondary keys = attributes of DataStorage class

        # primary key list:
        #   - 'simulation_info': loadsimtab (implemented)
        #   - 'doe_info': doetab (partially implemented)
        #   - 'metacontrol_info' : metacontroltab (NOT implemented)
        app_data = {
            'simulation_info': {
                'sim_filename': self.simulation_file,
                'sim_info': self.simulation_data,
                'sim_tree_input': self.tree_model_input,
                'sim_tree_output': self.tree_model_output,
                'mtc_input_table': self.input_table_data,
                'mtc_output_table': self.output_table_data,
                'mtc_expr_table': self.expression_table_data,
                },
            'doe_info': {
                'mtc_mv_bounds': self.doe_mv_bounds
            }
        }

        # perfom the JSON dump
        with open(output_path, 'w') as mtc_file:
            json.dump(app_data, mtc_file)

    def load(self, mtc_filepath: str) -> None:
        """Reads .mtc file data and updates the object attributes.

        Parameters
        ----------
        mtc_filepath : str
            Filepath to the .mtc file to be read.
        """
        # load the JSON file
        with open(mtc_filepath, 'r') as mtc_file:
            app_data = json.load(mtc_file)

        sim_info = app_data['simulation_info']
        doe_info = app_data['doe_info']

        # loadsimtab
        self.simulation_file = sim_info['sim_filename']
        self.simulation_data = sim_info['sim_info']
        self.tree_model_input = sim_info['sim_tree_input']
        self.tree_model_output = sim_info['sim_tree_output']
        self.input_table_data = sim_info['mtc_input_table']
        self.output_table_data = sim_info['mtc_output_table']
        self.expression_table_data = sim_info['mtc_expr_table']

        # doetab
        self.doe_mv_bounds = doe_info['mtc_mv_bounds']


if __name__ == "__main__":
    ds = DataStorage()
    ds.simulation_data = {'components': ['PROPANE', 'PROPENE'],
                          'therm_method': ['PENG-ROB'],
                          'blocks': ['TOWER'],
                          'streams': ['B', 'D', 'F'],
                          'reactions': [''],
                          'sens_analysis': ['S-1'],
                          'calculators': ['C-1'],
                          'optimizations': ['O-1'],
                          'design_specs': ['']}
    jsonfilepath = r"C:\Users\Felipe\Desktop\GUI\python\infill.json"

    with open(jsonfilepath, 'r') as jfile:
        tree = json.load(jfile)

    root_input = tree['input']
    root_output = tree['output']

    ds.tree_model_input = root_input
    ds.tree_model_output = root_output

    #  save test
    mtc_filepath = r"C:\Users\Felipe\Desktop\GUI\python\infill_mtc.json"
    ds.save(mtc_filepath)

    # load test
    mtc_filepath_load = r"C:\Users\Felipe\Desktop\GUI\python\infill_mtc_mtc_input.json"
    ds.input_table_data = [{'Path': r"\Data\Blocks\TOWER\Input\BASIS_RR", 'Alias': 'rr', 'Type': 'Manipulated (MV)'},
                           {'Path': r"\Data\Blocks\TOWER\Input\D:F", 'Alias': 'df', 'Type': 'Manipulated (MV)'}]
    ds.save(mtc_filepath_load)
    ds.input_table_data = []

    ds2 = DataStorage()
    ds2.load(mtc_filepath_load)

    print(ds2.input_table_data)
