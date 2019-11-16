from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox

from gui.models.data_storage import DataStorage
from gui.views.py_files.caballerotab import Ui_Form

from gui.models.sampling import CaballeroWorker, ReportObject
from surropt.core.options.nlp import DockerNLPOptions

from win32com.client import Dispatch


class OptimizationTab(QWidget):
    def __init__(self, application_database: DataStorage, parent_tab=None):
        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Form()
        parent_tab = parent_tab if parent_tab is not None else self
        self.ui.setupUi(parent_tab)

        # ------------------------ Internal Variables -------------------------
        self.application_database = application_database

        # ----------------------- Widget Initialization -----------------------
        # --------------------------- Signals/Slots ---------------------------
        self.ui.startOptPushButton.clicked.connect(self.on_start_pressed)
        self.ui.ipoptTestConnectionPushButton.clicked.connect(
            self.on_ipopt_test_connection_pressed)
        # ---------------------------------------------------------------------

    def on_start_pressed(self):
        # get caballero parameters from ui
        first_factor = float(self.ui.firstFactorLineEdit.text())
        sec_factor = float(self.ui.secondFactorLineEdit.text())
        tol_contract = float(self.ui.tolContractLineEdit.text())
        con_tol = float(self.ui.conTolLineEdit.text())
        penalty = float(self.ui.penaltyFactorLineEdit.text())
        tol1 = float(self.ui.tol1LineEdit.text())
        tol2 = float(self.ui.tol2LineEdit.text())
        maxfunevals = int(self.ui.maxFunEvalsLineEdit.text())
        regrpoly = self.ui.regrpolyComboBox.currentText()

        params = {
            'first_factor': first_factor,
            'sec_factor': sec_factor,
            'tol_contract': tol_contract,
            'con_tol': con_tol,
            'penalty': penalty,
            'tol1': tol1,
            'tol2': tol2,
            'maxfunevals': maxfunevals,
            'regrpoly': regrpoly,
            'server_url': self.ui.ipoptAddressLineEdit.text()
        }

        # TODO: move worker to thread
        # REMINDER: install ptvsd via pip to debug threads
        # https://github.com/microsoft/ptvsd/issues/1189#issuecomment-468406399
        ro = ReportObject(terminal=False)
        ro.iteration_printed.connect(self.on_iteration_printed)

        cw = CaballeroWorker(app_data=self.application_database, params=params,
                             report=ro)

        cw.start_optimization()

        a = 1

    def on_ipopt_test_connection_pressed(self):
        # tests the connection with the server specified in the UI
        srv_url = self.ui.ipoptAddressLineEdit.text()
        try:
            nlp_opts = DockerNLPOptions(name='test wsl', server_url=srv_url)
        except ValueError as con_err:
            # connection failed, inform the user
            fail_box = QMessageBox(QMessageBox.Critical, 'Connection failed!',
                                   str(con_err), buttons=QMessageBox.Ok,
                                   parent=None)
            fail_box.exec_()
        else:
            # connection succeed, let the user know it
            suc_box = QMessageBox(QMessageBox.Information, 'Connection OK!',
                                  'Connection to the ipopt was successful!',
                                  buttons=QMessageBox.Ok, parent=None)
            suc_box.exec_()

    def on_iteration_printed(self, iter_msg: str):
        self.ui.controlPanelTextBrowser.append(iter_msg)


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook
    from tests_.mock_data import DOE_TAB_MOCK_DS

    app = QApplication(sys.argv)

    ds = DOE_TAB_MOCK_DS
    w = OptimizationTab(application_database=ds,
                        parent_tab=None)
    w.show()

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
