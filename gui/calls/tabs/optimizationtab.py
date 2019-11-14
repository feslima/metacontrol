from PyQt5.QtWidgets import QApplication, QWidget

from gui.models.data_storage import DataStorage
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
        # --------------------------- Signals/Slots ---------------------------
        # ---------------------------------------------------------------------


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook

    app = QApplication(sys.argv)

    ds = DataStorage()
    w = OptimizationTab(application_database=ds,
                        parent_tab=None)
    w.show()

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
