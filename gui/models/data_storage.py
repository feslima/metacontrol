import copy
import simplejson as json
import pathlib

import numpy as np
import pandas as pd
from py_expression_eval import Parser
from PyQt5.QtCore import QObject, pyqtSignal
from scipy.special import comb

from gui.models.math_check import is_expression_valid
from gui.calls.base import warn_the_user

# TODO: Implement class object to handle temporary file/folder creation for the
# application


class PandasEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, pd.DataFrame):
            return o.to_dict()
        elif isinstance(o, pd.Series):
            return o.to_dict()
        return json.JSONEncoder.default(self, o)


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
    input_alias_data_changed = pyqtSignal()
    output_alias_data_changed = pyqtSignal()
    expr_data_changed = pyqtSignal()
    doe_mv_bounds_changed = pyqtSignal()
    doe_sampled_data_changed = pyqtSignal()
    optimization_results_changed = pyqtSignal()
    optimization_parameters_changed = pyqtSignal()
    reduced_space_dof_changed = pyqtSignal()
    active_candidates_changed = pyqtSignal()
    reduced_d_bounds_changed = pyqtSignal()
    reduced_doe_sampled_data_changed = pyqtSignal()
    reduced_selected_data_changed = pyqtSignal()
    differential_gy_data_changed = pyqtSignal(str)
    differential_gyd_data_changed = pyqtSignal(str)
    differential_juu_data_changed = pyqtSignal(str)
    differential_jud_data_changed = pyqtSignal(str)
    soc_dist_mag_data_changed = pyqtSignal(str)
    soc_meas_mag_data_changed = pyqtSignal(str)
    soc_subset_data_changed = pyqtSignal()

    sampling_enabled = pyqtSignal(bool)
    metamodel_enabled = pyqtSignal(bool)
    hessian_enabled = pyqtSignal(bool)
    soc_enabled = pyqtSignal(bool)

    # ------------------------------ CONSTANTS --------------------------------
    # simulation data columns
    _SIM_DATA_COLS = ['components', 'therm_method', 'blocks', 'streams',
                      'reactions', 'sens_analysis', 'calculators',
                      'optimizations', 'design_specs']

    # variables (aliases) columns
    _ALIAS_COLS = ['Alias', 'Path', 'Type']

    # expressions columns
    _EXPR_COLS = ['Alias', 'Expression', 'Type']

    # variables types
    _INPUT_ALIAS_TYPES = {
        'mv': 'Manipulated (MV)',
        'd': 'Disturbance (d)'
    }
    _OUTPUT_ALIAS_TYPES = {
        'aux': 'Auxiliary',
        'cv': 'Candidate (CV)'
    }
    _EXPR_ALIAS_TYPES = {
        'cv': 'Candidate (CV)',
        'cst': 'Constraint function',
        'obj': 'Objective function (J)'
    }

    # input variables bounds columns (disturbances included)
    _INP_BOUNDS_COLS = ['name', 'lb', 'ub']

    # metamodel theta bounds columns
    _META_THETA_BNDS = ['Alias', 'lb', 'ub', 'theta0']

    # selected metamodel columns
    _META_SELEC_COLS = ['Alias', 'Type', 'Checked']

    # reduced space dof
    _RED_SPACE_DOF_COLS = ['Alias', 'Checked']
    _RED_SPACE_ACT_COLS = ['Alias', 'Checked']

    # reduced space bounds
    _REDSPACE_BNDS_COLS = ['name', 'lb', 'nominal', 'ub']

    def __init__(self):
        super().__init__()
        self._simulation_file = ''
        self._tree_model_input = {}
        self._tree_model_output = {}
        self.input_table_data = pd.DataFrame(columns=self._ALIAS_COLS)
        self.output_table_data = pd.DataFrame(columns=self._ALIAS_COLS)
        self.expression_table_data = pd.DataFrame(columns=self._EXPR_COLS)

        self._hessian_data = {'metamodel_data': {'selected': []},
                              'regression': 'poly0',
                              'correlation': 'corrgauss',
                              'gy': {},
                              'gyd': {},
                              'juu': {},
                              'jud': {}
                              }
        self._soc_data = {'md': {},
                          'me': {},
                          'ss_list': {}
                          }

        # --------------------------- SIGNALS/SLOTS ---------------------------
        # Whenever simulation file changes, check simulation and sampling setup
        self.simulation_file_changed.connect(self.check_simulation_setup)
        self.simulation_file_changed.connect(self.check_sampling_setup)

        # Whenever INPUT ALIAS data changes update (or check setup):
        # - doe_mv_bounds
        self.input_alias_data_changed.connect(self._update_mv_bounds)
        # - metamodel_theta_data
        self.input_alias_data_changed.connect(self._update_theta_data)
        # reduced_space_dof
        self.input_alias_data_changed.connect(self._update_reduced_space_dof)
        # - reduced_doe_d_bounds
        self.input_alias_data_changed.connect(self._update_reduced_d_bounds)
        # - reduced_metamodel_theta_data
        self.input_alias_data_changed.connect(self._update_reduced_theta_data)
        # - check_simulation_setup
        self.input_alias_data_changed.connect(self.check_simulation_setup)
        # - check_sampling_setup
        self.input_alias_data_changed.connect(self.check_sampling_setup)

        # Whenever OUTPUT ALIAS data changes update (or check setup):
        # - metamodel_selected_data (construct metamodels)
        self.output_alias_data_changed.connect(self._update_selected_data)
        # - active_constraint_info
        self.output_alias_data_changed.connect(
            self._update_active_candidates)
        # - check_simulation_setup
        self.output_alias_data_changed.connect(self.check_simulation_setup)
        # - check_sampling_setup
        self.output_alias_data_changed.connect(self.check_sampling_setup)

        # Whenever EXPRESSION DATA changes update (or check setup):
        # - metamodel_selected_data (construct metamodels)
        self.expr_data_changed.connect(self._update_selected_data)
        # - active_constraint_info
        self.expr_data_changed.connect(self._update_active_candidates)
        # - check_simulation_setup
        self.expr_data_changed.connect(self.check_simulation_setup)
        # - check_sampling_setup
        self.expr_data_changed.connect(self.check_sampling_setup)

        # Whenever DOE SAMPLED DATA changes update (or check setup):
        # - check_sampling_setup
        self.doe_sampled_data_changed.connect(self.check_sampling_setup)

        # Whenever ACTIVE CONSTRAINT INFO changes update (or check setup):
        # - reduced_doe_d_bounds
        self.reduced_space_dof_changed.connect(
            self._update_reduced_d_bounds
        )

        # - reduced_metamodel_theta_data
        self.reduced_space_dof_changed.connect(
            self._update_reduced_theta_data
        )
        # - reduced_metamodel_selected_data
        self.active_candidates_changed.connect(
            self._update_reduced_selected_data
        )
        # - check_reduced_space_setup
        self.reduced_space_dof_changed.connect(
            self.check_reduced_space_setup)

        self.active_candidates_changed.connect(
            self.check_reduced_space_setup)

        # Whenever REDUCED DOE SAMPLED DATA changes update (or check setup):
        # - check_reduced_space_setup
        self.reduced_doe_sampled_data_changed.connect(
            self.check_reduced_space_setup)

        # whenever constraint activity/ expr data changes, update disturbance
        # and measurement error magnitudes data
        self.alias_data_changed.connect(self._update_magnitude_data)
        self.reduced_space_dof_changed.connect(
            self._update_magnitude_data
        )
        self.active_candidates_changed.connect(
            self._update_magnitude_data
        )

        # whenever reduced select data changes, update subset sizing list
        # data
        self.reduced_selected_data_changed.connect(
            self._update_subset_data
        )
        self.reduced_selected_data_changed.connect(
            self._update_magnitude_data
        )

        # perform a hessian setup check whenever gradient or hessian data
        # changes
        self.differential_gy_data_changed.connect(self.check_hessian_setup)
        self.differential_gyd_data_changed.connect(self.check_hessian_setup)
        self.differential_juu_data_changed.connect(self.check_hessian_setup)
        self.differential_jud_data_changed.connect(self.check_hessian_setup)

        # whenever optimization results change update the reduced space bounds
        self.optimization_results_changed.connect(
            self._update_reduced_d_bounds
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
        """DataFrame containing the information about the simulation;
        """

        if not hasattr(self, '_simulation_data'):
            self._simulation_data = pd.DataFrame(columns=self._SIM_DATA_COLS)

        return self._simulation_data

    @simulation_data.setter
    def simulation_data(self, frame: pd.DataFrame):
        if isinstance(frame, pd.DataFrame):
            # check for frame equality to avoid unnecessary operations
            if not frame.equals(self.simulation_data):
                # check if the columns are properly set.
                if frame.columns.isin(self._SIM_DATA_COLS).all():
                    # all columns present, reorganize columns and emit signal
                    self._simulation_data = frame[self._SIM_DATA_COLS]

                    self.simulation_info_changed.emit()
                else:
                    raise ValueError("All columns of 'simulation_data' must be "
                                     "defined.")
            else:
                # frame is equal, do nothing
                pass

        else:
            raise TypeError("Simulation data must be a DataFrame.")

    @property
    def input_table_data(self):
        """DataFrame containing the input variables aliases, paths and
        types. columns are: 'Alias', 'Path', 'Type'."""
        return self._input_table_data

    @input_table_data.setter
    def input_table_data(self, value: pd.DataFrame):
        if isinstance(value, pd.DataFrame):
            if value.columns.isin(self._ALIAS_COLS).all():
                if value.index.is_object():
                    value.index = value.index.astype(int)

                self._input_table_data = value
                self.input_alias_data_changed.emit()

            else:
                raise ValueError("'input_table_data' must have its columns "
                                 "defined.")
        else:
            raise TypeError("Input table data must be a DataFrame.")

    @property
    def output_table_data(self):
        """DataFrame containing the output variables aliases, paths and
        types. Keys are: 'Alias', 'Path', 'Type'."""
        return self._output_table_data

    @output_table_data.setter
    def output_table_data(self, value: pd.DataFrame):
        if isinstance(value, pd.DataFrame):
            if value.columns.isin(self._ALIAS_COLS).all():
                if value.index.is_object():
                    value.index = value.index.astype(int)

                self._output_table_data = value
                self.output_alias_data_changed.emit()
            else:
                raise ValueError("'output_table_data' must have its columns "
                                 "defined.")
        else:
            raise TypeError("Output table data must be a DataFrame.")

    @property
    def expression_table_data(self):
        """DataFrame containing the expressions names, equations and
        types. Keys are: 'Alias', 'Expression', 'Type'."""
        return self._expression_table_data

    @expression_table_data.setter
    def expression_table_data(self, value: pd.DataFrame):
        if isinstance(value, pd.DataFrame):
            if value.columns.isin(self._EXPR_COLS).all():
                if value.index.is_object():
                    value.index = value.index.astype(int)

                self._expression_table_data = value
                self.expr_data_changed.emit()
            else:
                raise ValueError("'expression_table_data' must have its "
                                 "columns defined.")
        else:
            raise TypeError("Expression table data must be a DataFrame.")

    @property
    def doe_mv_bounds(self):
        """DataFrame containing the MVs and its bounds to be displayed or
        modified in doetab. columns are: 'name', 'lb', 'ub'."""

        if not hasattr(self, '_doe_mv_bounds'):
            # attribute not created (init), create now
            self._doe_mv_bounds = pd.DataFrame(
                columns=self._INP_BOUNDS_COLS
            )

        return self._doe_mv_bounds

    @doe_mv_bounds.setter
    def doe_mv_bounds(self, value: pd.DataFrame):
        if isinstance(value, pd.DataFrame):
            if value.columns.isin(self._INP_BOUNDS_COLS).all():
                if value.index.is_object():
                    value.index = value.index.astype(int)

                self._doe_mv_bounds = value
                self.doe_mv_bounds_changed.emit()

            else:
                raise ValueError("'doe_mv_bounds' must have its columns "
                                 "defined.")
        else:
            raise TypeError("MV bounds table data must be a DataFrame.")

    @property
    def doe_lhs_settings(self):
        """LHS info (Series) to read/write into LHS settings dialog.
        Keys are: 'n_samples', 'n_iter', 'inc_vertices'."""
        if not hasattr(self, '_doe_lhs_settings'):
            # attribute not created (init), create now
            self._doe_lhs_settings = pd.Series({'n_samples': 50,
                                                'n_iter': 5,
                                                'inc_vertices': False})

        return self._doe_lhs_settings

    @doe_lhs_settings.setter
    def doe_lhs_settings(self, value: pd.Series):
        if isinstance(value, pd.Series):
            if value.index.isin(['n_samples', 'n_iter', 'inc_vertices']).all():
                self._doe_lhs_settings = value
            else:
                raise ValueError("'doe_lhs_settings' must have its fields "
                                 "defined.")

        else:
            raise TypeError("LHS settings must be a Series.")

    @property
    def doe_csv_settings(self):
        """CSV info (dict) to read/write into csveditor dialog.
        Keys are: 'filepath', 'convergence_index', pair_info"""
        if not hasattr(self, '_doe_csv_settings'):
            self._doe_csv_settings = {'filepath': '',
                                      'convergence_index': '',
                                      'pair_info': {}}

        return self._doe_csv_settings

    @doe_csv_settings.setter
    def doe_csv_settings(self, value: dict):
        if isinstance(value, dict):
            key_list = ['filepath', 'convergence_index', 'pair_info']
            self._check_keys(key_list, value, self._doe_csv_settings)
        else:
            raise TypeError("CSV editor settings must be a dictionary object.")

    @property
    def doe_sampled_data(self):
        """Sampled data dictionary. This dictionary is JSON compatible
        (dumped from pandas.DataFrame.to_dict('list'))."""

        if not hasattr(self, '_doe_sampled_data'):
            # attribute not created (init), create now
            self._doe_sampled_data = pd.DataFrame()

        return self._doe_sampled_data

    @doe_sampled_data.setter
    def doe_sampled_data(self, value: pd.DataFrame):
        if isinstance(value, pd.DataFrame):
            if value.index.is_object():
                value.index = value.index.astype(int)
            self._doe_sampled_data = self.evaluate_expr_data(value, 'original')
            self.doe_sampled_data_changed.emit()
        else:
            raise TypeError("Sampled data must be a DataFrame")

    @property
    def metamodel_theta_data(self):
        """DataFrame containing lower and upper bounds, and estimates of
        theta values."""
        if not hasattr(self, '_metamodel_theta_data'):
            # attribute not created (init), create now
            self._metamodel_theta_data = pd.DataFrame(
                columns=self._META_THETA_BNDS
            )

        return self._metamodel_theta_data

    @metamodel_theta_data.setter
    def metamodel_theta_data(self, value: pd.DataFrame):
        if isinstance(value, pd.DataFrame):
            if value.columns.isin(self._META_THETA_BNDS).all():
                self._metamodel_theta_data = value
            else:
                raise ValueError("'metamodel_theta_data' must have its columns "
                                 "defined.")
        else:
            raise TypeError("Theta data must be a DataFrame.")

    @property
    def metamodel_selected_data(self):
        """DataFrame containing info which variables are checked for model
        construction. Columns are 'Alias', 'Type' and 'Checked'."""

        if not hasattr(self, '_metamodel_selected_data'):
            # attribute not created (init), create now
            self._metamodel_selected_data = pd.DataFrame(
                columns=self._META_SELEC_COLS
            )

        return self._metamodel_selected_data

    @metamodel_selected_data.setter
    def metamodel_selected_data(self, value: pd.DataFrame):
        if isinstance(value, pd.DataFrame):
            if value.columns.isin(self._META_SELEC_COLS).all():
                self._metamodel_selected_data = value
            else:
                raise ValueError("'metamodel_selected_data' must have its "
                                 "columns defined.")
        else:
            raise TypeError("Selected data must be a DataFrame.")

    @property
    def optimization_results(self):
        """Series containing the results from the optimization."""

        if not hasattr(self, '_optimization_results'):
            self._optimization_results = pd.Series()

        return self._optimization_results

    @optimization_results.setter
    def optimization_results(self, value: pd.Series):
        if isinstance(value, pd.Series):
            self._optimization_results = value
            self.optimization_results_changed.emit()

        else:
            raise TypeError("Optimization results must be a Series object.")
    
    @property
    def optimization_parameters(self):
        """Dictionary containing the parameters for the optimization phase."""

        if not hasattr(self, '_optimization_parameters'):
            dc = {
                'first_factor': 0.8,
                'second_factor': 0.4,
                'tol_contract': 1e-4,
                'con_tol': 1e-6,
                'penalty': 1e3,
                'tol1': 1e-4,
                'tol2': 1e-5,
                'maxfunevals': 1000,
                'regrpoly': 'poly0',
                'nlp_params': {
                    'solver_type': 'ipopt_local',
                    'tol': 1e-8,
                    'con_tol': 1e-6,
                    'max_iter': 3000
                }
            }

            self._optimization_parameters = dc

        return self._optimization_parameters

    @optimization_parameters.setter
    def optimization_parameters(self, value: dict):
        if isinstance(value, dict):
            self._optimization_parameters = value
            self.optimization_parameters_changed.emit()

        else:
            raise TypeError("Optimization parameters must be a dictionary.")

    @property
    def reduced_space_dof(self):
        """DataFrame containing which MV's are in the reduced space degrees of
        freedom."""

        if not hasattr(self, '_reduced_space_dof'):
            self._reduced_space_dof = pd.DataFrame(
                columns=self._RED_SPACE_DOF_COLS
            )

        return self._reduced_space_dof

    @reduced_space_dof.setter
    def reduced_space_dof(self, value: pd.DataFrame):
        if isinstance(value, pd.DataFrame):
            if value.index.is_object():
                value.index = value.index.astype(int)
            self._reduced_space_dof = value
            self.reduced_space_dof_changed.emit()
        else:
            raise TypeError("Reduced space DOF must be a DataFrame.")

    @property
    def active_candidates(self):
        """DataFrame containing which candidates are active or not."""

        if not hasattr(self, '_active_candidates'):
            self._active_candidates = pd.DataFrame(
                columns=self._RED_SPACE_ACT_COLS
            )

        return self._active_candidates

    @active_candidates.setter
    def active_candidates(self, value: pd.DataFrame):
        if isinstance(value, pd.DataFrame):
            if value.index.is_object():
                value.index = value.index.astype(int)
            self._active_candidates = value
            self.active_candidates_changed.emit()

        else:
            raise TypeError("Active candidates must be a DataFrame.")

    @property
    def reduced_doe_lhs_settings(self):
        """LHS info (Series) to read/write into LHS settings dialog.
        Keys are: 'n_samples', 'n_iter', 'inc_vertices'."""
        if not hasattr(self, '_reduced_doe_lhs_settings'):
            # attribute not created (init), create now
            self._reduced_doe_lhs_settings = pd.Series({'n_samples': 50,
                                                        'n_iter': 5,
                                                        'inc_vertices': False})

        return self._reduced_doe_lhs_settings

    @reduced_doe_lhs_settings.setter
    def reduced_doe_lhs_settings(self, value: pd.Series):
        if isinstance(value, pd.Series):
            if value.index.isin(['n_samples', 'n_iter', 'inc_vertices']).all():
                self._reduced_doe_lhs_settings = value
            else:
                raise ValueError("'reduced_doe_lhs_settings' must have its "
                                 "fields defined.")

        else:
            raise TypeError("LHS settings must be a Series.")

    @property
    def reduced_doe_csv_settings(self):
        """Reduced space CSV info (dict) to read/write into csveditor dialog.
        Keys are: 'filepath', convergence_index, pair_info"""
        if not hasattr(self, '_reduced_doe_csv_settings'):
            self._reduced_doe_csv_settings = {'filepath': '',
                                              'convergence_index': '',
                                              'pair_info': {}}

        return self._reduced_doe_csv_settings

    @reduced_doe_csv_settings.setter
    def reduced_doe_csv_settings(self, value):
        if isinstance(value, dict):
            key_list = ['filepath', 'convergence_index', 'pair_info']
            self._check_keys(key_list, value, self._reduced_doe_csv_settings)
        else:
            raise TypeError("Reduced space CSV editor settings must be a "
                            "dictionary object.")

    @property
    def reduced_doe_d_bounds(self):
        """DataFrame containing the reduced space disturbance bounds and
        nominal values. columns are: 'name', 'lb', 'ub', 'nominal'."""

        if not hasattr(self, '_reduced_doe_d_bounds'):
            # attribute not created (init), create now
            self._reduced_doe_d_bounds = pd.DataFrame(
                columns=self._REDSPACE_BNDS_COLS
            )

        return self._reduced_doe_d_bounds

    @reduced_doe_d_bounds.setter
    def reduced_doe_d_bounds(self, value: pd.DataFrame):
        if isinstance(value, pd.DataFrame):
            if value.columns.isin(self._REDSPACE_BNDS_COLS).all():
                value = value[self._REDSPACE_BNDS_COLS]  # reorder columns
                if value.index.is_object():
                    value.index = value.index.astype(int)

                self._reduced_doe_d_bounds = value
                self.reduced_d_bounds_changed.emit()

            else:
                raise ValueError("'reduced_doe_d_bounds' must have its "
                                 "columns defined.")
        else:
            raise TypeError("Reduced space bounds table data must be a "
                            "DataFrame")

    @property
    def reduced_doe_sampled_data(self):
        """Reduced model sampled data DataFrame."""

        if not hasattr(self, '_reduced_doe_sampled_data'):
            # attribute not created (init), create now
            self._reduced_doe_sampled_data = pd.DataFrame()

        return self._reduced_doe_sampled_data

    @reduced_doe_sampled_data.setter
    def reduced_doe_sampled_data(self, value: pd.DataFrame):
        if isinstance(value, pd.DataFrame):
            if value.index.is_object():
                value.index = value.index.astype(int)
            self._reduced_doe_sampled_data = self.evaluate_expr_data(value,
                                                                     'reduced')
            self.reduced_doe_sampled_data_changed.emit()
        else:
            raise TypeError("Reduced model sampled data must be a DataFrame.")

    @property
    def reduced_metamodel_theta_data(self):
        """DataFrame containing lower and upper bounds, and estimates of
        reduced space variables theta values."""

        if not hasattr(self, '_reduced_metamodel_theta_data'):
            # attribute not created (init), create now
            self._reduced_metamodel_theta_data = pd.DataFrame(
                columns=self._META_THETA_BNDS
            )

        return self._reduced_metamodel_theta_data

    @reduced_metamodel_theta_data.setter
    def reduced_metamodel_theta_data(self, value: pd.DataFrame):
        if isinstance(value, pd.DataFrame):
            if value.columns.isin(self._META_THETA_BNDS).all():
                self._reduced_metamodel_theta_data = value
            else:
                raise ValueError("'reduced_metamodel_theta_data' must have "
                                 "its columns defined.")
        else:
            raise TypeError("Reduced theta data must be a DataFrame.")

    @property
    def reduced_metamodel_selected_data(self):
        """Updates the list of selected variables for reduced model
        construction whenever alias or expression data is changed (SLOT)."""

        if not hasattr(self, '_reduced_metamodel_selected_data'):
            # attribute not created (init), create now
            self._reduced_metamodel_selected_data = pd.DataFrame(
                columns=self._META_SELEC_COLS
            )

        return self._reduced_metamodel_selected_data

    @reduced_metamodel_selected_data.setter
    def reduced_metamodel_selected_data(self, value: pd.DataFrame):
        if isinstance(value, pd.DataFrame):
            if value.columns.isin(self._META_SELEC_COLS).all():
                self._reduced_metamodel_selected_data = value
                self.reduced_selected_data_changed.emit()
            else:
                raise ValueError("'reduced_metamodel_selected_data' must have "
                                 "its columns defined.")
        else:
            raise TypeError("Reduced selected data must be a DataFrame.")

    @property
    def differential_regression_model(self):
        """The Kriging regression model to be used in reduced space model."""
        return self._hessian_data['regression']

    @differential_regression_model.setter
    def differential_regression_model(self, value: str):
        if value not in ['poly0', 'poly1', 'poly2']:
            raise ValueError("Invalid regression model.")
        else:
            self._hessian_data['regression'] = value

    @property
    def differential_correlation_model(self):
        """The Kriging correlation model to be used in reduced space model."""
        return self._hessian_data['correlation']

    @differential_correlation_model.setter
    def differential_correlation_model(self, value: str):
        if value != 'corrgauss':
            raise ValueError("Invalid correlation model.")
        else:
            self._hessian_data['correlation'] = value

    @property
    def differential_gy(self):
        """Gradient of reduced space (Gy)."""
        return self._hessian_data['gy']

    @differential_gy.setter
    def differential_gy(self, value: dict):
        if isinstance(value, dict):
            self._hessian_data['gy'] = value
            self.differential_gy_data_changed.emit('gy')
        else:
            raise ValueError("Gy must be a dictionary.")

    @property
    def differential_gyd(self):
        """Gradient of reduced space (Gyd)."""
        return self._hessian_data['gyd']

    @differential_gyd.setter
    def differential_gyd(self, value: dict):
        if isinstance(value, dict):
            self._hessian_data['gyd'] = value
            self.differential_gyd_data_changed.emit('gyd')
        else:
            raise ValueError("Gyd must be a dictionary.")

    @property
    def differential_juu(self):
        """Hessian of reduced space (Juu)."""
        return self._hessian_data['juu']

    @differential_juu.setter
    def differential_juu(self, value: dict):
        if isinstance(value, dict):
            self._hessian_data['juu'] = value
            self.differential_juu_data_changed.emit('juu')
        else:
            raise ValueError("Juu must be a dictionary.")

    @property
    def differential_jud(self):
        """Hessian of reduced space (Jud)."""
        return self._hessian_data['jud']

    @differential_jud.setter
    def differential_jud(self, value: dict):
        if isinstance(value, dict):
            self._hessian_data['jud'] = value
            self.differential_jud_data_changed.emit('jud')
        else:
            raise ValueError("Jud must be a dictionary.")

    @property
    def soc_disturbance_magnitude(self):
        """Disturbances magnitude values."""
        return self._soc_data['md']

    @soc_disturbance_magnitude.setter
    def soc_disturbance_magnitude(self, value: dict):
        if isinstance(value, dict):
            self._soc_data['md'] = value
            self.soc_dist_mag_data_changed.emit('disturbance')
        else:
            raise ValueError("md must be a dictionary.")

    @property
    def soc_measure_error_magnitude(self):
        """Measurement error magnitude values."""
        return self._soc_data['me']

    @soc_measure_error_magnitude.setter
    def soc_measure_error_magnitude(self, value: dict):
        if isinstance(value, dict):
            self._soc_data['me'] = value
            self.soc_meas_mag_data_changed.emit('error')
        else:
            raise ValueError("me must be a dictionary.")

    @property
    def soc_subset_size_list(self):
        """The soc_subset_size_list property."""
        return self._soc_data['ss_list']

    @soc_subset_size_list.setter
    def soc_subset_size_list(self, value: dict):
        if isinstance(value, dict):
            self._soc_data['ss_list'] = value
            self.soc_subset_data_changed.emit()
        else:
            raise ValueError("Subset sizes must be a dictionary.")

    # ---------------------------- PRIVATE METHODS ---------------------------
    def _uneven_array_to_frame(self, arr: dict) -> pd.DataFrame:
        """Converts an uneven array represented by a dict into a DataFrame.
        Empty fields are filled with NaN.

        Parameters
        ----------
        arr : dict
            Uneven array represented by a dict.

        Returns
        -------
        pd.DataFrame
            DataFrame representation of a different length array where empty
            fields are represented by NaN
        """
        if isinstance(arr, dict):
            dict_conversion = dict([(k, pd.Series(v)) for k, v in arr.items()])
            return pd.DataFrame(dict_conversion).fillna(value=pd.np.nan)
        else:
            raise ValueError("'arr' has to be a dictionary.")

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
        """Updates the MV bounds data whenever input alias data is changed.
        (SLOT)
        """
        # list of aliases that are MV
        inps = self.input_table_data
        mv_aliases = inps.loc[inps['Type'] == self._INPUT_ALIAS_TYPES['mv'],
                              'Alias'].tolist()

        # delete the variables that aren't in the mv list
        bnd_df = self.doe_mv_bounds
        new_bnds = bnd_df[bnd_df['name'].isin(mv_aliases)]

        mv_bnd_list = new_bnds['name'].tolist()

        # insert new values
        nv = []
        for alias in mv_aliases:
            if alias not in mv_bnd_list:
                nv.append({
                    'name': alias,
                    'lb': 0.0,
                    'ub': 1.0
                })

        new_bnds = pd.concat([new_bnds, pd.DataFrame.from_records(nv)],
                             axis='index', ignore_index=True)

        # sort frame to ensure that the order is the same as input table
        new_bnds.set_index('name', inplace=True)
        new_bnds = new_bnds.loc[mv_aliases, :]
        new_bnds.reset_index(inplace=True)
        new_bnds = new_bnds.loc[:, self._INP_BOUNDS_COLS]

        # store values
        self.doe_mv_bounds = new_bnds

    def _update_theta_data(self) -> None:
        """Updates the theta list whenever alias data is changed. (SLOT)
        """
        # list of aliases that are MV
        inps = self.input_table_data
        input_aliases = inps.loc[inps['Type'] == self._INPUT_ALIAS_TYPES['mv'],
                                 'Alias'].tolist()

        # delete the variables that aren't in the mv list
        theta_df = self.metamodel_theta_data
        new_thetas = theta_df[theta_df['Alias'].isin(input_aliases)]

        theta_bnd_list = theta_df['Alias'].tolist()

        # insert new values
        nt = []
        for alias in input_aliases:
            if alias not in theta_bnd_list:
                nt.append({
                    'Alias': alias,
                    'lb': 1e-5,
                    'ub': 1.0e5,
                    'theta0': 1.0
                })

        new_thetas = pd.concat([new_thetas, pd.DataFrame.from_records(nt)],
                               axis='index', ignore_index=True)

        # sort frame to ensure that the order is the same as input table
        new_thetas.set_index('Alias', inplace=True)
        new_thetas = new_thetas.loc[input_aliases, :]
        new_thetas.reset_index(inplace=True)
        new_thetas = new_thetas.loc[:, self._META_THETA_BNDS]

        # store values
        self.metamodel_theta_data = new_thetas

    def _update_selected_data(self) -> None:
        """Updates the list of selected variables for model construction
        whenever alias or expression data is changed (SLOT).
        """
        # list of variables
        conc_tab = pd.concat([self.output_table_data,
                              self.expression_table_data],
                             axis='index', join='inner',
                             ignore_index=True
                             ).drop_duplicates().reset_index(drop=True)
        var_list = conc_tab.loc[
            (conc_tab['Type'] == self._OUTPUT_ALIAS_TYPES['cv']) |
            (conc_tab['Type'].isin(self._EXPR_ALIAS_TYPES.values()))
        ]

        # set the var_list index to the aliases (easier indexing)
        var_list.set_index('Alias', inplace=True)

        # list of aliases
        aliases = var_list.index.tolist()

        # delete variables that aren't in the list
        sel_df = self.metamodel_selected_data
        new_vars = sel_df[~sel_df['Alias'].isin(aliases)]
        new_vars_list = new_vars['Alias'].tolist()

        # insert new variables
        nv = []
        for alias in aliases:
            if alias not in new_vars_list:
                nv.append({
                    'Alias': alias,
                    'Type': var_list.at[alias, 'Type'],
                    'Checked': False
                })

        new_vars = pd.concat([new_vars, pd.DataFrame.from_records(nv)],
                             axis='index', ignore_index=True)

        # sort frame to ensure that the order is the same as output table
        new_vars.set_index('Alias', inplace=True)
        new_vars = new_vars.loc[aliases, :]
        new_vars.reset_index(inplace=True)
        new_vars = new_vars.loc[:, self._META_SELEC_COLS]

        # store values
        self.metamodel_selected_data = new_vars

    def _update_reduced_space_dof(self) -> None:
        inp_tab = self.input_table_data
        aliases = inp_tab.loc[
            inp_tab['Type'] == self._INPUT_ALIAS_TYPES['mv'],
            'Alias'
        ].tolist()

        dof_df = self.reduced_space_dof
        # delete the variables that aren't in the mv list
        new_vars = dof_df.loc[
            dof_df[self._RED_SPACE_DOF_COLS[0]].isin(aliases),
            :
        ]
        new_vars_list = new_vars['Alias'].tolist()

        # insert new values from input table
        nv = []
        for alias in aliases:
            if alias not in new_vars_list:
                nv.append({
                    'Alias': alias,
                    'Checked': False
                })

        new_vars = pd.concat([new_vars, pd.DataFrame.from_records(nv)],
                             ignore_index=True, axis='index')

        # sort frame to ensure that the order is the same as input table
        new_vars.set_index('Alias', inplace=True)
        new_vars = new_vars.loc[aliases, :]
        new_vars.reset_index(inplace=True)
        new_vars = new_vars.loc[:, self._RED_SPACE_DOF_COLS]

        # store values
        self.reduced_space_dof = new_vars

    def _update_active_candidates(self) -> None:
        out_data = self.output_table_data
        exp_data = self.expression_table_data

        var_tab = pd.concat([out_data, exp_data], axis='index',
                            ignore_index=True)
        aliases = var_tab.loc[
            (var_tab['Type'] == self._OUTPUT_ALIAS_TYPES['cv']) |
            (var_tab['Type'] == self._EXPR_ALIAS_TYPES['cv']),
            'Alias'
        ].tolist()
        act_df = self.active_candidates

        # delete the variables that aren't in the mv list
        new_vars = act_df.loc[
            act_df[self._RED_SPACE_ACT_COLS[0]].isin(aliases),
            :
        ]
        new_vars_list = new_vars['Alias'].tolist()

        # insert new values from input table
        nv = []
        for alias in aliases:
            if alias not in new_vars_list:
                nv.append({
                    'Alias': alias,
                    'Checked': False
                })

        new_vars = pd.concat([new_vars, pd.DataFrame.from_records(nv)],
                             ignore_index=True, axis='index')

        # sort frame to ensure that the order is the same as input table
        new_vars.set_index('Alias', inplace=True)
        new_vars = new_vars.loc[aliases, :]
        new_vars.reset_index(inplace=True)
        new_vars = new_vars.loc[:, self._RED_SPACE_ACT_COLS]

        # store values
        self.active_candidates = new_vars

    def _update_reduced_d_bounds(self) -> None:
        """Updates the reduced space disturbance bounds data whenever input
        alias data is changed. (SLOT)
        """
        # list of aliases that are D
        inps = self.input_table_data
        d_aliases = inps.loc[inps['Type'] == self._INPUT_ALIAS_TYPES['d'],
                             'Alias'].tolist()

        red_dof = self.reduced_space_dof
        non_consumed_aliases = red_dof.loc[red_dof['Checked'], 'Alias'].tolist(
        )

        input_aliases = d_aliases + non_consumed_aliases

        # delete the variables that aren't in the mv list
        bnd_df = self.reduced_doe_d_bounds
        new_bnds = bnd_df[bnd_df['name'].isin(input_aliases)]

        bnd_list = new_bnds['name'].tolist()

        # insert new values
        nv = []
        for alias in input_aliases:
            if alias in self.optimization_results.index:
                # set default values from optimization
                nom = self.optimization_results.at[alias]
            else:
                nom = 0.5

            if alias not in bnd_list:
                nv.append({
                    'name': alias,
                    'lb': 0.0,
                    'ub': 1.0,
                    'nominal': nom
                })

        new_bnds = pd.concat([new_bnds, pd.DataFrame.from_records(nv)],
                             axis='index', ignore_index=True)

        # sort frame to ensure that the order is the same as input table
        new_bnds.set_index('name', inplace=True)
        new_bnds = new_bnds.loc[input_aliases, :]
        new_bnds.reset_index(inplace=True)
        new_bnds = new_bnds.loc[:, self._REDSPACE_BNDS_COLS]

        # store values
        self.reduced_doe_d_bounds = new_bnds

    def _update_reduced_theta_data(self) -> None:
        """Updates the reduced model theta list whenever alias data is changed.
        (SLOT) - associated with alias and constraint activity change.
        """
        # list of aliases that are D
        inps = self.input_table_data
        d_aliases = inps.loc[inps['Type'] == self._INPUT_ALIAS_TYPES['d'],
                             'Alias'].tolist()

        red_dof = self.reduced_space_dof
        non_consumed_aliases = red_dof.loc[red_dof['Checked'], 'Alias'].tolist(
        )

        input_aliases = d_aliases + non_consumed_aliases

        # delete the variables that aren't in the mv list
        theta_df = self.reduced_metamodel_theta_data
        new_thetas = theta_df[theta_df['Alias'].isin(input_aliases)]

        theta_bnd_list = theta_df['Alias'].tolist()

        # insert new values
        nt = []
        for alias in input_aliases:
            if alias not in theta_bnd_list:
                nt.append({
                    'Alias': alias,
                    'lb': 1e-12,
                    'ub': 1e-3,
                    'theta0': 1e-6
                })

        new_thetas = pd.concat([new_thetas, pd.DataFrame.from_records(nt)],
                               axis='index', ignore_index=True)

        # sort frame to ensure that the order is the same as input table
        new_thetas.set_index('Alias', inplace=True)
        new_thetas = new_thetas.loc[input_aliases, :]
        new_thetas.reset_index(inplace=True)
        new_thetas = new_thetas.loc[:, self._META_THETA_BNDS]

        # # store values
        self.reduced_metamodel_theta_data = new_thetas

    def _update_reduced_selected_data(self) -> None:
        """Updates the list of selected variables for model construction
        whenever alias or expression data is changed (SLOT) - associated with
        alias and constraint activity change."""
        # list of non active constraints

        act_cvars = self.active_candidates

        non_act_aliases = act_cvars.loc[
            ~ act_cvars['Checked'].astype(bool),
            'Alias'
        ].tolist()

        act_aliases = act_cvars.loc[
            act_cvars['Checked'],
            'Alias'
        ].tolist()

        conc_tab = pd.concat([self.output_table_data,
                              self.expression_table_data],
                             axis='index', join='inner',
                             ignore_index=True
                             ).drop_duplicates().reset_index(drop=True)

        var_list = conc_tab.loc[
            (~conc_tab['Alias'].isin(act_aliases)) &
            (
                (conc_tab['Type'] == self._OUTPUT_ALIAS_TYPES['cv']) |
                (conc_tab['Type'] == self._EXPR_ALIAS_TYPES['obj'])
            ),
            ['Alias', 'Type']
        ]

        # set the var_list index to the aliases (easier indexing)
        var_list.set_index('Alias', inplace=True)

        # list of aliases
        aliases = var_list.index.tolist()

        # delete variables that aren't in the list
        sel_df = self.reduced_metamodel_selected_data
        new_vars = sel_df[~sel_df['Alias'].isin(aliases)]
        new_vars_list = new_vars['Alias'].tolist()

        # insert new variables
        nv = []
        for alias in aliases:
            if alias not in new_vars_list:
                nv.append({
                    'Alias': alias,
                    'Type': var_list.at[alias, 'Type'],
                    'Checked': True
                })

        new_vars = pd.concat([new_vars, pd.DataFrame.from_records(nv)],
                             axis='index', ignore_index=True)

        # sort frame to ensure that the order is the same as output table
        new_vars.set_index('Alias', inplace=True)
        new_vars = new_vars.loc[aliases, :]
        new_vars.reset_index(inplace=True)
        new_vars = new_vars.loc[:, self._META_SELEC_COLS]

        # # store values
        self.reduced_metamodel_selected_data = new_vars

    def _update_magnitude_data(self) -> None:
        """Updates the distubance and measurement error magnitudes whenever
        alias data changes. (SLOT)"""
        # disturbances
        inps = self.input_table_data
        d_aliases = inps.loc[inps['Type'] == self._INPUT_ALIAS_TYPES['d'],
                             'Alias'].tolist()
        # d_aliases = [row['Alias'] for row in self.input_table_data
        #              if row['Type'] == 'Disturbance (d)']

        # delete vars
        soc_d = copy.deepcopy(self.soc_disturbance_magnitude)
        for dist in self.soc_disturbance_magnitude:
            if dist not in d_aliases:
                del soc_d[dist]

        # insert new keys
        [soc_d.update({d: None}) for d in d_aliases if d not in soc_d]

        self.soc_disturbance_magnitude = {'Value': soc_d}

        # measurement errors
        t_data = self.reduced_metamodel_selected_data
        y_aliases = t_data.loc[
            (t_data['Checked']) &
            (t_data['Type'] == self._OUTPUT_ALIAS_TYPES['cv']), 'Alias'
        ].tolist()
        # y_aliases = [row['Alias']
        #              for row in self.reduced_metamodel_selected_data
        #              if row['Type'] == 'Candidate (CV)'
        #              and row['Checked']]

        # delete vars
        soc_me = copy.deepcopy(self.soc_measure_error_magnitude)
        for me in self.soc_measure_error_magnitude:
            if me not in y_aliases:
                del soc_me[me]

        # insert new keys
        [soc_me.update({y: None}) for y in y_aliases if y not in soc_me]

        self.soc_measure_error_magnitude = {'Value': soc_me}

    def _update_subset_data(self) -> None:
        """Updates the subset size list whenever alias or expression data
        changes. (SLOT)"""
        # list of aliases that are reduced space CV's
        t_data = self.reduced_metamodel_selected_data
        y_aliases = t_data.loc[
            (t_data['Checked']) &
            (t_data['Type'] == self._OUTPUT_ALIAS_TYPES['cv']), 'Alias'
        ].tolist()

        # possible number of subset
        n_y_list = len(y_aliases)

        red_dof = self.reduced_space_dof
        non_consumed_aliases = red_dof.loc[red_dof['Checked'], 'Alias'].tolist(
        )

        n_u = 1 if len(non_consumed_aliases) == 0 else len(
            non_consumed_aliases)

        # starting from subsets of size 1 to n_y_list
        self.soc_subset_size_list = {str(y):
                                     {'Subset number': 1}
                                     for y in range(n_u, n_y_list + 1)}

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
            'opt_info': {
                'mtc_opt_results': self.optimization_results,
                'mtc_optimization_parameters': self.optimization_parameters
            },
            'reduced_space_info': {
                'mtc_reduced_space_dof': self.reduced_space_dof,
                'mtc_reduced_active_candidates': self.active_candidates,
                'mtc_reduced_d_bounds': self.reduced_doe_d_bounds,
                'mtc_reduced_sampled_data': self.reduced_doe_sampled_data
            },
            'differential_info': {
                'mtc_gy': self.differential_gy,
                'mtc_gyd': self.differential_gyd,
                'mtc_juu': self.differential_juu,
                'mtc_jud': self.differential_jud
            },
            'soc_info': {
                'mtc_disturbance_magnitude': self.soc_disturbance_magnitude,
                'mtc_measurement_magnitude': self.soc_measure_error_magnitude,
                'mtc_subset_sizing_data': self.soc_subset_size_list
            }
        }

        # perfom the JSON dump
        with open(output_path, 'w') as mtc_file:
            json.dump(app_data, mtc_file, indent=4, cls=PandasEncoder,
                      ignore_nan=True)

    def load(self, mtc_filepath: str) -> None:
        """Reads .mtc file data and updates the object attributes.

        Parameters
        ----------
        mtc_filepath : str
            Filepath to the .mtc file to be read.
        """
        # FIXME: block signals when assigning variableas and fire specific ones
        # load the JSON file
        with open(mtc_filepath, 'r') as mtc_file:
            app_data = json.load(mtc_file)

        sim_info = app_data['simulation_info']
        doe_info = app_data['doe_info']
        opt_info = app_data['opt_info']
        redspace_info = app_data['reduced_space_info']
        diff_info = app_data['differential_info']
        soc_info = app_data['soc_info']

        # loadsimtab
        try:
            self.simulation_file = sim_info['sim_filename']
        except FileNotFoundError:
            msg_tile = 'File not found!'
            msg_str = ("The .bkp file specified in the .mtc could not "
                       "be found!\nPlease, load the .bkp file that "
                       "corresponds to this setup.")
            warn_the_user(msg_text=msg_str, msg_title=msg_tile)
            self.simulation_file = ''

        self.simulation_data = self._uneven_array_to_frame(
            sim_info['sim_info'])
        self.tree_model_input = sim_info['sim_tree_input']
        self.tree_model_output = sim_info['sim_tree_output']
        self.input_table_data = pd.DataFrame(sim_info['mtc_input_table'])
        self.output_table_data = pd.DataFrame(sim_info['mtc_output_table'])
        self.expression_table_data = pd.DataFrame(sim_info['mtc_expr_table'])

        # # doetab
        self.doe_mv_bounds = pd.DataFrame(doe_info['mtc_mv_bounds'])
        self.doe_sampled_data = pd.DataFrame(doe_info['mtc_sampled_data'])

        # optimization tab
        self.optimization_parameters = opt_info['mtc_optimization_parameters']

        # reducedpsacetab
        self.reduced_space_dof = pd.DataFrame(
            redspace_info['mtc_reduced_space_dof'])
        self.active_candidates = pd.DataFrame(
            redspace_info['mtc_reduced_active_candidates'])
        self.reduced_doe_d_bounds = pd.DataFrame(
            redspace_info['mtc_reduced_d_bounds'])
        self.reduced_doe_sampled_data = pd.DataFrame(
            redspace_info['mtc_reduced_sampled_data'])

        # hessianextraction tab
        self.differential_gy = diff_info['mtc_gy']
        self.differential_gyd = diff_info['mtc_gyd']
        self.differential_juu = diff_info['mtc_juu']
        self.differential_jud = diff_info['mtc_jud']

        # soc tab
        self.soc_disturbance_magnitude = soc_info['mtc_disturbance_magnitude']
        self.soc_measure_error_magnitude = soc_info['mtc_measurement_magnitude']
        self.soc_subset_size_list = soc_info['mtc_subset_sizing_data']

    def check_simulation_setup(self):
        """Checks if there are aliases and expressions are mathematically
        valid. Also checks if expression types are defined, and there are no
        duplicates between expression names and variable aliases.

        If everything is ok, emits a signal with a boolean value where True
        means that the sampling phase is good to go, otherwise the value is
        False.
        """
        # check if the bkp file is valid
        fpath = pathlib.Path(self.simulation_file)
        is_bkp_valid = fpath.exists() and fpath.is_file()

        # get aliases
        aliases = pd.concat([self.input_table_data, self.output_table_data],
                            axis='index', ignore_index=True, sort=False)

        # get expressions validity
        expr_df = self.expression_table_data
        expr_valid_check = expr_df['Expression'].apply(
            lambda x: is_expression_valid(x, aliases['Alias'].tolist())
        )

        is_name_not_duplicated = pd.concat(
            [aliases['Alias'], expr_df['Alias']],
            axis='index', ignore_index=True
        ).is_unique and not aliases.empty and not expr_df.empty

        # expressions check is True if all expressions are valid and not empty
        is_exprs_valid = not expr_df.empty and expr_valid_check.all()

        is_expr_defined = expr_df['Type'].ne('Choose a type').any() and \
            not expr_df.empty

        if is_exprs_valid and is_name_not_duplicated and is_expr_defined \
                and is_bkp_valid:
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
        # check if the bkp file is valid
        fpath = pathlib.Path(self.simulation_file)
        is_bkp_valid = fpath.exists() and fpath.is_file()

        inp_data = self.input_table_data
        out_data = self.output_table_data
        expr_data = self.expression_table_data
        input_alias = inp_data.loc[
            inp_data['Type'] == self._INPUT_ALIAS_TYPES['mv'], 'Alias'
        ].tolist()
        output_alias = out_data.loc[:, 'Alias'].tolist()
        expr_alias = expr_data.loc[:, 'Alias'].tolist()
        aliases = input_alias + output_alias + expr_alias

        # build the DataFrame
        df = self.doe_sampled_data

        is_sampling_empty = df.empty

        is_alias_sampled = all(alias in df.columns for alias in aliases)

        if is_alias_sampled and not is_sampling_empty and is_bkp_valid:
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
        dof_df = self.reduced_space_dof
        act_cvs = self.active_candidates

        # check if reduced space doe is sampled
        red_df = self.reduced_doe_sampled_data

        is_sampling_empty = red_df.empty

        if dof_df.empty or act_cvs.empty:
            # empty active contraint info object
            is_dof_set = False

        else:
            # check if at least one dof is checked
            is_dof_set = dof_df['Checked'].any()

        if is_dof_set and not is_sampling_empty:
            self.hessian_enabled.emit(True)
        else:
            self.hessian_enabled.emit(False)

    def check_hessian_setup(self):
        """Checks if the gradients and hessian are set.

        If everything is ok, emits a signal with a boolean value where True
        means that the SOC phase is good to go, otherwise the value is False.
        """
        is_gy_empty = pd.DataFrame(self.differential_gy).empty
        is_gyd_empty = pd.DataFrame(self.differential_gyd).empty
        is_juu_empty = pd.DataFrame(self.differential_juu).empty
        is_jud_empty = pd.DataFrame(self.differential_jud).empty

        if not is_gy_empty and not is_gyd_empty and not is_juu_empty and \
                not is_jud_empty:
            self.soc_enabled.emit(True)
        else:
            self.soc_enabled.emit(False)

    def evaluate_expr_data(self, sampled_data: pd.DataFrame,
                           space_type: str) -> pd.DataFrame:
        """Evaluates the expressions and append values to the current sampled
        data.

        Parameters
        ----------
        sampled_data: pd.DataFrame
            Sampled data.
        space_type : str
            Which space the data represents: 'original' or 'reduced'

        Returns
        -------
        out : pd.DataFrame
            The complete dataframe with expressions evaluated as a DataFrame.
        """
        if space_type not in ['original', 'reduced']:
            raise ValueError("The space type must be 'original' or 'reduced'.")

        aliases = pd.concat([self.input_table_data, self.output_table_data],
                            axis='index', ignore_index=True, sort=False)

        if space_type == 'original':
            hdr = aliases.loc[aliases['Type'] != self._INPUT_ALIAS_TYPES['d'],
                              'Alias'].tolist()
        else:
            hdr = aliases.loc[:, 'Alias'].tolist()

        df_headers = ['case', 'status'] + hdr
        if not sampled_data.empty:
            sampled_data = sampled_data[df_headers]
        else:
            sampled_data = pd.DataFrame(columns=df_headers)

        # intialize empty dataframe
        expr_df = pd.DataFrame(columns=self.expression_table_data['Alias'])

        parser = Parser()

        for idx, row in sampled_data.iterrows():
            row_val_dict = row.to_dict()  # convert row series to dict
            expr_row_values = {}

            for _, expr in self.expression_table_data.iterrows():
                expr_to_parse = parser.parse(expr['Expression'])
                var_list = expr_to_parse.variables()
                expr_row_values[expr['Alias']] = expr_to_parse.evaluate(
                    row_val_dict)

            # append values to expr_df
            expr_df = expr_df.append(expr_row_values, ignore_index=True)

        # merge sampled data and expression data and store them, if they don't
        # already exist
        if expr_df.columns.difference(sampled_data.columns).size != 0:
            sampled_data = sampled_data.merge(expr_df, left_index=True,
                                              right_index=True)

        return sampled_data
