import numpy as np
import pandas as pd
from pydace import dacefit, predictor
from PyQt5.QtWidgets import QApplication, QWidget, QTableView, QHeaderView
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt5.QtGui import QFont

from gui.models.data_storage import DataStorage
from gui.views.py_files.hessianextractiontab import Ui_Form
from gui.models.hessian_eval import hesscorrgauss


class DiffTableModel(QAbstractTableModel):
    def __init__(self, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)

        self.diff = pd.DataFrame()

    def update_diff(self, diff: pd.DataFrame):
        self.layoutAboutToBeChanged.emit()
        self.diff = diff
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return self.diff.shape[0] if not self.diff.empty else 0

    def columnCount(self, parent=None):
        return self.diff.shape[1] if not self.diff.empty else 0

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):

        if self.diff.empty:
            return None

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.diff.columns[section]
            else:
                return self.diff.index[section]

        elif role == Qt.FontRole:
            df_font = QFont()
            df_font.setBold(True)
            return df_font

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        else:
            return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or self.diff.empty:
            return None

        row = index.row()
        col = index.column()

        value = self.diff.iat[row, col]

        if role == Qt.DisplayRole:
            return str(value)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        else:
            return None


class HessianExtractionTab(QWidget):
    def __init__(self, application_database: DataStorage, parent_tab=None):
        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Form()
        parent_tab = parent_tab if parent_tab is not None else self
        self.ui.setupUi(parent_tab)

        # ------------------------ Internal Variables -------------------------
        self.application_database = application_database

        # ----------------------- Widget Initialization -----------------------
        gy_table = self.ui.gyTableView
        gy_model = DiffTableModel(gy_table)
        gy_table.setModel(gy_model)

        gy_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        gyd_table = self.ui.gydTableView
        gyd_model = DiffTableModel(gyd_table)
        gyd_table.setModel(gyd_model)

        gyd_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        juu_table = self.ui.juuTableView
        juu_model = DiffTableModel(juu_table)
        juu_table.setModel(juu_model)

        juu_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        jud_table = self.ui.judTableView
        jud_model = DiffTableModel(jud_table)
        jud_table.setModel(jud_model)

        jud_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # --------------------------- Signals/Slots ---------------------------
        self.ui.genGradHessPushButton.clicked.connect(
            self.on_generate_grad_hess_pressed
        )
        # ---------------------------------------------------------------------

    def on_generate_grad_hess_pressed(self):
        # get reduced space inputs from reduced theta data
        X_labels = [row['Alias']
                    for row in
                    self.application_database.reduced_metamodel_theta_data]

        # sampled data
        sampled_data = pd.DataFrame(
            self.application_database.reduced_doe_sampled_data)

        G = self.get_differentials(X_labels, sampled_data, difftype='gradient')

        # split G in Gy and Gyd
        d_labels = [var['Alias'] for var in
                    self.application_database.input_table_data
                    if var['Type'] == 'Disturbance (d)']

        u_labels = [label for label in X_labels if label not in d_labels]

        Gyd = G[d_labels]
        Gy = G[u_labels]

        self.application_database.differential_gy = Gy.to_dict(orient='list')
        self.application_database.differential_gyd = Gyd.to_dict(orient='list')

        # update the tables models
        self.ui.gyTableView.model().update_diff(Gy)
        self.ui.gydTableView.model().update_diff(Gyd)

        # hessian
        J = self.get_differentials(X_labels, sampled_data, difftype='hessian')

        # split between juu and jud
        Jud = J.loc[u_labels, d_labels]
        Juu = J.loc[u_labels, u_labels]

        self.application_database.differential_juu = Juu.to_dict(orient='list')
        self.application_database.differential_jud = Jud.to_dict(orient='list')

        # update table models
        self.ui.judTableView.model().update_diff(Jud)
        self.ui.juuTableView.model().update_diff(Juu)

    def get_differentials(self, X_labels: list, sampled_data: pd.DataFrame,
                          difftype: str):

        app_data = self.application_database

        # get output data labels
        if difftype == 'gradient':
            Y_labels = [var['Alias'] for var in
                        app_data.reduced_metamodel_selected_data
                        if var['Type'] != 'Objective function (J)']
        else:
            Y_labels = [var['Alias'] for var in
                        app_data.reduced_metamodel_selected_data
                        if var['Type'] == 'Objective function (J)']

        # extract data
        X = sampled_data.loc[:, X_labels].to_numpy()
        Y = sampled_data.loc[:, Y_labels].to_numpy()

        Y_dim = Y.shape[1] if Y.ndim > 1 else 1
        if len(Y_labels) == 1:
            # single variable, convert to column vector
            Y = Y.reshape(-1, 1)

        # regression model
        regr = self.application_database.differential_regression_model

        # correlation model
        corr = self.application_database.differential_correlation_model

        # theta and bounds values
        theta_data = []

        for row in app_data.reduced_metamodel_theta_data:
            for label in X_labels:
                if row['Alias'] == label:
                    # reorder theta values in X label order
                    theta_data.append(row)

        theta0, lob, upb = map(list,
                               zip(*[(row['theta0'], row['lb'], row['ub'])
                                     for row in theta_data]))

        theta0 = np.asarray(theta0)
        lob = np.asarray(lob)
        upb = np.asarray(upb)

        # get nominal values
        # FIXME: implement better way to ensure order of MV's are correct
        act_info = app_data.active_constraint_info
        values = [var['nom']
                  for var in app_data.reduced_doe_d_bounds
                  if var['name'] in X_labels] + \
            [act_info[var]['Value']
             for var in act_info
             if var in X_labels]
        x_nom = np.array([values])

        if difftype == 'gradient':
            # G dataFrame (Transposed because skogestad nomeclature)
            G = pd.DataFrame(columns=X_labels, index=Y_labels)

            # train the models
            for j in range(Y_dim):
                ph, _ = dacefit(S=X, Y=Y[:, j], regr=regr, corr=corr,
                                theta0=theta0, lob=lob, upb=upb)

                _, gy_ph, *_ = predictor(x=x_nom, dmodel=ph,
                                         compute_jacobian=True)

                for i in range(x_nom.size):
                    # store G values in the dataframe
                    G.at[Y_labels[j], X_labels[i]] = gy_ph[i, 0]

            return G
        else:
            # J dataFrame
            J = pd.DataFrame(columns=X_labels, index=X_labels)
            dmodel = dacefit(S=X, Y=Y, regr=regr, corr=corr,
                             theta0=theta0, lob=lob, upb=upb)[0]

            j_np = hesscorrgauss(x_nom, dmodel)
            for i in range(len(X_labels)):
                for j in range(len(X_labels)):
                    J.at[X_labels[i], X_labels[j]] = j_np[i, j]

            return J


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook
    from tests_.mock_data import REDSPACE_TAB_MOCK_DS

    app = QApplication(sys.argv)
    ds = REDSPACE_TAB_MOCK_DS
    w = HessianExtractionTab(application_database=ds)
    w.show()

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
