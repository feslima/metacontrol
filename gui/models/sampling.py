import numpy as np
import pandas as pd
import pythoncom
import win32com.client
from py_expression_eval import Parser
from pydace.utils import lhsdesign
from PyQt5.QtCore import QObject, QThread, pyqtSignal
# import ptvsd

from surropt.caballero import Caballero, CaballeroOptions
from surropt.caballero.problem import CaballeroReport
from surropt.core.options.nlp import DockerNLPOptions, IpOptOptions

from gui.models.data_storage import DataStorage
from gui.models.sim_connections import AspenConnection


def lhs(n_samples: int, lb: list, ub: list, n_iter: int, inc_vertices: bool) \
        -> np.ndarray:
    lb = np.asarray(lb)
    ub = np.asarray(ub)

    return lhsdesign(n_samples, lb, ub, k=n_iter,
                     include_vertices=inc_vertices)


class SamplerThread(QThread):
    """
    Sampling thread that opens the aspen connection to keep the sampling
    assistant GUI responsive while the sampling is
    performed
    """

    case_sampled = pyqtSignal(int, object)

    def __init__(self, input_design_data: pd.DataFrame, app_data: DataStorage,
                 parent=None):
        QThread.__init__(self, parent)
        self._input_des_data = input_design_data
        self._app_data = app_data

        # https://stackoverflow.com/questions/26764978/using-win32com-with-multithreading
        # initialize
        pythoncom.CoInitialize()
        self._aspen_connection = AspenConnection(app_data.simulation_file)

        # create id
        self._aspen_id = pythoncom.CoMarshalInterThreadInterfaceInStream(
            pythoncom.IID_IDispatch,
            self._aspen_connection.get_connection_object())

        # clean up
        self.finished.connect(self.__del__)

    def __del__(self):
        # kill the connection on thread cleanup
        self._aspen_connection.close_connection()

    def run(self):
        # ptvsd.debug_this_thread()
        # initialize
        pythoncom.CoInitialize()

        # get instance from id
        aspen_con = win32com.client.Dispatch(
            pythoncom.CoGetInterfaceAndReleaseStream(
                self._aspen_id, pythoncom.IID_IDispatch)
        )
        inp_data = self._app_data.input_table_data
        out_data = self._app_data.output_table_data
        input_vars = inp_data.loc[
            inp_data['Type'] == self._app_data._INPUT_ALIAS_TYPES['mv'],
            ['Alias', 'Path']
        ].to_dict(orient='records')
        output_vars = out_data.loc[:,
                                   ['Alias', 'Path']].to_dict(orient='records')

        for row in range(self._input_des_data.shape[0]):
            [var.update({'value': self._input_des_data.loc[row, var['Alias']]})
             for var in input_vars]
            self.case_sampled.emit(row + 1,
                                   run_case(input_vars, output_vars, aspen_con)
                                   )

            if self.isInterruptionRequested():  # to allow task abortion
                return


class ReducedSamplerThread(SamplerThread):
    def __init__(self, input_design_data: pd.DataFrame,
                 app_data: DataStorage, bkp_filepath: str, parent=None):
        QThread.__init__(self, parent)
        self._input_des_data = input_design_data
        self._app_data = app_data

        # initialize
        pythoncom.CoInitialize()
        self._aspen_connection = AspenConnection(bkp_filepath)

        # create id
        self._aspen_id = pythoncom.CoMarshalInterThreadInterfaceInStream(
            pythoncom.IID_IDispatch,
            self._aspen_connection.get_connection_object())

        # clean up
        self.finished.connect(self.__del__)

    def run(self):
        # ptvsd.debug_this_thread()
        # initialize
        pythoncom.CoInitialize()

        # get instance from id
        aspen_con = win32com.client.Dispatch(
            pythoncom.CoGetInterfaceAndReleaseStream(
                self._aspen_id, pythoncom.IID_IDispatch)
        )
        inp_data = self._app_data.input_table_data
        out_data = self._app_data.output_table_data
        # TODO: move consumed aliases from input into output collection
        inp_data_ph = inp_data.set_index('Alias')
        red_inp_alias = self._app_data.reduced_doe_d_bounds.loc[
            :, 'name'].tolist()
        output_mvs = inp_data.loc[~inp_data['Alias'].isin(red_inp_alias)]
        input_vars = inp_data_ph.loc[red_inp_alias,
                                     'Path'].reset_index().to_dict(orient='records')
        output_vars = pd.concat([out_data.loc[:, ['Alias', 'Path']],
                                 output_mvs], ignore_index=True,
                                axis='index', sort=False).to_dict(orient='records')

        for row in range(self._input_des_data.shape[0]):
            [var.update({'value': self._input_des_data.loc[row, var['Alias']]})
             for var in input_vars]
            self.case_sampled.emit(row + 1,
                                   run_case(input_vars, output_vars, aspen_con)
                                   )

            if self.isInterruptionRequested():  # to allow task abortion
                return


