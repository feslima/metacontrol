import pandas as pd
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QApplication, QDialog

from gui.models.data_storage import DataStorage
from gui.views.py_files.lhssettings import Ui_Dialog


class LhsSettingDialog(QDialog):
    def __init__(self, application_database: DataStorage):
        # ------------------------ Internal Variables -------------------------
        self.app_data = application_database

        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # ----------------------- Widget Initialization -----------------------
        lhs_settings = self.app_data.reduced_doe_lhs_settings
        self.ui.lineEditNSamples.setText(str(lhs_settings['n_samples']))
        self.ui.lineEditNIter.setText(str(lhs_settings['n_iter']))
        self.ui.checkBoxIncVertices.setChecked(lhs_settings['inc_vertices'])

        # validators
        n_samples_validator = QIntValidator(3, 1e4, self.ui.lineEditNSamples)
        n_iter_validator = QIntValidator(2, 50, self.ui.lineEditNIter)

        self.ui.lineEditNSamples.setValidator(n_samples_validator)
        self.ui.lineEditNIter.setValidator(n_iter_validator)

        # --------------------------- Signals/Slots ---------------------------
        self.ui.buttonBox.accepted.connect(self.set_lhs_settings)

        # ---------------------------------------------------------------------

    def set_lhs_settings(self):
        lhs_set = {'n_samples': int(self.ui.lineEditNSamples.text()),
                   'n_iter': int(self.ui.lineEditNIter.text()),
                   'inc_vertices': self.ui.checkBoxIncVertices.isChecked()}

        self.app_data.reduced_doe_lhs_settings = pd.Series(lhs_set)
