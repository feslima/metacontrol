from math import ceil

import matplotlib
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg,
                                                NavigationToolbar2QT)
from matplotlib.figure import Figure
from pydace import Dace
# from pydace import dacefit, predictor
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtGui import QBrush, QFont, QPalette, QResizeEvent
from PyQt5.QtWidgets import (QApplication, QDialog, QHeaderView, QTableView,
                             QVBoxLayout, QWidget)
from sklearn.metrics import (explained_variance_score, mean_absolute_error,
                             mean_squared_error, r2_score)
from sklearn.model_selection import KFold, train_test_split

from gui.calls.base import (CheckBoxDelegate, DoubleEditorDelegate,
                            warn_the_user)
from gui.models.data_storage import DataStorage
from gui.views.py_files.metamodeltab import Ui_Form

matplotlib.use('Qt5Agg')


class ThetaTableModel(QAbstractTableModel):
    def __init__(self, application_data: DataStorage, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)
        self.app_data = application_data
        self.load_data()
        self.headers = ['Variable', 'Lower Bound', 'Upper Bound', 'Estimate']

        self.app_data.alias_data_changed.connect(self.load_data)

    def load_data(self):
        self.layoutAboutToBeChanged.emit()
        self.theta_data = self.app_data.metamodel_theta_data
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return len(self.theta_data)

    def columnCount(self, parent):
        return len(self.headers)

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):

        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self.headers[section]

            elif role == Qt.FontRole:
                df_font = QFont()
                df_font.setBold(True)
                return df_font

            else:
                return None

        else:
            return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        theta_row = self.theta_data[row]

        if role == Qt.DisplayRole:
            if col == 0:
                return str(theta_row['Alias'])
            elif col == 1:
                return str(theta_row['lb'])
            elif col == 2:
                return str(theta_row['ub'])
            elif col == 3:
                return str(theta_row['theta0'])
            else:
                return None

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.BackgroundColorRole:
            if col == 1 or col == 2:
                if theta_row['lb'] >= theta_row['ub']:
                    return QBrush(Qt.red)
                else:
                    return QBrush(self.parent().palette().brush(QPalette.Base))

            elif col == 3:
                if theta_row['theta0'] < theta_row['lb'] or \
                        theta_row['theta0'] > theta_row['ub']:
                    return QBrush(Qt.red)
                else:
                    return QBrush(self.parent().palette().brush(QPalette.Base))
            else:
                return None

        elif role == Qt.ToolTipRole:
            if col == 1 or col == 2:
                if theta_row['lb'] >= theta_row['ub']:
                    return "Lower bound can't be greater than upper bound!"
                else:
                    return ""
            elif col == 3:
                if theta_row['theta0'] < theta_row['lb'] or \
                        theta_row['theta0'] > theta_row['ub']:
                    return ("Initial estimate can't be lower than lb or "
                            "greater than ub!")
                else:
                    return ""
            else:
                return None

        else:
            return None

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):
        if role != Qt.EditRole or not index.isValid():
            return False

        row = index.row()
        col = index.column()

        theta_row = self.theta_data[row]

        if col == 1:
            theta_row['lb'] = float(value)
        elif col == 2:
            theta_row['ub'] = float(value)
        elif col == 3:
            theta_row['theta0'] = float(value)
        else:
            return False

        self.dataChanged.emit(index.sibling(row, 1), index.sibling(row, 2))
        return True

    def flags(self, index: QModelIndex):
        if index.column() != 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | ~Qt.ItemIsEditable


