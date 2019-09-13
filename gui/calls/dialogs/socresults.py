from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt

from gui.views.py_files.socresults import Ui_Dialog
from gui.models.data_storage import DataStorage

from pysoc.soc import helm
from pysoc.bnb import pb3wc
import pandas as pd


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

        # NOTE: testar helm com matrizes da coluna
        res = pb3wc(gy=Gy.to_numpy(), gyd=Gyd.to_numpy(), wd=md.to_numpy().flatten(),
                    wn=me.to_numpy().flatten(), juu=Juu.to_numpy(), jud=Jud.to_numpy(), n=3, nc=5)
        for i in res[1]:
            st = ""
            for j in i:
                st += Gy.index[j-1] + " "

            print(st)
        res = helm(Gy=Gy.to_numpy(), Gyd=Gyd.to_numpy(), Juu=Juu.to_numpy(),
                   Jud=Jud.to_numpy(), md=md.to_numpy().flatten(),
                   me=me.to_numpy().flatten(), ss_size=1, nc_user=3)
        s = 1

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
