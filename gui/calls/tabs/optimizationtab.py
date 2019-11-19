from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget
from surropt.core.options.nlp import DockerNLPOptions
from win32com.client import Dispatch

from gui.models.data_storage import DataStorage
from gui.models.sampling import CaballeroWorker, ReportObject
from gui.views.py_files.caballerotab import Ui_Form


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
        # disable abort button (for now, while surropt api does not implement)
        self.ui.abortOptPushButton.setEnabled(False)

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

        # disable ui elements
        self.ui.startOptPushButton.setEnabled(False)
        self.ui.regrpolyComboBox.setEnabled(False)
        self.ui.ipoptTestConnectionPushButton.setEnabled(False)

        # instantiate the report object (communication with UI)
        ro = ReportObject(terminal=False)
        ro.iteration_printed.connect(self.on_iteration_printed)

        # instantiate the optimization thread and worker
        self.opt_thread = QThread()
        self.opt_worker = CaballeroWorker(app_data=self.application_database,
                                          params=params, report=ro)

        # worker signals connection
        self.opt_worker.opening_connection.connect(
            self.on_opening_sim_connection)
        self.opt_worker.connection_opened.connect(
            self.on_sim_connection_opened)

        # move the worker to another thread
        self.opt_worker.moveToThread(self.opt_thread)

        self.opt_worker.optimization_finished.connect(self.opt_thread.quit)
        self.opt_worker.optimization_finished.connect(
            self.on_optimization_finished)
        self.opt_thread.started.connect(self.opt_worker.start_optimization)

        # start the thread
        self.opt_thread.start()

    def on_optimization_finished(self):
        # enable ui elements
        self.ui.startOptPushButton.setEnabled(True)
        self.ui.regrpolyComboBox.setEnabled(True)
        self.ui.ipoptTestConnectionPushButton.setEnabled(True)

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

    def on_opening_sim_connection(self):
        self.on_iteration_printed("Connecting to the simulation engine...\n")

    def on_sim_connection_opened(self):
        self.on_iteration_printed("Simulation engine connection successful!\n")


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
