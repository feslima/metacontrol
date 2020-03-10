import pandas as pd
from PyQt5.QtCore import (QAbstractTableModel, QModelIndex, Qt, QThread,
                          pyqtSignal)
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QHeaderView, QMessageBox, QWidget
from surropt.core.options.nlp import DockerNLPOptions
from win32com.client import Dispatch

from gui.models.data_storage import DataStorage
from gui.models.sampling import CaballeroWorker, ReportObject
from gui.views.py_files.caballerotab import Ui_Form


class ResultsTableModel(QAbstractTableModel):
    def __init__(self, results_frame: pd.DataFrame, parent=None):
        super().__init__(parent)
        self.df = results_frame

    def load_results(self, results_frame: pd.DataFrame):
        self.layoutAboutToBeChanged.emit()
        self.df = results_frame
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return self.df.shape[0]

    def columnCount(self, parent=None):
        return self.df.shape[1]

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if self.df.empty:
            return None

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.df.columns[section]
            else:
                return self.df.index[section]

        elif role == Qt.FontRole:
            df_font = QFont()
            df_font.setBold(True)
            return df_font

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        else:
            return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or self.df.empty:
            return None

        row = index.row()
        col = index.column()

        value = self.df.iat[row, col]

        if role == Qt.DisplayRole:
            return str(value)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        else:
            return None


