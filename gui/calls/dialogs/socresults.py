from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt

from gui.views.py_files.socresults import Ui_Dialog
from gui.models.data_storage import DataStorage

from pysoc.soc import helm
from pysoc.bnb import pb3wc
import pandas as pd
import numpy as np


class SocResultsDialog(QDialog):
    def __init__(self, application_data: DataStorage):
        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Window)
        self.setWindowState(Qt.WindowMaximized)
        # ------------------------ Internal Variables -------------------------
        self.app_data = application_data

        Gy = pd.DataFrame(self.app_data.differential_gy)
        Gyd = pd.DataFrame(self.app_data.differential_gyd)
        Juu = pd.DataFrame(self.app_data.differential_juu)
        Jud = pd.DataFrame(self.app_data.differential_jud)
        md = pd.DataFrame(self.app_data.soc_disturbance_magnitude)
        me = pd.DataFrame(self.app_data.soc_measure_error_magnitude)
        ss_list = self.app_data.soc_subset_size_list

        # keys are the subset sizes
        soc_results = {}

        for ss in ss_list:
            n = int(ss)
            nc = int(ss_list[ss]['Subset number'])

            res = helm(Gy=Gy.to_numpy(), Gyd=Gyd.to_numpy(),
                       Juu=Juu.to_numpy(), Jud=Jud.to_numpy(),
                       md=md.to_numpy().flatten(),
                       me=me.to_numpy().flatten(),
                       ss_size=n, nc_user=nc)

            # prepare the frames to be displayed
            worst_loss_list, average_loss_list, sset_bnb, cond_list, \
                H_list, Gy_list, Gyd_list, F_list = res

            # losses dataframe
            loss_df = pd.DataFrame(np.nan, index=range(nc),
                                   columns=['Structure', 'Worst-case loss',
                                            'Average loss'], dtype=object)

            soc_results[ss] = {'loss': loss_df}

            for i in range(nc):
                # build the structure string
                st = ""
                ss_row = sset_bnb[i, :]
                for j in ss_row:
                    if j != ss_row[-1]:
                        st += Gy.index[j - 1] + " | "
                    else:
                        st += Gy.index[j - 1]

                # assign structure
                loss_df.at[i, 'Structure'] = st

                loss_df.at[i, 'Worst-case loss'] = worst_loss_list[i]
                loss_df.at[i, 'Average loss'] = average_loss_list[i]

            # H dataframe
            h_df = pd.DataFrame(None, index=loss_df.loc[:, 'Structure'].values,
                                columns=Gy.index)
            soc_results[ss]['h'] = h_df
            soc_results[ss]['f'] = {}
            for i in range(nc):
                ss_row = sset_bnb[i, :]

                # sensitivity matrices
                F = pd.DataFrame(F_list[i], index=Gy.index[ss_row - 1],
                                 columns=Gyd.columns)
                soc_results[ss]['f']["set_" + str(i)] = F
                # populate H matrix
                for col, j in enumerate(ss_row):
                    h_df.at[loss_df.at[i, 'Structure'],
                            Gy.index[j - 1]] = H_list[i][0, col]

            s = 1

        raise NotImplementedError("NOT FINISHED!")

        # ----------------------- Widget Initialization -----------------------
        # --------------------------- Signals/Slots ---------------------------
        # ---------------------------------------------------------------------


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook
    from tests_.mock_data import SOC_TAB_MOC_DS

    app = QApplication(sys.argv)
    ds = SOC_TAB_MOC_DS
    w = SocResultsDialog(application_data=ds)
    w.show()

    sys.excepthook = my_exception_hook

    sys.exit(app.exec_())