def run_case(mv_values: list, output_data: list, aspen_obj):
    """
    Samples a single case of DOE.

    Parameters
    ----------
    mv_values : list
        List containing all the design values to sample.
    output_data : list
        List containing all the output variables info to sample.
    aspen_obj : COM object
        Object connection handle.

    Returns
    -------
    dict
        Dictionary with output alias as keys and values as data sampled.
    """

    # get the paths to feed to the aspen obj
    for var in mv_values:
        aspen_obj.Tree.FindNode(var['Path']).Value = var['value']

    # run the engine
    aspen_obj.Engine.Run2()

    # get the output
    res_dict = {}
    UOSTAT2_val = aspen_obj.Tree.FindNode(
        r"\Data\Results Summary\Run-Status\Output\UOSSTAT2").Value
    if UOSTAT2_val == 8:
        res_dict['success'] = 'ok'
        for out_var in output_data:
            res_dict[out_var['Alias']] = aspen_obj.Tree.FindNode(
                out_var['Path']).Value
    else:
        res_dict['success'] = 'error'
        for out_var in output_data:
            res_dict[out_var['Alias']] = np.spacing(1)

    return res_dict


class SamplerWorker(QObject):

    def __init__(self, app_data: DataStorage,
                 marshalled_sim_id):
        self.app_data = app_data
        self.marshall_id = marshalled_sim_id
        # alias to index mapping of variables for easy access
        self.inp_aliases = {var['Alias']: idx for var, idx in
                            enumerate(self.app_data.input_table_data)}

    def sample_case(self, mv_values: dict):
        """Samples a single case based on values provided in `mv_values`.

        Parameters
        ----------
        mv_values : dict
            Dictionary where the keys are the aliases of the input variables
            and the values are the numeric values of each variable.
        """

        pythoncom.CoInitialize()
        aspen_obj = win32com.client.Dispatch(
            pythoncom.CoGetInterfaceAndReleaseStream(self.marshall_id,
                                                     pythoncom.IID_IDispatch)
        )

        # set input values
        for alias, value in mv_values.items():
            if alias in self.inp_aliases:
                # if the value exists in the input variables, set it in the
                # simulation
                row = self.app_data.input_table_data[self.inp_aliases[alias]]
                aspen_obj.Tree.FindNode(row['Path']).Value = value

        # get the output
        res_dict = {}
        UOSTAT2_val = aspen_obj.Tree.FindNode(
            r"\Data\Results Summary\Run-Status\Output\UOSSTAT2").Value
        if UOSTAT2_val == 8:
            res_dict['success'] = True
            for out_var in self.app_data.output_table_data:
                res_dict[out_var['Alias']] = aspen_obj.Tree.FindNode(
                    out_var['Path']).Value

        else:
            res_dict['success'] = False
            for out_var in self.app_data.output_table_data:
                res_dict[out_var['Alias']] = 1.0

        pythoncom.CoUninitialize()  # unmarshal the thread
        return res_dict


class ReportObject(CaballeroReport):

    def __init__(self, iteration_printed, terminal=False, plot=False):
        CaballeroReport.__init__(self, terminal=terminal, plot=plot)
        self.iteration_printed = iteration_printed

    def build_iter_report(self, movement, iter_count, x, f_pred, f_actual,
                          g_actual, header=False, field_size=12):
        # capture message from Report class and send it to the gui
        str_msg = super().build_iter_report(movement, iter_count, x, f_pred,
                                            f_actual, g_actual, header=header,
                                            field_size=field_size)
        self.iteration_printed.emit(str_msg)
        return str_msg

    def get_results_report(self, index, r, x, f, lb, ub, fun_evals):
        res_msg = super().get_results_report(index, r, x, f, lb, ub, fun_evals)
        self.iteration_printed.emit(res_msg)
        return res_msg