class OptimizationTab(QWidget):
    iteration_printed = pyqtSignal(str)
    opening_connection = pyqtSignal()
    connection_opened = pyqtSignal()
    optimization_failed = pyqtSignal(str)

    def __init__(self, application_database: DataStorage, parent_tab=None):
        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Form()
        parent_tab = parent_tab if parent_tab is not None else self
        self.ui.setupUi(parent_tab)

        # ------------------------ Internal Variables -------------------------
        self.application_database = application_database

        # ----------------------- Widget Initialization -----------------------
        self.load_opt_params()

        res_tab = self.ui.resultsTableView
        res_model = ResultsTableModel(results_frame=pd.DataFrame({}))
        res_tab.setModel(res_model)

        res_tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # disable abort button (for now, while surropt api does not implement)
        self.ui.abortOptPushButton.setEnabled(False)

        # --------------------------- Signals/Slots ---------------------------
        self.ui.startOptPushButton.clicked.connect(self.on_start_pressed)
        self.ui.ipoptTestConnectionPushButton.clicked.connect(
            self.on_ipopt_test_connection_pressed)

        # whenever any of the opt parameters changes update the underlying obj
        factor1_le, factor2_le, tol_contract_le, con_tol_le, penalty_le, \
            tol1_le, tol2_le, maxfunevals_le, \
            regrpoly_cb = self._get_lineedit_handles()

        factor1_le.textChanged.connect(self.set_opt_params)
        factor2_le.textChanged.connect(self.set_opt_params)
        tol_contract_le.textChanged.connect(self.set_opt_params)
        con_tol_le.textChanged.connect(self.set_opt_params)
        penalty_le.textChanged.connect(self.set_opt_params)
        tol1_le.textChanged.connect(self.set_opt_params)
        tol2_le.textChanged.connect(self.set_opt_params)
        maxfunevals_le.textChanged.connect(self.set_opt_params)
        regrpoly_cb.currentIndexChanged.connect(self.set_opt_params)
        self.ui.ipoptLocalDualFeasLineEdit.textChanged.connect(
            self.set_opt_params)
        self.ui.ipoptLocalMaxIterLineEdit.textChanged.connect(
            self.set_opt_params)
        self.ui.ipoptLocalConTolLineEdit.textChanged.connect(
            self.set_opt_params)
        self.ui.ipoptServerDualFeasLineEdit.textChanged.connect(
            self.set_opt_params)
        self.ui.ipoptServerMaxIterLineEdit.textChanged.connect(
            self.set_opt_params)
        self.ui.ipoptServerConTolLineEdit.textChanged.connect(
            self.set_opt_params)

        # control panel related stuff
        self.opening_connection.connect(self.on_opening_sim_connection)
        self.connection_opened.connect(self.on_sim_connection_opened)
        self.iteration_printed.connect(self.on_iteration_printed)
        self.optimization_failed.connect(self.on_optimization_failed)
        # ---------------------------------------------------------------------

    def _get_lineedit_handles(self):
        factor1_le = self.ui.firstFactorLineEdit
        factor2_le = self.ui.secondFactorLineEdit
        tol_contract_le = self.ui.secondFactorLineEdit
        con_tol_le = self.ui.conTolLineEdit
        penalty_le = self.ui.penaltyFactorLineEdit
        tol1_le = self.ui.tol1LineEdit
        tol2_le = self.ui.tol2LineEdit
        maxfunevals_le = self.ui.maxFunEvalsLineEdit
        regrpoly_cb = self.ui.regrpolyComboBox

        return factor1_le, factor2_le, tol_contract_le, con_tol_le, \
            penalty_le, tol1_le, tol2_le, maxfunevals_le, regrpoly_cb

    def load_opt_params(self):
        factor1_le, factor2_le, tol_contract_le, con_tol_le, penalty_le, \
            tol1_le, tol2_le, maxfunevals_le, \
            regrpoly_cb = self._get_lineedit_handles()

        opt_params = self.application_database.optimization_parameters
        solver_params = opt_params['nlp_params']

        factor1_le.setText(str(opt_params['first_factor']))
        factor2_le.setText(str(opt_params['second_factor']))
        tol_contract_le.setText(str(opt_params['tol_contract']))
        con_tol_le.setText(str(opt_params['con_tol']))
        penalty_le.setText(str(opt_params['penalty']))
        tol1_le.setText(str(opt_params['tol1']))
        tol2_le.setText(str(opt_params['tol2']))
        maxfunevals_le.setText(str(opt_params['maxfunevals']))

        if opt_params['regrpoly'] == 'poly0':
            regrpoly_cb.setCurrentIndex(0)
        elif opt_params['regrpoly'] == 'poly1':
            regrpoly_cb.setCurrentIndex(1)
        elif opt_params['regrpoly'] == 'poly2':
            regrpoly_cb.setCurrentIndex(2)
        else:
            raise ValueError("Invalid polynomial regression option.")

        if solver_params['solver_type'] == 'ipopt_local':
            ipopt_tol_le = self.ui.ipoptLocalDualFeasLineEdit
            ipopt_max_iter_le = self.ui.ipoptLocalMaxIterLineEdit
            ipopt_con_tol_le = self.ui.ipoptLocalConTolLineEdit

            tol = solver_params['tol']
            max_iter = solver_params['max_iter']
            con_tol = solver_params['con_tol']

        elif solver_params['solver_type'] == 'ipopt_server':
            server_url_le = self.ui.ipoptServerAddressLineEdit

            server_url_le.setText(solver_params['server_url'])
            ipopt_tol_le = self.ui.ipoptServerDualFeasLineEdit
            ipopt_max_iter_le = self.ui.ipoptServerMaxIterLineEdit
            ipopt_con_tol_le = self.ui.ipoptServerConTolLineEdit

            tol = solver_params['tol']
            max_iter = solver_params['max_iter']
            con_tol = solver_params['con_tol']

        else:
            raise ValueError("Invalid solver type.")

        ipopt_tol_le.setText(str(tol))
        ipopt_max_iter_le.setText(str(max_iter))
        ipopt_con_tol_le.setText(str(con_tol))

    def set_opt_params(self):
        factor1_le, factor2_le, tol_contract_le, con_tol_le, penalty_le, \
            tol1_le, tol2_le, maxfunevals_le, \
            regrpoly_cb = self._get_lineedit_handles()

        le_name = self.sender().objectName()

        opt_params = self.application_database.optimization_parameters
        solver_params = opt_params['nlp_params']

        if le_name == factor1_le.objectName():
            opt_params['first_factor'] = float(factor1_le.text())

        elif le_name == factor2_le.objectName():
            opt_params['second_factor'] = float(factor2_le.text())

        elif le_name == tol_contract_le.objectName():
            opt_params['tol_contract'] = float(tol_contract_le.text())

        elif le_name == con_tol_le.objectName():
            opt_params['con_tol'] = float(con_tol_le.text())

        elif le_name == penalty_le.objectName():
            opt_params['penalty'] = float(penalty_le.text())

        elif le_name == tol1_le.objectName():
            opt_params['tol1'] = float(tol1_le.text())

        elif le_name == tol2_le.objectName():
            opt_params['tol2'] = float(tol2_le.text())

        elif le_name == maxfunevals_le.objectName():
            opt_params['maxfunevals'] = float(maxfunevals_le.text())

        elif le_name == regrpoly_cb.objectName():
            if regrpoly_cb.currentIndex() == 0:
                opt_params['regrpoly'] = 'poly0'
            elif regrpoly_cb.currentIndex() == 1:
                opt_params['regrpoly'] = 'poly1'
            else:
                opt_params['regrpoly'] = 'poly2'

        tabw = self.ui.tabWidget

        if tabw.currentWidget().objectName() == 'ipOptLocalTab':
            ipopt_tol_le = self.ui.ipoptLocalDualFeasLineEdit
            ipopt_max_iter_le = self.ui.ipoptLocalMaxIterLineEdit
            ipopt_con_tol_le = self.ui.ipoptLocalConTolLineEdit

            solver_params['solver_type'] = 'ipopt_local'

        elif tabw.currentWidget().objectName() == 'ipOptServerTab':
            server_url_le = self.ui.ipoptServerAddressLineEdit
            ipopt_tol_le = self.ui.ipoptServerDualFeasLineEdit
            ipopt_max_iter_le = self.ui.ipoptServerMaxIterLineEdit
            ipopt_con_tol_le = self.ui.ipoptServerConTolLineEdit

            solver_params['server_url'] = server_url_le.text()
            solver_params['solver_type'] = 'ipopt_server'

        else:
            raise IndexError('Tab object not found.')

        solver_params['tol'] = float(ipopt_tol_le.text())
        solver_params['max_iter'] = int(ipopt_max_iter_le.text())
        solver_params['con_tol'] = float(ipopt_con_tol_le.text())

        opt_params['nlp_params'] = solver_params

        self.application_database.optimization_parameters = opt_params

    def on_start_pressed(self):
        # get caballero parameters from storage
        opt_params = self.application_database.optimization_parameters
        solver_params = opt_params['nlp_params']

        first_factor = opt_params['first_factor']
        sec_factor = opt_params['second_factor']
        tol_contract = opt_params['tol_contract']
        con_tol = opt_params['con_tol']
        penalty = opt_params['penalty']
        tol1 = opt_params['tol1']
        tol2 = opt_params['tol2']
        maxfunevals = opt_params['maxfunevals']
        regrpoly = opt_params['regrpoly']

        nlp_dict = solver_params

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
            'nlp_dict': nlp_dict
        }

        # disable ui elements
        self.ui.startOptPushButton.setEnabled(False)
        self.ui.regrpolyComboBox.setEnabled(False)
        self.ui.ipoptTestConnectionPushButton.setEnabled(False)

        # instantiate the optimization thread and worker
        self.opt_thread = QThread()
        self.opt_worker = CaballeroWorker(
            app_data=self.application_database,
            params=params,
            iteration_printed=self.iteration_printed,
            opening_connection=self.opening_connection,
            connection_opened=self.connection_opened,
            optimization_failed=self.optimization_failed
        )

        # worker signals connection
        self.opt_worker.results_ready.connect(self.on_opt_results_ready)

        # move the worker to another thread
        self.opt_worker.moveToThread(self.opt_thread)

        self.opt_worker.optimization_finished.connect(self.opt_thread.quit)
        self.opt_worker.optimization_finished.connect(
            self.on_optimization_finished)
        self.opt_thread.started.connect(self.opt_worker.start_optimization)

        # start the thread
        self.opt_thread.start()

    def on_opt_results_ready(self, report: dict):
        report_s = pd.Series(report)  # make a copy as series
        report = pd.DataFrame(report, index=['Values']).copy(deep=True)

        model = self.ui.resultsTableView.model()

        model.load_results(report)

        self.application_database.optimization_results = report_s

    def on_optimization_failed(self, error_msg: str):
        # append message to the control panel
        err_msg = "\n\n-------OPTIMIZATION PROCEDURE FAILED!-------\n\n" + \
            "This is the error returned by the procedure:\n\n" + error_msg + \
            "\n\n---------------USEFUL INFO----------------\n\n" + \
            "Depending on the error type, if you change the optimization " + \
            "parameters you might obtain a better outcome."

        self.ui.controlPanelTextBrowser.append(err_msg)

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
