import numpy as np
import pandas as pd
from pydace import Dace
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QApplication, QDialog, QHeaderView
from sklearn.metrics import (explained_variance_score, mean_absolute_error,
                             mean_squared_error, r2_score)
from sklearn.model_selection import KFold, train_test_split

from gui.calls.base import (CheckBoxDelegate, DoubleEditorDelegate,
                            warn_the_user)
from gui.calls.tabs.metamodeltab import (CrossValidationMetricsTableModel,
                                         PlotWindow, ThetaTableModel,
                                         VariableSelectionTableModel)
from gui.models.data_storage import DataStorage
from gui.views.py_files.redspacemetamodeldialog import Ui_Dialog


class ReducedThetaTableModel(ThetaTableModel):
    def load_data(self):
        # overload to read reduced data
        self.layoutAboutToBeChanged.emit()
        self.theta_data = self.app_data.reduced_metamodel_theta_data
        self.layoutChanged.emit()


class RedVarSelectionTableModel(VariableSelectionTableModel):
    def load_data(self):
        self.layoutAboutToBeChanged.emit()
        self.variables = self.app_data.reduced_metamodel_selected_data
        self.layoutChanged.emit()

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

            self.app_data.reduced_selected_data_changed.emit()

            return True

        return False


class ReducedSpaceMetamodelDialog(QDialog):
    def __init__(self, application_data: DataStorage):
        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Window)
        self.setWindowState(Qt.WindowMaximized)

        # ------------------------ Internal Variables -------------------------
        self.application_database = application_data

        # ----------------------- Widget Initialization -----------------------
        theta_table = self.ui.thetaTableView
        theta_model = ReducedThetaTableModel(self.application_database,
                                             parent=theta_table)
        theta_table.setModel(theta_model)

        theta_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        sel_var_table = self.ui.outvariableTableView
        sel_var_model = RedVarSelectionTableModel(self.application_database,
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
            self.on_train_reduced_metamodel_pressed
        )

        self.ui.viewPlotPushButton.clicked.connect(
            self.on_view_plots_pressed
        )

        self.ui.confirmPushButton.clicked.connect(
            self.on_confirm_pressed
        )
        # ---------------------------------------------------------------------

    def on_train_reduced_metamodel_pressed(self):
        app_data = self.application_database
        mtm_var_data = app_data.reduced_metamodel_selected_data

        if not mtm_var_data.loc[:, 'Checked'].any():
            msg_title = "No variable chosen for model building!"
            msg_text = ("You have to select at least one variable to have its "
                        "model built!")

            warn_the_user(msg_text, msg_title)

            return

        else:
            # get reduced space inputs from reduced theta data
            t_data = self.application_database.reduced_metamodel_theta_data
            X_labels = t_data.loc[:, 'Alias'].tolist()

            # outputs from all the reduced selected data
            Y_labels = mtm_var_data.loc[
                mtm_var_data['Checked'], 'Alias'
            ].tolist()

        # sampled data
        sampled_data = self.application_database.reduced_doe_sampled_data

        X = sampled_data.loc[
            (sampled_data['status'] == 'ok'),
            X_labels
        ].to_numpy()
        Y = sampled_data.loc[
            (sampled_data['status'] == 'ok'),
            Y_labels
        ].to_numpy()

        Y_dim = Y.shape[1] if Y.ndim > 1 else 1
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
        theta_data = \
            self.application_database.reduced_metamodel_theta_data.set_index(
                'Alias')

        theta0 = theta_data.loc[X_labels, 'theta0'].tolist()
        lob = theta_data.loc[X_labels, 'lb'].tolist()
        upb = theta_data.loc[X_labels, 'ub'].tolist()

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

    def on_view_plots_pressed(self):
        if hasattr(self, 'metamodel_data'):
            dialog = PlotWindow(self.metamodel_data)
            dialog.exec_()

    def on_confirm_pressed(self):
        if self.ui.regrComboBox.currentText() == "Constant (0th order)":
            self.application_database.differential_regression_model = 'poly0'
        elif self.ui.regrComboBox.currentText() == "Linear (1st order)":
            self.application_database.differential_regression_model = 'poly1'
        else:
            raise NotImplementedError("Invalid regression option!")

        if self.ui.corrComboBox.currentText() == \
                "Exponential Gaussian (Kriging)":
            self.application_database.differential_correlation_model = \
                'corrgauss'
        else:
            raise NotImplementedError("Invalid correlation option!")

        self.close()


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook
    from tests_.mock_data import REDSPACE_TAB_MOCK_DS

    app = QApplication(sys.argv)
    ds = REDSPACE_TAB_MOCK_DS
    w = ReducedSpaceMetamodelDialog(application_data=ds)
    w.show()

    sys.exepthook = my_exception_hook
    sys.exit(app.exec_())
