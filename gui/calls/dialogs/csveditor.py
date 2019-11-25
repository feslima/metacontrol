import pathlib

import numpy as np
import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QObject
from PyQt5.QtGui import QBrush, QPalette
from PyQt5.QtWidgets import (QApplication, QDialog, QFileDialog, QHeaderView,
                             QMessageBox)

from gui.calls.base import CheckBoxDelegate, ComboBoxDelegate, warn_the_user
from gui.calls.dialogs.convergenceselector import ConvergenceSelectorDialog
from gui.models.data_storage import DataStorage
from gui.views.py_files.csveditor import Ui_Dialog


class pandasModel(QAbstractTableModel):
    """Table model template to load pandas dataframes. The first row is where
    the user decides if it is to use extract from the dataframe through
    checkboxes.

    In the second row, the user selects which alias the column from
    the dataframe will be renamed through a combobox. This second row can only
    be defined if the checkbox in the first row, for that column, is checked.

    Parameters
    ----------
    dataframe : pd.DataFrame
        The pandas dataframe to be displayed.
    parent: QObject
        The parent QTableView which this model will be attached.
    app_data : DataStorage
        Application data storage.

    Notes
    -----
    The parent of the model has to be explicitly set to its correspondent
    tableview
    """
    _HEADER_ROW_OFFSET = 2

    def __init__(self, dataframe: pd.DataFrame, parent: QObject,
                 app_data: DataStorage):
        QAbstractTableModel.__init__(self, parent)

        self._data = dataframe
        self._app_data = app_data
        self._pair_info = self._app_data.doe_csv_settings['pair_info']

        pair_info = self._pair_info

        if pair_info is None or len(pair_info) == 0:
            # if no dictionary is defined, create a default
            pair_info = {}
            for header in self._data.columns.values:
                pair_info[header] = {'alias': 'Select alias',
                                     'status': False}
            self._app_data.doe_csv_settings['pair_info'] = pair_info
            self._pair_info = pair_info

    def rowCount(self, parent=None):
        return self._data.shape[0] + self._HEADER_ROW_OFFSET

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        row = index.row()
        col = index.column()

        pair_info_alias = self._pair_info[self._data.columns[col]]['alias']
        pair_info_status = self._pair_info[self._data.columns[col]]['status']

        df_rows, df_cols = self._data.shape

        if role == Qt.DisplayRole:
            if self._HEADER_ROW_OFFSET - 1 < row < df_rows + \
                    self._HEADER_ROW_OFFSET:
                # for rows above _HEADER_ROW_OFFSET, display the dataframe
                # values
                val = self._data.iloc[row - self._HEADER_ROW_OFFSET, col]
                if isinstance(val, float):
                    # if the value from csv is float, truncate 8 digits
                    val = "{0:.7f}".format(val)
                else:
                    val = str(val)

                return val

            elif row == 1:
                # the text will be displayed in the combo boxes
                return pair_info_alias

        elif role == Qt.CheckStateRole:
            if row == 0:
                if pair_info_status:
                    return Qt.Checked
                else:
                    return Qt.Unchecked

        elif role == Qt.BackgroundRole:
            if row == 1:
                # cell color behavior of the second row

                # get aliases that have their status true
                checked_data = [(self._pair_info[header]['alias'], col) for
                                col, header in enumerate(self._pair_info)
                                if self._pair_info[header]['status']]

                # get list of aliases that are checked
                aliases, col_num = list(zip(*checked_data)) \
                    if len(checked_data) != 0 else [[], []]

                is_duplicated = True if aliases.count(pair_info_alias) > 1 \
                    and pair_info_status else False

                if (pair_info_alias == 'Select alias' and pair_info_status) \
                        or is_duplicated:
                    return QBrush(Qt.red)
                else:
                    # original color repaint
                    return QBrush(self.parent().palette().brush(QPalette.Base))

        elif role == Qt.TextAlignmentRole:
            # Center align contents
            return Qt.AlignCenter

    def setData(self, index, value, role):
        row = index.row()
        col = index.column()

        if role == Qt.EditRole:
            if row == 0:
                self._pair_info[self._data.columns[col]]['status'] = True \
                    if value == 1 else False

                # emit the datachanged signal to update the table rows
                self.dataChanged.emit(index.sibling(row + 1, col),
                                      index.sibling(self.rowCount(), col))
                return True
            elif row == 1:
                self._pair_info[self._data.columns[col]]['alias'] = value
                return True

        return False

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            # headers names from dataframe/csv
            return self._data.columns[section]

        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            # show vertical headers only the case number
            if self._HEADER_ROW_OFFSET - 1 < section < self._data.shape[0] + \
                    self._HEADER_ROW_OFFSET:
                return self._data.index[section - self._HEADER_ROW_OFFSET]

        return None

    def flags(self, index: QModelIndex):
        row = index.row()
        col = index.column()

        if row == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | \
                Qt.ItemIsEditable
        else:
            if self._pair_info[self._data.columns[col]]['status']:
                if row == 1:
                    # enable editing so that the combobox delegate can act
                    return Qt.ItemIsEnabled | Qt.ItemIsEditable
                else:
                    return Qt.ItemIsEnabled | Qt.ItemIsSelectable
            else:
                # disable all the data rows
                return ~Qt.ItemIsEnabled | Qt.ItemIsSelectable


