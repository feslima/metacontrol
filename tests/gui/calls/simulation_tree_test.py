import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
sys.path.extend(['C:\\Users\\Felipe\\PycharmProjects\\metacontrol', 'C:/Users/Felipe/PycharmProjects/metacontrol'])
from gui.calls.callsimulationtree import LoadSimulationTreeDialog
from gui.models.data_storage import DataStorage

if __name__ == '__main__':
    app = QApplication(sys.argv)
    stream_file = r"C:\Users\Felipe\Desktop\GUI\python\AspenTreeStreams - Input & Output.txt"
    blocks_file = r"C:\Users\Felipe\Desktop\GUI\python\AspenTreeBlocks - Input & Output.txt"
    filepath = r"C:\Users\Felipe\Desktop\GUI\python\infill.bkp"

    # w = LoadSimulationTreeDialog(filepath)
    gui_data_storage = DataStorage()

    input_table_data = [{'Path': r"\Data\Blocks\TOWER\Output\MOLE_RR", 'Alias': 'rr', 'Type': 'Manipulated (MV)'},
                        {'Path': r"\Data\Blocks\TOWER\Output\MOLE_DFR", 'Alias': 'df', 'Type': 'Manipulated (MV)'}]

    output_table_data = [{'Path': r"\Data\Streams\D\Output\TOT_FLOW", 'Alias': 'd', 'Type': 'Auxiliary'},
                         {'Path': r"\Data\Streams\B\Output\MOLEFRAC\MIXED\PROPENE", 'Alias': 'xb',
                          'Type': 'Candidate (CV)'},
                         {'Path': r"\Data\Streams\B\Output\TOT_FLOW", 'Alias': 'b', 'Type': 'Auxiliary'},
                         {'Path': r"\Data\Blocks\TOWER\Output\REB_DUTY", 'Alias': 'qr', 'Type': 'Auxiliary'},
                         {'Path': r"\Data\Blocks\TOWER\Output\MOLE_L1", 'Alias': 'l', 'Type': 'Auxiliary'},
                         {'Path': r"\Data\Blocks\TOWER\Output\MOLE_VN", 'Alias': 'v', 'Type': 'Auxiliary'},
                         {'Path': r"\Data\Streams\FEED\Output\TOT_FLOW", 'Alias': 'f', 'Type': 'Auxiliary'},
                         {'Path': r"\Data\Streams\D\Output\MOLEFRAC\MIXED\PROPENE", 'Alias': 'xd',
                          'Type': 'Candidate (CV)'}]

    # for non empty table
    # gui_data_storage.setInputTableData(input_table_data)
    # gui_data_storage.setOutputTableData(output_table_data)

    w = LoadSimulationTreeDialog(filepath, gui_data_storage,
                                 streams_file_txt_path=stream_file, blocks_file_txt_path=blocks_file)

    w.show()

    def my_exception_hook(exctype, value, tback):
        # Print the error and traceback
        # print(exctype, value, traceback)
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText(traceback.format_exception(exctype, value, tback)[-1])
        error_dialog.setDetailedText(''.join(traceback.format_exception(exctype, value, tback)))

        error_dialog.exec_()
        # Call the normal Exception hook after
        sys._excepthook(exctype, value, tback)
        sys.exit()

        # Back up the reference to the exceptionhook


    sys._excepthook = sys.excepthook

    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook

    sys.exit(app.exec_())
