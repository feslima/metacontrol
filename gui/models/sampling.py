import numpy as np
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

    def __init__(self, input_design_data: np.ndarray, app_data: DataStorage,
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

        max_rows = self._input_des_data.shape[0]
        for row in range(max_rows):
            mv_values = self._input_des_data[row, :].flatten().tolist()
            self.case_sampled.emit(row + 1,
                                   run_case(self._app_data,
                                            mv_values,
                                            aspen_con)
                                   )

            if self.isInterruptionRequested():  # to allow task abortion
                return


def run_case(app_data: DataStorage, mv_values: list, aspen_obj):
    """
Samples a single case of DOE.

    Parameters
    ----------
    app_data : DataStorage
        Application data storage object.
    mv_values : list
        List containing all the design values to sample.
    aspen_obj : COM object
        Object connection handle.

    Returns
    -------
    dict
        Dictionary with output alias as keys and values as data sampled.
    """
    # get mv from doe data
    mv_alias_list = [entry['name'] for entry in app_data.doe_mv_bounds]

    # input/ output data
    inp_data = app_data.input_table_data
    out_data = app_data.output_table_data

    # get the paths to feed to the aspen obj
    for i in range(len(mv_alias_list)):
        path_item = [inp['Path']
                     for inp in inp_data if inp['Alias'] == mv_alias_list[i]]
        aspen_obj.Tree.FindNode(path_item[0]).Value = mv_values[i]

    # run the engine
    aspen_obj.Engine.Run2()

    # get the output
    res_dict = {}
    UOSTAT2_val = aspen_obj.Tree.FindNode(
        r"\Data\Results Summary\Run-Status\Output\UOSSTAT2").Value
    if UOSTAT2_val == 8:
        res_dict['success'] = 'ok'
        for out_var in out_data:
            res_dict[out_var['Alias']] = aspen_obj.Tree.FindNode(
                out_var['Path']).Value
    else:
        res_dict['success'] = 'error'
        for out_var in out_data:
            res_dict[out_var['Alias']] = 0.0

    return res_dict
