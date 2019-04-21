from pydace.aux_functions import lhsdesign
import numpy as np

from PyQt5.QtCore import QThread, pyqtSignal, QEventLoop, QTimer
from PyQt5.QtWidgets import QMessageBox

from gui.models.data_storage import DataStorage

# TODO: (21/04/2019) Implement Thread that samples the data while keeping the GUI responsive

def lhs(n_samples: int, lb: list, ub: list, n_iter: int, inc_vertices: bool):

    lb = np.asarray(lb)
    ub = np.asarray(ub)

    return lhsdesign(n_samples, lb, ub, k=n_iter, include_vertices=inc_vertices)


class SamplerThread(QThread):
    """
    Sampling thread that opens the aspen connection to keep the sampling assistant GUI responsive while the sampling is
    performed
    """

    caseSampled = pyqtSignal(list)

    def __init__(self, input_design_data, ):
        QThread.__init__(self)

    def run(self):
        # test function
        count = 0
        while count < 10:
            self.sleep(1)
            count += 1
            self.caseSampled.emit(np.random.rand())


def runCase(app_data: DataStorage, mv_values: list, aspen_obj):
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
    mv_alias_list = [entry['name'] for entry in app_data.getDoeData()['mv']]

    # input/ output data
    inp_data = app_data.getInputTableData()
    out_data = app_data.getOutputTableData()

    # get the paths to feed to the aspen obj
    for i in range(len(mv_alias_list)):
        path_item = [inp['Path'] for inp in inp_data if inp['Alias'] == mv_alias_list[i]]
        aspen_obj.Tree.FindNode(path_item[0]).Value = mv_values[i]

    # run the engine
    aspen_obj.Engine.Run2()

    # get the output
    res_dict = {}
    if aspen_obj.Tree.FindNode(r"\Data\Results Summary\Run-Status\Output\UOSSTAT2").Value == 8:
        for out_var in out_data:
            res_dict[out_var['Alias']] = aspen_obj.Tree.FindNode(out_var['Path']).Value

    else:
        for out_var in out_data:
            res_dict[out_var['Alias']] = 0.0

    return res_dict