class CsvEditorDialog(QDialog):
    def __init__(self, application_data: DataStorage):
        # ------------------------ Form Initialization ------------------------
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Window)
        self.setWindowState(Qt.WindowMaximized)

        self.ui.loadFilePushButton.setEnabled(False)
        self.ui.okPushButton.setEnabled(False)

        # ------------------------ Internal Variables -------------------------
        self.app_data = application_data
        # ----------------------- Widget Initialization -----------------------
        display_table = self.ui.displayTableView
        display_table_header = display_table.horizontalHeader()

        display_table_header.setMinimumSectionSize(80)
        display_table_header.setSectionResizeMode(QHeaderView.Stretch)

        # --------------------------- Signals/Slots ---------------------------
        # prompts the user to select the .csv file
        self.ui.openCsvFilePushButton.clicked.connect(self.open_csv_file)

        # loads csv contents into table
        self.ui.loadFilePushButton.clicked.connect(self.load_csv_file)

        # user is finished defining aliases
        self.ui.okPushButton.clicked.connect(self.on_done)
        # ---------------------------------------------------------------------

    def open_csv_file(self):
        """Prompts the user to select the .csv file location.
        """
        homedir = str(pathlib.Path().home())
        dialog_title = "Select .csv containing the DOE data."
        file_type = "Comma Separated Values files (*.csv)"
        csv_filepath, _ = QFileDialog.getOpenFileName(self,
                                                      dialog_title,
                                                      homedir,
                                                      file_type)

        if csv_filepath != "":
            self.ui.lineEditCsvFilePath.setText(csv_filepath)
            self.app_data.doe_csv_settings['filepath'] = csv_filepath
            self.ui.loadFilePushButton.setEnabled(True)
            self.ui.okPushButton.setEnabled(True)
        else:
            self.ui.loadFilePushButton.setEnabled(False)
            self.ui.okPushButton.setEnabled(False)

    def load_csv_file(self):
        """Loads the .csv file contents into the table in display.
        """
        display_view = self.ui.displayTableView
        csv_filepath = self.app_data.doe_csv_settings['filepath']
        if csv_filepath != '':
            df = pd.read_csv(csv_filepath)
            headers = list(df.columns)

            # ask the user which header is the convergence flag
            conv_dialog = ConvergenceSelectorDialog(headers, self.app_data,
                                                    mode='original')

            if conv_dialog.exec_():
                # clear the table model
                if display_view.model() is not None:
                    # forces model deletion
                    display_view.model().setParent(None)
                    display_view.model().deleteLater()

                # Update the keys in the pair info storage: delete the keys
                # that aren't in the headers list, and add the elements from
                #  headers list with default aliases
                pair_info = self.app_data.doe_csv_settings['pair_info']

                for key in list(pair_info):
                    if key not in headers:
                        del pair_info[key]

                for header in headers:
                    if header not in pair_info:
                        pair_info[header] = {'alias': 'Select alias',
                                             'status': False}

                status_index = headers.index(
                    self.app_data.doe_csv_settings['convergence_index'])

                # swap the status column
                headers[status_index], headers[0] = (headers[0],
                                                     headers[status_index])

                df = df.reindex(columns=headers)
                # pair_info = self.app_data.doe_csv_settings['pair_info']

                # create and set models and set row delegates
                table_model = pandasModel(dataframe=df, app_data=self.app_data,
                                          parent=display_view)
                display_view.setModel(table_model)

                # grab defined aliases
                inp_data = self.app_data.input_table_data
                out_data = self.app_data.output_table_data
                input_alias = inp_data.loc[
                    inp_data['Type'] == self.app_data._INPUT_ALIAS_TYPES['mv'],
                    'Alias'].tolist()
                output_alias = out_data.loc[:, 'Alias'].tolist()
                aliases = input_alias + output_alias

                # create delegates with reference anchoring
                self._check_delegate = CheckBoxDelegate()
                self._combo_delegate = ComboBoxDelegate(item_list=aliases)

                display_view.setItemDelegateForRow(0, self._check_delegate)
                display_view.setItemDelegateForRow(1, self._combo_delegate)

    def on_done(self):
        """When the user is done choosing and defining aliases, stores whatever
        was defined/choosen into application storage and close the dialog.
        """
        # check for undefined/duplicated aliases
        pair_info = self.app_data.doe_csv_settings['pair_info']

        checked_vars = [pair_info[header]['alias'] for header in pair_info
                        if pair_info[header]['status']]

        has_undefined = True if 'Select alias' in checked_vars else False

        has_duplicated = True if len(checked_vars) != len(set(checked_vars)) \
            else False

        if (has_undefined and not has_duplicated) or \
                (has_undefined and has_duplicated):
            msg_txt = "You have to define all the variables you chose."
            msg_title = "Undefined variable detected!"

            warn_the_user(msg_txt, msg_title)
        elif not has_undefined and has_duplicated:
            msg_txt = "You can't select the same alias for two columns."
            msg_title = "Duplicated aliased detected!"

            warn_the_user(msg_txt, msg_title)
        else:
            # no duplicates or undefined found. Check if all the aliases from
            # app storage are defined
            inp_data = self.app_data.input_table_data
            out_data = self.app_data.output_table_data
            input_alias = inp_data.loc[
                inp_data['Type'] == self.app_data._INPUT_ALIAS_TYPES['mv'],
                'Alias'].tolist()
            output_alias = out_data.loc[:, 'Alias'].tolist()
            aliases = input_alias + output_alias

            all_defined = True \
                if all(alias in checked_vars for alias in aliases) \
                else False

            if not all_defined:
                msg_txt = ("You have to attribute all the aliases you chose "
                           "from the simulation tree.")
                msg_title = "Not all aliases are defined!"

                warn_the_user(msg_txt, msg_title)
            else:
                # everything is ok, store the data and close the dialog
                # the renaming from comboboxes
                raw_df = self.ui.displayTableView.model()._data

                # checked columns mapping
                rename = dict([(header, pair_info[header]['alias'])
                               for header in pair_info
                               if pair_info[header]['status']])

                # extract checked columns, rename them and rearrange columns
                # following the aliases order
                df = raw_df[rename.keys()].rename(
                    columns=rename).reindex(columns=aliases)

                # append case number and status columns
                stat_idx = self.app_data.doe_csv_settings['convergence_index']
                df.insert(loc=0, column='status', value=raw_df[stat_idx])
                df.insert(loc=0, column='case',
                          value=range(1, df.shape[0] + 1))

                # convert to dict and store in application data
                self.app_data.doe_sampled_data = df

                # close the dialog
                self.close()


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook
    from tests_.mock_data import loadsim_mock, CSVEDIT_PAIRINFO_MOCK

    app = QApplication(sys.argv)

    ds = loadsim_mock()
    ds.doe_csv_settings['pair_info'] = CSVEDIT_PAIRINFO_MOCK
    w = CsvEditorDialog(application_data=ds)
    w.show()

    sys.excepthook = my_exception_hook

    sys.exit(app.exec_())
