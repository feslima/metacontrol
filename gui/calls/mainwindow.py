import pathlib

from PyQt5.QtCore import QRegExp, Qt, QAbstractItemModel
from PyQt5.QtWidgets import (QApplication, QFileDialog, QItemDelegate,
                             QLineEdit, QMainWindow, QMessageBox, QComboBox)

from gui.models.data_storage import DataStorage
from gui.views.py_files.mainwindow import Ui_MainWindow
from gui.calls.tabs.loadsimtab import LoadSimTab
from gui.calls.tabs.doetab import DoeTab
from gui.calls.tabs.metamodeltab import MetamodelTab
from gui.calls.tabs.optimizationtab import OptimizationTab
from gui.calls.tabs.reducedspacetab import ReducedSpaceTab
from gui.calls.tabs.hessianextractiontab import HessianExtractionTab
from gui.calls.tabs.soctab import SocTab


class MainWindow(QMainWindow):
    _DOETAB_IDX = 1
    _METAMODELTAB_IDX = 2
    _OPTTAB_IDX = 3
    _REDSPACETAB_IDX = 4
    _HESSIANTAB_IDX = 5
    _SOCTAB_IDX = 6

    def __init__(self):
        # ------------------------- UI Initialization -------------------------
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowState(Qt.WindowMaximized)
        self.setWindowTitle('Metacontrol - untitled.mtc')

        maintab = self.ui.tabMainWidget

        # disable the tabs
        maintab.setTabEnabled(self._DOETAB_IDX, False)
        maintab.setTabEnabled(self._METAMODELTAB_IDX, False)
        maintab.setTabEnabled(self._OPTTAB_IDX, False)
        maintab.setTabEnabled(self._HESSIANTAB_IDX, False)
        maintab.setTabEnabled(self._SOCTAB_IDX, False)

        # ------------------------ Internal variables -------------------------
        self.application_database = DataStorage()

        # ----------------------- Load the tabs widgets -----------------------
        self.tab_loadsim = LoadSimTab(self.application_database,
                                      parent_tab=self.ui.simulationTab)
        self.tab_doe = DoeTab(self.application_database,
                              parent_tab=self.ui.samplingTab)
        self.tab_metamodel = MetamodelTab(self.application_database,
                                          parent_tab=self.ui.metamodelTab)
        self.tab_optimization = OptimizationTab(self.application_database,
                                                parent_tab=self.ui.optimizationTab)
        self.tab_reducedspace = ReducedSpaceTab(self.application_database,
                                                parent_tab=self.ui.reducedspaceTab)
        self.tab_hessianext = HessianExtractionTab(self.application_database,
                                                   parent_tab=self.ui.hessianextractionTab)
        self.tab_soc = SocTab(self.application_database,
                              parent_tab=self.ui.socTab)

        # ------------------------ Actions connections ------------------------
        self.ui.actionOpen.triggered.connect(self.open_file)
        self.ui.actionSave.triggered.connect(self.save_file)
        self.ui.actionSave_As.triggered.connect(self.save_file_as)

        # --------------------------- Signals/Slots ---------------------------
        # sampling tab enabled
        self.application_database.sampling_enabled.connect(
            self.on_sampling_enabled)

        # metamodel tab enabled
        self.application_database.metamodel_enabled.connect(
            self.on_metamodel_enabled)

        # optimization tab enabled
        self.application_database.metamodel_enabled.connect(
            self.on_optimization_enabled)

        # hessian tab enabled
        self.application_database.hessian_enabled.connect(
            self.on_hessianextraction_enabled)

        # soc tab enabled
        self.application_database.soc_enabled.connect(
            self.on_soc_enabled
        )

    def open_file(self):
        """Prompts the user to select which .mtc file to open.
        """
        homedir = pathlib.Path().home()
        mtc_filename, _ = \
            QFileDialog.getOpenFileName(self,
                                        "Select the .mtc file to open.",
                                        str(homedir),
                                        "Metacontrol files (*.mtc)")

        if mtc_filename != "":
            # the user provided a valid file (did not canceled the dialog).
            self.application_database.load(mtc_filename)

            # update the window title
            self.setWindowTitle("Metacontrol - " + mtc_filename)

    def save_file(self):
        """Saves the current application configuration as is. If it is a new
        file prompts the user to select the location and name of the .mtc file.
        """
        current_mtc_name = self.windowTitle().split(' - ')[1]

        if pathlib.Path(current_mtc_name).is_file():
            # file exists, save it
            self.application_database.save(current_mtc_name)
        else:
            # new file, prompt the user
            self.save_file_as()

    def save_file_as(self):
        """Prompts the user to select location and name of the .mtc file to
        save.
        """
        dialog_title = "Select the name and where to save the .mtc file"
        filetype = "Metacontrol files (*.mtc)"
        homedir = pathlib.Path().home()
        mtc_filepath, _ = QFileDialog.getSaveFileName(self,
                                                      dialog_title,
                                                      str(homedir),
                                                      filetype)
        if mtc_filepath != '':
            # change the window title
            self.setWindowTitle("Metacontrol - " + mtc_filepath)

            # save the file
            self.application_database.save(mtc_filepath)

    def on_sampling_enabled(self, is_enabled):
        self.ui.tabMainWidget.setTabEnabled(self._DOETAB_IDX, is_enabled)

    def on_metamodel_enabled(self, is_enabled):
        self.ui.tabMainWidget.setTabEnabled(self._METAMODELTAB_IDX, is_enabled)

    def on_optimization_enabled(self, is_enabled):
        self.ui.tabMainWidget.setTabEnabled(self._OPTTAB_IDX, is_enabled)

    def on_hessianextraction_enabled(self, is_enabled):
        self.ui.tabMainWidget.setTabEnabled(self._HESSIANTAB_IDX, is_enabled)

    def on_soc_enabled(self, is_enabled):
        self.ui.tabMainWidget.setTabEnabled(self._SOCTAB_IDX, is_enabled)


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