class CaballeroWorker(QObject):
    optimization_finished = pyqtSignal()
    results_ready = pyqtSignal(object)

    def __init__(self, app_data: DataStorage, params: dict,
                 iteration_printed: pyqtSignal,
                 opening_connection: pyqtSignal,
                 connection_opened: pyqtSignal):
        QObject.__init__(self)

        self.app_data = app_data
        self.params = params
        self.parser = Parser()
        self.iteration_printed = iteration_printed
        self.opening_connection = opening_connection
        self.connection_opened = connection_opened

    def __del__(self):
        if hasattr(self, 'asp_obj'):
            self.asp_obj.close_connection()

    def start_optimization(self):
        # ptvsd.debug_this_thread()
        params = self.params

        # unzip parameter data
        first_factor = params['first_factor']
        sec_factor = params['sec_factor']
        tol_contract = params['tol_contract']
        con_tol = params['con_tol']
        penalty = params['penalty']
        tol1 = params['tol1']
        tol2 = params['tol2']
        maxfunevals = params['maxfunevals']
        regrpoly = params['regrpoly']

        nlp_params = params['nlp_dict']

        # setup the problem data
        inp_data = self.app_data.input_table_data
        expr_data = self.app_data.expression_table_data

        inp_aliases = inp_data.loc[
            inp_data['Type'] == self.app_data._INPUT_ALIAS_TYPES['mv'],
            'Alias'].tolist()
        con_aliases = expr_data.loc[
            expr_data['Type'] == self.app_data._EXPR_ALIAS_TYPES['cst'],
            'Alias'].tolist()
        obj_alias = expr_data.loc[
            expr_data['Type'] == self.app_data._EXPR_ALIAS_TYPES['obj'],
            'Alias'].tolist()

        doe = self.app_data.doe_sampled_data
        x = doe.loc[:, inp_aliases].to_numpy()
        g = doe.loc[:, con_aliases].to_numpy()
        f = doe.loc[:, obj_alias].to_numpy().flatten()

        # open the aspen connection
        self.open_connection()

        # define model function
        def model_fun(pt): return self.model_function(pt)

        # nlp bounds
        lb_list = self.app_data.doe_mv_bounds.loc[:, 'lb'].tolist()
        ub_list = self.app_data.doe_mv_bounds.loc[:, 'ub'].tolist()

        # nlp options (assumes that the user already tested the connection)
        if nlp_params['solver'] == "ipopt_server":
            server_url = nlp_params['server_url']
            ipopt_tol = nlp_params['ipopt_tol']
            ipopt_max_iter = nlp_params['ipopt_max_iter']
            ipopt_con_tol = nlp_params['ipopt_con_tol']
            nlp_opts = DockerNLPOptions(name='nlp-server',
                                        server_url=server_url,
                                        tol=ipopt_tol,
                                        max_iter=ipopt_max_iter,
                                        con_tol=ipopt_con_tol)

        elif nlp_params['solver'] == "ipopt_local":
            ipopt_tol = nlp_params['ipopt_tol']
            ipopt_max_iter = nlp_params['ipopt_max_iter']
            ipopt_con_tol = nlp_params['ipopt_con_tol']
            nlp_opts = IpOptOptions(name='nlp-server',
                                    tol=ipopt_tol,
                                    max_iter=ipopt_max_iter,
                                    con_tol=ipopt_con_tol)

        # algorithm options
        cab_opts = CaballeroOptions(max_fun_evals=maxfunevals,
                                    feasible_tol=con_tol,
                                    penalty_factor=penalty,
                                    ref_tol=tol1, term_tol=tol2,
                                    first_factor=first_factor,
                                    second_factor=sec_factor,
                                    contraction_tol=tol_contract)

        report_obj = ReportObject(iteration_printed=self.iteration_printed,
                                  terminal=False, plot=False)

        opt_obj = Caballero(x=x, g=g, f=f, model_function=model_fun,
                            lb=lb_list, ub=ub_list, regression=regrpoly,
                            options=cab_opts, nlp_options=nlp_opts,
                            report_options=report_obj)

        opt_obj.optimize()

        self.asp_obj.close_connection()

        # create the results table report
        opt_vals = np.append(opt_obj.xopt,
                             np.append(opt_obj.gopt, opt_obj.fopt)).tolist()
        report = pd.Series(opt_vals, index=inp_aliases + con_aliases +
                           obj_alias).to_dict()

        self.results_ready.emit(report)

        self.optimization_finished.emit()

    def open_connection(self):
        # warn others that a simulation engine connection is about to be opened
        self.opening_connection.emit()

        pythoncom.CoInitialize()
        asp_obj = AspenConnection(self.app_data.simulation_file)
        self.asp_obj = asp_obj
        self._aspen_connection = asp_obj.get_connection_object()

        # emit the signal to warn others that the connection is done
        self.connection_opened.emit()

    def model_function(self, x):
        inp_data = self.app_data.input_table_data
        out_data = self.app_data.output_table_data
        expr_data = self.app_data.expression_table_data
        input_vars = inp_data.loc[
            inp_data['Type'] == self.app_data._INPUT_ALIAS_TYPES['mv'],
            ['Alias', 'Path']
        ].to_dict(orient='records')
        output_vars = out_data.loc[:,
                                   ['Alias', 'Path']].to_dict(orient='records')

        # update input values
        [var.update({'value': x[idx]}) for idx, var in enumerate(input_vars)]

        # query the simulation engine, store the results
        results = run_case(input_vars, output_vars, self._aspen_connection)

        # update the results including input variables values
        results.update({var['Alias']: var['value'] for var in input_vars})

        # evaluate constraint and objective functions
        expr_values = {}
        parser = self.parser
        for _, expr in expr_data.iterrows():
            expr_to_parse = parser.parse(expr['Expression'])
            var_list = expr_to_parse.variables()
            expr_values[expr['Alias']] = expr_to_parse.evaluate(results)

        # separate constraints values
        con_aliases = expr_data.loc[
            expr_data['Type'] == self.app_data._EXPR_ALIAS_TYPES['cst'],
            'Alias'].tolist()

        g = [expr_values[cn_alias] for cn_alias in con_aliases]

        # objective function
        obj_alias = expr_data.loc[
            expr_data['Type'] == self.app_data._EXPR_ALIAS_TYPES['obj'],
            'Alias'].tolist()

        f = [expr_values[alias] for alias in obj_alias]

        res = {
            'status': results['success'] == 'ok',
            'f': np.array(f).item(),
            'g': g,
            'extras': []
        }

        return res
