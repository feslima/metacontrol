import json
import pathlib

import pandas as pd
from py_expression_eval import Parser
from PyQt5.QtCore import QObject, pyqtSignal

from gui.models.math_check import is_expression_valid

# TODO: Implement class object to handle temporary file/folder creation for the
# application


class DataStorage(QObject):
    """Application data storage. This is for reuse of application data such as
    tree models, simulation data, aliases,
    expressions, etc.

    For tables, initialize and store empty tables as empty list.
    For forms, dictionaries must be initialized and empty stored with empty
    strings as values.
    """

    # signals to be fired when an attribute changes
    simulation_file_changed = pyqtSignal()
    simulation_info_changed = pyqtSignal()
    alias_data_changed = pyqtSignal()
    expr_data_changed = pyqtSignal()
    doe_mv_bounds_changed = pyqtSignal()
    doe_sampled_data_changed = pyqtSignal()
    reduced_doe_constraint_activity_changed = pyqtSignal()
    reduced_doe_sampled_data_changed = pyqtSignal()

    sampling_enabled = pyqtSignal(bool)
    metamodel_enabled = pyqtSignal(bool)
    hessian_enabled = pyqtSignal(bool)

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
                          'lhs': {'n_samples': 50,
                                  'n_iter': 5,
                                  'inc_vertices': False},
                          'csv': {'filepath': '',
                                  'convergence_index': '',
                                  'pair_info': {}},
                          'sampled': {}
                          }
        self._metamodel_data = {
            'theta': [],
            'selected': [],
        }
        # TODO: Move activity data into reduced data dictionary
        self._activity_data = {'activity_info': {}}
        self._reduced_data = {'d_bounds': [],
                              'csv': {'filepath': '',
                                      'convergence_index': '',
                                      'pair_info': {}},
                              'sampled': {}
                              }
        self._hessian_data = {'metamodel_data': {'theta': [],
                                                 'selected': []
                                                 }
                              }

        # --------------------------- SIGNALS/SLOTS ---------------------------
        # whenever expression data changes, perform a simulation setup check
        self.expr_data_changed.connect(self.check_simulation_setup)

        # update doe_mv_bounds whenever aliases data changes
        self.alias_data_changed.connect(self._update_mv_bounds)

        # update theta data whenever aliases data changes
        self.alias_data_changed.connect(self._update_theta_data)

        # update selected variables data for construction whenever alias or
        # expression data changes
        self.alias_data_changed.connect(self._update_selected_data)
        self.expr_data_changed.connect(self._update_selected_data)

        # update constraint activity data whenever expression datas changes
        self.alias_data_changed.connect(self._update_constraint_activity)
        self.expr_data_changed.connect(self._update_constraint_activity)

        # whenever variable, expression or sampled data changes, perform a DOE
        # setup check
        self.alias_data_changed.connect(self.check_sampling_setup)
        self.expr_data_changed.connect(self.check_sampling_setup)
        self.doe_sampled_data_changed.connect(self.check_sampling_setup)

        # whenever constraint activity info changes, perform a setup check
        self.reduced_doe_constraint_activity_changed.connect(
            self.check_reduced_space_setup)

        # update reduced_doe_d_bounds whenever aliases data changes
        self.alias_data_changed.connect(self._update_d_bounds)

        # update reduced theta data whenever aliases or constraint activity
        # changes
        self.alias_data_changed.connect(self._update_reduced_theta_data)
        self.reduced_doe_constraint_activity_changed.connect(
            self._update_reduced_theta_data)

        # update selected variables data for construction whenever constraint
        # activity data changes
        self.reduced_doe_constraint_activity_changed.connect(
            self._update_reduced_selected_data
        )

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
                self.simulation_file_changed.emit()
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

            try:
                self._check_keys(key_list, dictionary, self._simulation_data)
            except KeyError as ke:
                # re-raise the KeyError exception
                raise ke
            else:
                # if the values are properly set, emit the signal
                self.simulation_info_changed.emit()
        else:
            raise KeyError("Simulation data must be a dictionary object.")

    @property
    def input_table_data(self):
        """List of dicts containing the input variables aliases, paths and
        types. Keys are: 'Alias', 'Path', 'Type'."""
        return self._input_table_data

    @input_table_data.setter
    def input_table_data(self, value: list):
        if isinstance(value, list):
            self._input_table_data = value
            self.alias_data_changed.emit()
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
            self.alias_data_changed.emit()
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
            self.expr_data_changed.emit()
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
            self.doe_mv_bounds_changed.emit()
        else:
            raise TypeError("MV bounds table data must be a list.")

    @property
    def doe_lhs_settings(self):
        """LHS info (dict) to read/write into LHS settings dialog.
        Keys are: 'n_samples', 'n_iter', 'inc_vertices'."""
        return self._doe_data['lhs']

    @doe_lhs_settings.setter
    def doe_lhs_settings(self, value: dict):
        if isinstance(value, dict):
            key_list = ['n_samples', 'n_iter', 'inc_vertices']
            self._check_keys(key_list, value, self._doe_data['lhs'])
        else:
            raise TypeError("LHS settings must be a dictionary object.")

    @property
    def doe_csv_settings(self):
        """CSV info (dict) to read/write into csveditor dialog.
        Keys are: 'filepath', 'convergence_index', pair_info"""
        return self._doe_data['csv']

    @doe_csv_settings.setter
    def doe_csv_settings(self, value: dict):
        if isinstance(value, dict):
            key_list = ['filepath', 'convergence_index', 'pair_info']
            self._check_keys(key_list, value, self._doe_data['csv'])
        else:
            raise TypeError("CSV editor settings must be a dictionary object.")

    @property
    def doe_sampled_data(self):
        """Sampled data dictionary. This dictionary is JSON compatible
        (dumped from pandas.DataFrame.to_dict('list'))."""
        return self._doe_data['sampled']

    @doe_sampled_data.setter
    def doe_sampled_data(self, value: dict):
        if isinstance(value, dict):
            self._doe_data['sampled'] = self.evaluate_expr_data(
                value, 'original')
            self.doe_sampled_data_changed.emit()
        else:
            raise TypeError("Sampled data must be a dictionary object")

    @property
    def metamodel_theta_data(self):
        """List of dicts containing lower and upper bounds, and estimates of
        theta values."""
        return self._metamodel_data['theta']

    @metamodel_theta_data.setter
    def metamodel_theta_data(self, value: list):
        if isinstance(value, list):
            self._metamodel_data['theta'] = value
        else:
            raise TypeError("Theta data must be a list of dictionaries.")

    @property
    def metamodel_selected_data(self):
        """List of dicts containing info which variables are checked for model
        construction. Keys are 'Alias', 'Type' and 'Checked'."""
        return self._metamodel_data['selected']

    @metamodel_selected_data.setter
    def metamodel_selected_data(self, value: list):
        if isinstance(value, list):
            self._metamodel_data['selected'] = value
        else:
            raise TypeError("Selected data must be a list of dictionaries.")

    @property
    def active_constraint_info(self):
        """Dictionary containing which variables from the optimization are
        active or not."""
        return self._activity_data['activity_info']

    @active_constraint_info.setter
    def active_constraint_info(self, value: dict):
        if isinstance(value, dict):
            self._activity_data['activity_info'] = value
            self.reduced_doe_constraint_activity_changed.emit()
        else:
            raise TypeError("Activity constraint info must be a dictionary.")

    @property
    def reduced_doe_csv_settings(self):
        """Reduced space CSV info (dict) to read/write into csveditor dialog.
        Keys are: 'filepath', convergence_index, pair_info"""
        return self._reduced_data['csv']

    @reduced_doe_csv_settings.setter
    def reduced_doe_csv_settings(self, value):
        if isinstance(value, dict):
            key_list = ['filepath', 'convergence_index', 'pair_info']
            self._check_keys(key_list, value, self._reduced_data['csv'])
        else:
            raise TypeError("Reduced space CSV editor settings must be a "
                            "dictionary object.")

    @property
    def reduced_doe_d_bounds(self):
        """List of dicts containing the D's and its bounds to be displayed
        or modified in doetab. Keys are: 'name', 'lb', 'ub'."""
        return self._reduced_data['d_bounds']

    @reduced_doe_d_bounds.setter
    def reduced_doe_d_bounds(self, value: list):
        if isinstance(value, list):
            self._reduced_data['d_bounds'] = value
        else:
            raise TypeError("Disturbance bounds table data must be a list.")

    @property
    def reduced_doe_sampled_data(self):
        """Reduced model sampled data dictionary. This dictionary is JSON compatible
        (dumped from pandas.DataFrame.to_dict('list'))."""
        return self._reduced_data['sampled']

    @reduced_doe_sampled_data.setter
    def reduced_doe_sampled_data(self, value):
        self._reduced_doe_sampled_data = value
        if isinstance(value, dict):
            self._reduced_data['sampled'] = self.evaluate_expr_data(
                value, 'reduced')
            self.reduced_doe_sampled_data_changed.emit()
        else:
            raise TypeError("Reduced model sampled data must be a dictionary "
                            "object")

    @property
    def reduced_metamodel_theta_data(self):
        """List of dicts containing lower and upper bounds, and estimates of
        reduced space variables theta values."""
        return self._hessian_data['metamodel_data']['theta']

    @reduced_metamodel_theta_data.setter
    def reduced_metamodel_theta_data(self, value):
        if isinstance(value, list):
            self._hessian_data['metamodel_data']['theta'] = value
        else:
            raise TypeError(
                "Reduced theta data must be a list of dictionaries.")

    @property
    def reduced_metamodel_selected_data(self):
        """Updates the list of selected variables for reduced model
        construction whenever alias or expression data is changed (SLOT)."""
        return self._hessian_data['metamodel_data']['selected']

    @reduced_metamodel_selected_data.setter
    def reduced_metamodel_selected_data(self, value):
        if isinstance(value, list):
            self._hessian_data['metamodel_data']['selected'] = value
        else:
            raise TypeError("Selected data must be a list of dictionaries.")

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

    def _update_mv_bounds(self) -> None:
        """Updates the MV bounds data whenever alias data is changed. (SLOT)
        """
        # list of aliases that are MV
        mv_aliases = [row['Alias'] for row in self._input_table_data
                      if row['Type'] == 'Manipulated (MV)']

        # delete the variables that aren't in the mv list
        new_bnds = [row for idx, row in enumerate(self._doe_data['mv_bounds'])
                    if row['name'] in mv_aliases]

        mv_bnd_list = [row['name'] for row in new_bnds]

        # insert new values
        [new_bnds.append({'name': alias, 'lb': 0.0, 'ub': 1.0}) for alias
         in mv_aliases if alias not in mv_bnd_list]

        # store values
        self.doe_mv_bounds = new_bnds

    def _update_theta_data(self) -> None:
        """Updates the theta list whenever alias data is changed. (SLOT)
        """
        # list of aliases that are MV
        input_aliases = [row['Alias'] for row in self._input_table_data
                         if row['Type'] == 'Manipulated (MV)']

        # delete the variables that aren't in the mv list
        new_thetas = [row for row in self._metamodel_data['theta']
                      if row['Alias'] in input_aliases]

        theta_bnd_list = [row['Alias'] for row in new_thetas]

        # insert new values
        [new_thetas.append({'Alias': alias, 'lb': 1e-5,
                            'ub': 1.0e5, 'theta0': 1.0})
         for alias in input_aliases if alias not in theta_bnd_list]

        # store values
        self.metamodel_theta_data = new_thetas

    def _update_selected_data(self) -> None:
        """Updates the list of selected variables for model construction
        whenever alias or expression data is changed (SLOT).
        """
        # list of variables
        vars = [{'Alias': row['Alias'], 'Type': row['Type']}
                for row in self._output_table_data +
                self._expression_table_data
                if row['Type'] == 'Candidate (CV)' or
                row['Type'] == 'Constraint function' or
                row['Type'] == 'Objective function (J)']

        # list of aliases
        aliases = [row['Alias'] for row in vars]

        # delete variables that aren't in the list
        new_vars = [row for row in self._metamodel_data['selected']
                    if row['Alias'] in aliases]

        vars_list = [row['Alias'] for row in new_vars]

        # insert new variables
        [new_vars.append({'Alias': var['Alias'], 'Type': var['Type'],
                          'Checked': False})
         for var in vars if var['Alias'] not in vars_list]

        # store values
        self.metamodel_selected_data = new_vars

    def _update_constraint_activity(self) -> None:
        """Updates the constraint activity info to be displayed whenever
        alias data changes (SLOT). Managed to be used by a pandas DataFrame.
        """
        # list of variables
        vars = [{'Alias': row['Alias'], 'Type': row['Type']}
                for row in self.input_table_data + self.output_table_data +
                self._expression_table_data
                if row['Type'] == 'Manipulated (MV)' or
                row['Type'] == 'Candidate (CV)']

        # list of aliases
        aliases = [row['Alias'] for row in vars]

        # delete variables that aren't in the list
        new_vars = {row: {'Type': self.active_constraint_info[row]['Type'],
                          'Active': self.active_constraint_info[row]['Active'],
                          'Value': self.active_constraint_info[row]['Value'],
                          'Pairing': self.active_constraint_info[row]['Pairing']}
                    for row in self.active_constraint_info
                    if row in aliases}

        # insert new variables
        [new_vars.update({var['Alias']: {'Type': var['Type'],
                                         'Active': False,
                                         'Value': None,
                                         'Pairing': None}})
         for var in vars if var['Alias'] not in new_vars]

        # store values
        self.active_constraint_info = new_vars

    def _update_d_bounds(self) -> None:
        """Updates the D bounds data whenever alias data is changed. (SLOT)
        """
        # list of aliases that are D
        d_aliases = [row['Alias'] for row in self._input_table_data
                     if row['Type'] == 'Disturbance (d)']

        # delete the variables that aren't in the mv list
        new_bnds = [row for _, row in enumerate(self._reduced_data['d_bounds'])
                    if row['name'] in d_aliases]

        d_bnd_list = [row['name'] for row in new_bnds]

        # insert new values
        [new_bnds.append({'name': alias, 'lb': 0.0, 'ub': 1.0}) for alias
         in d_aliases if alias not in d_bnd_list]

        # store values
        self.reduced_doe_d_bounds = new_bnds

    def _update_reduced_theta_data(self) -> None:
        """Updates the reduced model theta list whenever alias data is changed.
        (SLOT) - associated with alias and constraint activity change.
        """

        # list of aliases that are disturbances and not paired (consumed) MVs.
        dist_aliases = [row['Alias'] for row in self.input_table_data
                        if row['Type'] == 'Disturbance (d)']

        # get the consumed aliases from constraint activity info where the
        # type of paired alias is active and not manipulated.
        con_act = self.active_constraint_info
        consumed_aliases = [con_act[con]['Pairing']
                            for con in con_act
                            if con_act[con]['Type'] != 'Manipulated (MV)' and
                            con_act[con]['Active']]

        non_consumed_aliases = [row['Alias'] for row in self.input_table_data
                                if row['Type'] == 'Manipulated (MV)' and
                                row['Alias'] not in consumed_aliases]

        # aliases to be displayed in the theta table
        input_aliases = dist_aliases + non_consumed_aliases

        # delete the variables that aren't in the input list
        new_thetas = [row for row in self.reduced_metamodel_theta_data
                      if row['Alias'] in input_aliases]

        theta_bnd_list = [row['Alias'] for row in new_thetas]

        # insert new values
        [new_thetas.append({'Alias': alias, 'lb': 1e-12,
                            'ub': 1.e-3, 'theta0': 1e-6})
         for alias in input_aliases if alias not in theta_bnd_list]

        # store values
        self.reduced_metamodel_theta_data = new_thetas

    def _update_reduced_selected_data(self) -> None:
        """Updates the list of selected variables for model construction
        whenever alias or expression data is changed (SLOT) - associated with
        alias and constraint activity change."""
        # list of non active constraints

        con_act = self.active_constraint_info
        non_act_aliases = [{'Alias': con, 'Type': con_act[con]['Type']}
                           for con in con_act
                           if not con_act[con]['Active'] and
                           con_act[con]['Type'] != "Manipulated (MV)"]

        # assuming that a pairing is always a MV
        pairings = [{'Alias': con_act[con]['Pairing'],
                     'Type': 'Manipulated (MV)'}
                    for con in con_act
                    if con_act[con]['Type'] != 'Manipulated (MV)' and
                    con_act[con]['Active']]

        obj_fun = [{'Alias': row['Alias'], 'Type': row['Type']}
                   for row in self.output_table_data +
                   self.expression_table_data
                   if row['Type'] == 'Objective function (J)']

        vars = non_act_aliases + pairings + obj_fun

        # list of aliases
        aliases = [row['Alias'] for row in vars]

        # delete variables that aren't in the list
        new_vars = [row for row in self.reduced_metamodel_selected_data
                    if row['Alias'] in aliases]

        vars_list = [row['Alias'] for row in new_vars]

        # insert new vairables
        [new_vars.append({'Alias': var['Alias'], 'Type': var['Type'],
                          'Checked': False})
         for var in vars if var['Alias'] not in vars_list]

        # store values
        self.reduced_metamodel_selected_data = new_vars

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
        #   - 'doe_info': doetab (implemented)
        #   - 'metacontrol_info' : metacontroltab (implemented)
        #   - 'reduced_space_info' : reducedspacetab (partially implemented)
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
                'mtc_mv_bounds': self.doe_mv_bounds,
                'mtc_sampled_data': self.doe_sampled_data
            },
            'reduced_space_info': {
                'mtc_constraint_activity': self.active_constraint_info,
                'mtc_reduced_d_bounds': self.reduced_doe_d_bounds,
                'mtc_reduced_sampled_data': self.reduced_doe_sampled_data
            }
        }

        # perfom the JSON dump
        with open(output_path, 'w') as mtc_file:
            json.dump(app_data, mtc_file, indent=4)

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
        redspace_info = app_data['reduced_space_info']

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
        self.doe_sampled_data = doe_info['mtc_sampled_data']

        # reducedpsacetab
        self.active_constraint_info = redspace_info['mtc_constraint_activity']
        self.reduced_doe_d_bounds = redspace_info['mtc_reduced_d_bounds']
        self.reduced_doe_sampled_data = redspace_info['mtc_reduced_sampled_data']

    def check_simulation_setup(self):
        """Checks if there are aliases and expressions are mathematically
        valid. Also checks if expression types are defined, and there are no
        duplicates between expression names and variable aliases.

        If everything is ok, emits a signal with a boolean value where True
        means that the sampling phase is good to go, otherwise the value is
        False.
        """
        # get aliases
        aliases = [row['Alias'] for row in self.input_table_data +
                   self.output_table_data]

        # get expression names
        expr_names = [row['Alias'] for row in self.expression_table_data]

        # get expressions validity
        expr_valid_check = [is_expression_valid(row['Expr'], aliases)
                            for row in self.expression_table_data]

        is_name_duplicated = True if len(expr_names + aliases) != \
            len(set(expr_names + aliases)) else False

        is_exprs_valid = True if len(expr_valid_check) != 0 \
            and all(expr_valid_check) else False

        is_expr_defined = True if all(row['Type'] != 'Choose a type' for row
                                      in self.expression_table_data) else False

        if is_exprs_valid and not is_name_duplicated and is_expr_defined:
            # everything is ok, proceed to sampling
            self.sampling_enabled.emit(True)
        else:
            # not ok, can't proceed to sampling
            self.sampling_enabled.emit(False)

    def check_sampling_setup(self):
        """Checks if sampling data contains the data for all input/output
        variables and is not empty.

        If everything is ok, emits a signal with a boolean value where True
        means that the metamodel construction phase is good to go, otherwise
        the value is False.
        """
        input_alias = [row['Alias'] for row in self.input_table_data
                       if row['Type'] == 'Manipulated (MV)']
        output_alias = [row['Alias']
                        for row in self.output_table_data]
        expr_alias = [row['Alias'] for row in self.expression_table_data]
        aliases = input_alias + output_alias + expr_alias

        # build the DataFrame
        df = pd.DataFrame(self.doe_sampled_data)

        is_sampling_empty = df.empty

        is_alias_sampled = all(alias in df.columns for alias in aliases)

        if is_alias_sampled and not is_sampling_empty:
            self.metamodel_enabled.emit(True)
        else:
            self.metamodel_enabled.emit(False)

    def check_reduced_space_setup(self):
        """Check if the reduced space setup is properly set.

        If everything is ok, emits a signal with a boolean value where True
        means that the hessian extraction phase is good to go, otherwise
        the value is False.
        """
        # FIXME: Case where there is not active constraint selected is not
        # treated. What to do? Proceed or not?
        cact_df = pd.DataFrame(self.active_constraint_info)

        if not cact_df.empty:
            # check if the optimum mv values are set
            mv_var_idx = cact_df.loc['Type', :] == 'Manipulated (MV)'
            mv_values = cact_df.loc['Value', mv_var_idx]
            is_mv_set = mv_values.notna().all()

            # check if the pairing MVs aren't repeated
            active_con_funs = cact_df.loc['Active', :].astype(bool)
            not_mvs_active = cact_df.columns[~mv_var_idx & active_con_funs]
            pairings = cact_df.loc['Pairing', not_mvs_active]
            is_pairing_repeated = pairings.duplicated().sum() > 0

            # check if the pairings are defined
            is_pairing_defined = not pairings.isna().any()

            # check if reduced space doe is sampled
            red_df = pd.DataFrame(self.reduced_doe_sampled_data)

            is_sampling_empty = red_df.empty
        else:
            # empty active contraint info object
            is_mv_set = False
            is_pairing_repeated = True
            is_pairing_defined = False
            is_sampling_empty = True

        if is_mv_set and not is_pairing_repeated and is_pairing_defined and \
                not is_sampling_empty:
            self.hessian_enabled.emit(True)
        else:
            self.hessian_enabled.emit(False)

    def evaluate_expr_data(self, sampled_data_dict: dict, space_type: str) -> \
            dict:
        """Evaluates the expressions and append values to the current sampled
        data.

        Parameters
        ----------
        sampled_data_dict: dict
            Sampled data in dictionary format. (dumped from another Dataframe)
        space_type : str
            Which space the data represents: 'original' or 'reduced'

        Returns
        -------
        out : dict
            The complete dataframe with expressions evaluated as a dict
        """
        if space_type not in ['original', 'reduced']:
            raise ValueError("The space type must be 'original' or 'reduced'.")

        samp_data = pd.DataFrame(sampled_data_dict)

        if space_type == 'original':
            hdr = [row['Alias']
                   for row in self.input_table_data +
                   self.output_table_data
                   if row['Type'] != "Disturbance (d)"]
        else:
            hdr = [row['Alias']
                   for row in self.input_table_data +
                   self.output_table_data]

        df_headers = ['case', 'status'] + hdr
        if not samp_data.empty:
            samp_data = samp_data[df_headers]
        else:
            samp_data = pd.DataFrame(columns=df_headers)

        # intialize empty dataframe
        expr_df = pd.DataFrame(columns=[row['Alias'] for row in
                                        self.expression_table_data])

        parser = Parser()

        for idx, row in samp_data.iterrows():
            row_val_dict = row.to_dict()  # convert row series to dict
            expr_row_values = {}

            for expr in self.expression_table_data:
                expr_to_parse = parser.parse(expr['Expr'])
                var_list = expr_to_parse.variables()
                expr_row_values[expr['Alias']] = expr_to_parse.evaluate(
                    row_val_dict)

            # append values to expr_df
            expr_df = expr_df.append(expr_row_values, ignore_index=True)

        # merge sampled data and expression data and store them, if they don't
        # already exist
        if expr_df.columns.difference(samp_data.columns).size != 0:
            samp_data = samp_data.merge(expr_df, left_index=True,
                                        right_index=True)

        return samp_data.to_dict(orient='list')
