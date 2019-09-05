import pathlib

import numpy as np
import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, QObject, Qt
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QHeaderView

from gui.calls.dialogs.convergenceselector import ConvergenceSelectorDialog
from gui.calls.dialogs.csveditor import CsvEditorDialog, pandasModel
from gui.models.data_storage import DataStorage
from gui.views.py_files.csveditor import Ui_Dialog
from gui.calls.base import ComboBoxDelegate, CheckBoxDelegate, warn_the_user


class ReducedPandasModel(pandasModel):
    def __init__(self, dataframe: pd.DataFrame, parent: QObject,
                 app_data: DataStorage):
        QAbstractTableModel.__init__(self, parent)

        self._data = dataframe
        self._app_data = app_data
        self._pair_info = self._app_data.reduced_doe_csv_settings['pair_info']
        pair_info = self._pair_info

        if pair_info is None or len(pair_info) == 0:
            # if no dictionary is defined, create a default
            pair_info = {}
            for header in self._data.columns.values:
                pair_info[header] = {'alias': 'Select alias',
                                     'status': False}
            self._app_data.doe_csv_settings['pair_info'] = pair_info
            self._pair_info = pair_info


class ReducedCsvEditorDialog(CsvEditorDialog):
    def open_csv_file(self):
        homedir = str(pathlib.Path().home())
        dialog_title = "Select .csv containing the DOE data."
        file_type = "Comma Separated Values files (*.csv)"
        csv_filepath, _ = QFileDialog.getOpenFileName(self,
                                                      dialog_title,
                                                      homedir,
                                                      file_type)

        if csv_filepath != "":
            self.ui.lineEditCsvFilePath.setText(csv_filepath)
            self.app_data.reduced_doe_csv_settings['filepath'] = csv_filepath
            self.ui.loadFilePushButton.setEnabled(True)
            self.ui.okPushButton.setEnabled(True)
        else:
            self.ui.loadFilePushButton.setEnabled(False)
            self.ui.okPushButton.setEnabled(False)

    def load_csv_file(self):
        display_view = self.ui.displayTableView
        csv_filepath = self.app_data.reduced_doe_csv_settings['filepath']
        if csv_filepath != '':
            df = pd.read_csv(csv_filepath)
            headers = list(df.columns)

            # ask the user which header is the convergence flag
            conv_dialog = ConvergenceSelectorDialog(headers, self.app_data,
                                                    mode='reduced')

            if conv_dialog.exec_():
                # clear the table model
                if display_view.model() is not None:
                    # forces model deletion
                    display_view.model().setParent(None)
                    display_view.model().deleteLater()

                # Update the keys in the pair info storage: delete the keys
                # that aren't in the headers list, and add the elements from
                # headers list with default aliases
                pair_info = self.app_data.reduced_doe_csv_settings['pair_info']

                for key in list(pair_info):
                    if key not in headers:
                        del pair_info[key]

                for header in headers:
                    if header not in pair_info:
                        pair_info[header] = {'alias': 'Select alias',
                                             'status': False}

                status_index = headers.index(
                    self.app_data.reduced_doe_csv_settings['convergence_index'])

                # swap the status column
                headers[status_index], headers[0] = (headers[0],
                                                     headers[status_index])

                df = df.reindex(columns=headers)

                # create and set models and set row delegates
                table_model = ReducedPandasModel(dataframe=df,
                                                 app_data=self.app_data,
                                                 parent=display_view)
                display_view.setModel(table_model)

                # grab defined aliases
                input_alias = [row['Alias'] for row in
                               self.app_data.input_table_data
                               if row['Type'] == 'Manipulated (MV)' or
                               row['Type'] == 'Disturbance (d)']
                output_alias = [row['Alias']
                                for row in self.app_data.output_table_data]
                aliases = input_alias + output_alias

                # create delegates with reference anchoring
                self._check_delegate = CheckBoxDelegate()
                self._combo_delegate = ComboBoxDelegate(item_list=aliases)

                display_view.setItemDelegateForRow(0, self._check_delegate)
                display_view.setItemDelegateForRow(1, self._combo_delegate)

    def on_done(self):
        # check for undefined/duplicated aliases
        pair_info = self.app_data.reduced_doe_csv_settings['pair_info']

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
            input_alias = [row['Alias'] for row in
                           self.app_data.input_table_data]
            output_alias = [row['Alias']
                            for row in self.app_data.output_table_data]
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
                stat_idx = self.app_data.reduced_doe_csv_settings['convergence_index']
                df.insert(loc=0, column='status', value=raw_df[stat_idx])
                df.insert(loc=0, column='case',
                          value=range(1, df.shape[0] + 1))

                # convert to dict and store in application data
                self.app_data.reduced_doe_sampled_data = df.to_dict('list')

                # close the dialog
                self.close()


if __name__ == "__main__":
    import sys
    from gui.calls.base import my_exception_hook
    from tests_.mock_data import DOE_TAB_MOCK_DS

    app = QApplication(sys.argv)
    ds = DOE_TAB_MOCK_DS
    w = ReducedCsvEditorDialog(ds)
    w.show()

    sys.excepthook = my_exception_hook
    sys.exit(app.exec_())