class VariableSelectionTableModel(QAbstractTableModel):
    def __init__(self, application_data: DataStorage, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)
        self.app_data = application_data
        self.headers = ['Select', 'Alias', 'Type']
        self.load_data()

        self.app_data.alias_data_changed.connect(self.load_data)
        self.app_data.expr_data_changed.connect(self.load_data)

    def load_data(self):
        self.layoutAboutToBeChanged.emit()

        # get candidates, constraints and objective function
        self.variables = self.app_data.metamodel_selected_data

        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return len(self.variables)

    def columnCount(self, parent=None):
        return len(self.headers)

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.headers[section]

            else:
                return None

        elif role == Qt.FontRole:
            if orientation == Qt.Horizontal:
                df_font = QFont()
                df_font.setBold(True)
                return df_font
            else:
                return None
        else:
            return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        var_data = self.variables[row]

        if role == Qt.DisplayRole:
            if col == 1:
                return str(var_data['Alias'])
            elif col == 2:
                return str(var_data['Type'])
            else:
                return None

        elif role == Qt.CheckStateRole:
            if col == 0:
                if var_data['Checked']:
                    return Qt.Checked
                else:
                    return Qt.Unchecked
            else:
                return None

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):
        if role != Qt.EditRole or not index.isValid():
            return False

        row = index.row()
        col = index.column()

        var_data = self.variables[row]

        if col == 0:
            var_data['Checked'] = True if value == 1 else False

            self.dataChanged.emit(index.sibling(row, col + 1),
                                  index.sibling(row, self.columnCount()))

            return True

        return False

    def flags(self, index: QModelIndex):
        row = index.row()
        col = index.column()

        var_data = self.variables[row]

        if col == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | \
                Qt.ItemIsEditable
        else:
            if var_data['Checked']:
                # enable row
                return Qt.ItemIsEnabled | Qt.ItemIsSelectable
            else:
                # disable row
                return ~Qt.ItemIsEnabled | Qt.ItemIsSelectable


class CrossValidationMetricsTableModel(QAbstractTableModel):

    _ABREV_DICT = {'OMSE': 'Overall Mean Squared Error',
                   'ORMSE': 'Overall Root Mean Squared Error',
                   'OMAE': 'Overal Mean Absolute Error',
                   'OR2': 'Overall R^2 linear coefficient',
                   'OEV': 'Overall Explained Variance',
                   'MSE': 'Mean Squared Error',
                   'RMSE': 'Root Mean Squared Error',
                   'MAE': 'Mean Absolute Error',
                   'R2': 'R^2 linear coefficient',
                   'EV': 'Explained Variance',
                   'Sample Mean': 'Sample mean of the variable',
                   'Sample Std': 'Sample standard deviation of the variable'}

    def __init__(self, parent: QTableView):
        QAbstractTableModel.__init__(self, parent)
        # initialize empty dataframe
        self.metric_data = pd.DataFrame()

    def load_data(self, dframe: pd.DataFrame):
        self.layoutAboutToBeChanged.emit()

        self.metric_data = dframe

        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        return self.metric_data.shape[0]

    def columnCount(self, parent=None):
        return self.metric_data.shape[1]

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                headers = list(self.metric_data.columns)
                return headers[section]

            else:
                headers = list(self.metric_data.index)
                return headers[section]

        elif role == Qt.FontRole:
            df_font = QFont()
            df_font.setBold(True)
            return df_font

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.ToolTipRole:
            if orientation == Qt.Vertical:
                index = self.metric_data.index[section]
                return self._ABREV_DICT[index]

        else:
            return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole:
            return str(self.metric_data.iloc[row, col])

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        else:
            return None


class PlotWindow(QDialog):
    def __init__(self, metamodel_data: dict, parent=None):
        super(PlotWindow, self).__init__(parent)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle("Validation results")

        self.figure = Figure()

        self.canvas = FigureCanvasQTAgg(self.figure)

        self.plt_toolbar = NavigationToolbar2QT(self.canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.plt_toolbar)
        self.setLayout(layout)

        self.metamodel_data = metamodel_data
        self.plot()

    def plot(self):
        test_data = self.metamodel_data['Y_test']
        pred_data = self.metamodel_data['Y_pred']
        fig_titles = self.metamodel_data['labels']

        self.figure.clear()

        # plot data
        n_vars = test_data.shape[1]
        is_even = True if (n_vars % 2) == 0 else False

        n_cols = 2
        nrows = ceil(n_vars / 2)

        for i in range(n_vars):
            ax = self.figure.add_subplot(nrows, n_cols, i + 1,
                                         xlabel='Test values',
                                         ylabel='Predicted values',
                                         title=fig_titles[i])

            # plot data
            ax.plot(test_data[:, i], pred_data[:, i], 'b.')
            ax.grid(True)

            # 45 degree line
            x = np.linspace(*ax.get_xlim())
            ax.plot(x, x, 'k')

            # refresh canvas
            self.canvas.draw()

        self.figure.tight_layout()

    def resizeEvent(self, e: QResizeEvent):
        super().resizeEvent(e)
        self.figure.tight_layout()


