import numpy as np
import pandas as pd
from pydace import dacefit, predictor
from PyQt5.QtWidgets import QApplication, QWidget, QTableView, QHeaderView
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt5.QtGui import QFont

from gui.models.data_storage import DataStorage
from gui.views.py_files.hessianextractiontab import Ui_Form


class GTableModel(QAbstractTableModel):
    def __init__(self, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)

        self.G = pd.DataFrame()

    def update_g(self, G: pd.DataFrame):
        self.layoutAboutToBeChanged.emit()
        self.G = G
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return self.G.shape[0] if not self.G.empty else 0

    def columnCount(self, parent=None):
        return self.G.shape[1] if not self.G.empty else 0

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):

        if self.G.empty:
            return None

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.G.columns[section]
            else:
                return self.G.index[section]

        elif role == Qt.FontRole:
            df_font = QFont()
            df_font.setBold(True)
            return df_font

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        else:
            return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or self.G.empty:
            return None

        row = index.row()
        col = index.column()

        value = self.G.iat[row, col]

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
        gy_model = GTableModel(gy_table)
        gy_table.setModel(gy_model)

        gy_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        gyd_table = self.ui.gydTableView
        gyd_model = GTableModel(gyd_table)
        gyd_table.setModel(gyd_model)

        gyd_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

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

        G = self.get_gradients(X_labels, sampled_data)

        # split G in Gy and Gyd
        gyd_labels = [var['Alias'] for var in
                      self.application_database.input_table_data
                      if var['Type'] == 'Disturbance (d)']

        Gyd = G[gyd_labels]
        Gy = G[[label for label in X_labels if label not in gyd_labels]]

        self.ui.gyTableView.model().update_g(Gy)
        self.ui.gydTableView.model().update_g(Gyd)

    def get_gradients(self, X_labels: list, sampled_data: pd.DataFrame):
        # get output data labels
        Y_labels = [var['Alias'] for var in
                    self.application_database.reduced_metamodel_selected_data
                    if var['Type'] != 'Objective function (J)']

        # extract data
        X = sampled_data.loc[:, X_labels].to_numpy()
        Y = sampled_data.loc[:, Y_labels].to_numpy()

        Y_dim = Y.shape[1] if Y.ndim > 1 else 1
        if len(Y_labels) == 1:
            # single variable, convert to column vector
            Y = Y.reshape(-1, 1)

        # regression model
        regr = 'poly0'

        # correlation model
        corr = 'corrgauss'

        # theta and bounds values
        theta_data = []

        for row in self.application_database.reduced_metamodel_theta_data:
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
        x_nom = np.array([[0., 273., 147., 13.5632]])

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
