import numpy as np
import pandas as pd
import pythoncom
import win32com.client
from pydace.aux_functions import lhsdesign
from PyQt5.QtCore import QThread, pyqtSignal

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
        self._aspen_connection = AspenConnection(
            app_data.simulation_file)

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
        # initialize
        pythoncom.CoInitialize()

        # get instance from id
        aspen_con = win32com.client.Dispatch(
            pythoncom.CoGetInterfaceAndReleaseStream(
                self._aspen_id, pythoncom.IID_IDispatch)
        )

        input_vars = [{'var': row['Alias'], 'Path': row['Path']}
                      for row in self._app_data.input_table_data
                      if row['Type'] == 'Manipulated (MV)']

        output_vars = [{'var': row['Alias'], 'Path': row['Path']}
                       for row in self._app_data.output_table_data]

        for row in range(self._input_des_data.shape[0]):
            [var.update({'value': self._input_des_data.loc[row, var['var']]})
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
            res_dict[out_var['var']] = aspen_obj.Tree.FindNode(
                out_var['Path']).Value
    else:
        res_dict['success'] = 'error'
        for out_var in output_data:
            res_dict[out_var['var']] = np.spacing(1)

    return res_dict