class MetamodelTab(QWidget):
    def __init__(self, application_database: DataStorage, parent_tab=None):
        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Form()
        parent_tab = parent_tab if parent_tab is not None else self
        self.ui.setupUi(parent_tab)

        # ------------------------ Internal Variables -------------------------
        self.application_database = application_database

        # ----------------------- Widget Initialization -----------------------
        theta_table = self.ui.thetaTableView
        theta_model = ThetaTableModel(self.application_database,
                                      parent=theta_table)
        theta_table.setModel(theta_model)

        theta_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        sel_var_table = self.ui.outvariableTableView
        sel_var_model = VariableSelectionTableModel(self.application_database,
                                                    parent=sel_var_table)
        sel_var_table.setModel(sel_var_model)

        sel_var_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        metric_table = self.ui.crossValMetricTableView
        metric_model = CrossValidationMetricsTableModel(parent=metric_table)
        metric_table.setModel(metric_model)

        metric_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        # bounds and estimate double value delegate
        self._lb_delegate = DoubleEditorDelegate()
        self._ub_delegate = DoubleEditorDelegate()
        self._theta0_delegate = DoubleEditorDelegate()

        theta_table.setItemDelegateForColumn(1, self._lb_delegate)
        theta_table.setItemDelegateForColumn(2, self._ub_delegate)
        theta_table.setItemDelegateForColumn(3, self._theta0_delegate)

        # checkbox delegate for selected output variables
        self._check_delegate = CheckBoxDelegate()
        sel_var_table.setItemDelegateForColumn(0, self._check_delegate)

        # --------------------------- Signals/Slots ---------------------------
        self.ui.generateModelpushButton.clicked.connect(
            self.on_generate_model_pressed)

        self.ui.viewPlotPushButton.clicked.connect(
            self.on_view_graphics_pressed)

        # ---------------------------------------------------------------------

    def on_generate_model_pressed(self):
        # check which variables are elected to model construction
        mtm_var_data = self.application_database.metamodel_selected_data

        if all(not var['Checked'] for var in mtm_var_data):
            msg_title = "No variable chosen for model building!"
            msg_text = ("You have to select at least one variable to have its "
                        "model built!")

            warn_the_user(msg_text, msg_title)

            return

        else:
            X_labels = [row['Alias']
                        for row in self.application_database.input_table_data
                        if row['Type'] == 'Manipulated (MV)']
            Y_labels = [var['Alias'] for var in mtm_var_data if var['Checked']]

        # sampled data
        sampled_data = pd.DataFrame(self.application_database.doe_sampled_data)
        # get converged cases index
        valid_idx = np.logical_or(sampled_data['status'] == True,
                                  sampled_data['status'] == 'ok')

        X = sampled_data.loc[valid_idx, X_labels].to_numpy()
        Y = sampled_data.loc[valid_idx, Y_labels].to_numpy()

        Y_dim = Y.shape[1] if Y.ndim > 1 else 2
        if len(Y_labels) == 1:
            # single variable, convert to column vector
            Y = Y.reshape(-1, 1)

        # regression model
        regr_idx = self.ui.regrComboBox.currentIndex()
        if regr_idx == 0:
            regr = 'poly0'
        elif regr_idx == 1:
            regr = 'poly1'
        else:
            regr = 'poly2'

        # correlation model
        corr_idx = self.ui.corrComboBox.currentIndex()
        corr = 'corrgauss'

        # theta and bounds values
        theta_data = []

        for row in self.application_database.metamodel_theta_data:
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

        if self.ui.kFoldRadioButton.isChecked():
            # KFolds selected
            n_folds = self.ui.kfoldsHorizontalSlider.value()

            # do not suffle the splits because of LHS (random sampling)
            kf = KFold(n_splits=n_folds, shuffle=False)

            # initialize metrics arrays
            k = 0
            mse = np.empty((n_folds, Y_dim))
            mse.fill(np.NaN)

            mae = np.empty(mse.shape)
            mae.fill(np.NaN)

            r2 = np.empty(mse.shape)
            r2.fill(np.NaN)

            evs = np.empty(mse.shape)
            evs.fill(np.NaN)

            for train_idx, test_idx in kf.split(X, Y):
                X_train = X[train_idx, :]
                Y_train = Y[train_idx, :]

                X_test = X[test_idx, :]
                Y_test = Y[test_idx, :]

                Y_pred = np.empty(Y_test.shape)
                Y_pred.fill(np.NaN)

                for j in range(Y_dim):
                    # build the univariate models
                    krmodel = Dace(regression=regr, correlation=corr)
                    krmodel.fit(S=X_train, Y=Y_train[:, j], theta0=theta0,
                                lob=lob, upb=upb)
                    # test the model
                    Y_pred[:, [j]], *_ = krmodel.predict(X_test)

                # evaluate error metrics
                mse[k, :] = mean_squared_error(
                    Y_test, Y_pred, multioutput='raw_values')

                mae[k, :] = mean_absolute_error(
                    Y_test, Y_pred, multioutput='raw_values')

                r2[k, :] = r2_score(Y_test, Y_pred, multioutput='raw_values')

                evs[k, :] = explained_variance_score(
                    Y_test, Y_pred, multioutput='raw_values')

                k += 1

            # overall cross validation metrics
            omse = np.mean(mse, axis=0)
            ormse = omse ** 0.5
            omae = np.mean(mae, axis=0)
            or2 = np.mean(r2, axis=0)
            oev = np.mean(evs, axis=0)

            metric_frame = pd.DataFrame(
                np.vstack((omse, ormse, omae, or2, oev, np.mean(Y, axis=0),
                           np.std(Y, axis=0))),
                index=['OMSE', 'ORMSE', 'OMAE', 'OR2', 'OEV', 'Sample Mean',
                       'Sample Std'],
                columns=Y_labels)

            metric_model = self.ui.crossValMetricTableView.model()
            metric_model.load_data(metric_frame)

        else:
            split_ratio = self.ui.holdoutHorizontalSlider.value() / 100.0

            X_train, X_test, Y_train, Y_test = \
                train_test_split(X, Y, train_size=split_ratio, shuffle=False)

            Y_pred = np.empty(Y_test.shape)
            Y_pred.fill(np.NaN)

            for j in range(Y_dim):
                # build the univariate models
                krmodel = Dace(regression=regr, correlation=corr)
                krmodel.fit(S=X_train, Y=Y_train[:, j], theta0=theta0,
                            lob=lob, upb=upb)
                # test the model
                Y_pred[:, [j]], *_ = krmodel.predict(X_test)

            # store metamodel data for plotting
            self.metamodel_data = {'Y_test': Y_test,
                                   'Y_pred': Y_pred,
                                   'labels': Y_labels}

            # evaluate error metrics
            mse = mean_squared_error(Y_test, Y_pred, multioutput='raw_values')

            rmse = mse ** 0.5

            mae = mean_absolute_error(Y_test, Y_pred, multioutput='raw_values')

            r2 = r2_score(Y_test, Y_pred, multioutput='raw_values')

            evs = explained_variance_score(Y_test, Y_pred,
                                           multioutput='raw_values')

            metric_frame = pd.DataFrame(
                np.vstack((mse, rmse, mae, r2, evs, np.mean(Y, axis=0),
                           np.std(Y, axis=0))),
                index=['MSE', 'RMSE', 'MAE', 'R2', 'EV', 'Sample Mean',
                       'Sample Std'],
                columns=Y_labels)

            metric_model = self.ui.crossValMetricTableView.model()
            metric_model.load_data(metric_frame)

    def on_view_graphics_pressed(self):
        if hasattr(self, 'metamodel_data'):
            dialog = PlotWindow(self.metamodel_data)
            dialog.exec_()


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook
    from tests_.mock_data import DOE_TAB_MOCK_DS

    app = QApplication(sys.argv)
    ds = DOE_TAB_MOCK_DS
    w = MetamodelTab(application_database=ds)
    w.show()

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
