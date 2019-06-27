import pathlib
from gui.models.data_storage import DataStorage

TESTS_FOLDER_PATH = pathlib.Path(__file__).parent

# ------------------------ SIMULATION FOLDER AND FILES ------------------------
SIMULATION_FOLDER_PATH = TESTS_FOLDER_PATH.joinpath(
    TESTS_FOLDER_PATH, 'model_files')
ASPEN_BKP_FILE_PATH = SIMULATION_FOLDER_PATH.joinpath('infill.bkp')

# -------------------------------- MTC FOLDER ---------------------------------
MTC_FOLDER_PATH = TESTS_FOLDER_PATH.joinpath('save_open')


# --------------------------- DATASTORE FOR MOCKING ---------------------------
# loasim and sampling(doe) tabs
LOADSIM_SAMPLING_MOCK_DS = DataStorage()
LOADSIM_SAMPLING_MOCK_DS.load(MTC_FOLDER_PATH / 'loadsim_sampling_test.mtc')
LOADSIM_SAMPLING_MOCK_DS.simulation_file = str(ASPEN_BKP_FILE_PATH)

# lhs settings dialog
_mtc_lhs_settings = {'n_samples': '50', 'n_iter': '10', 'inc_vertices': False}
LHSSETTINGS_MOCK_DS = DataStorage()
LHSSETTINGS_MOCK_DS.doe_lhs_settings = _mtc_lhs_settings

# doetab and sampling assistant
DOE_TAB_MOCK_DS = DataStorage()
DOE_TAB_MOCK_DS.load(MTC_FOLDER_PATH / 'sampling_assistant.mtc')
DOE_TAB_MOCK_DS.simulation_file = str(ASPEN_BKP_FILE_PATH)

# csveditor dialog
CSVEDIT_PAIRINFO_MOCK = {'B': {'alias': 'b', 'status': True},
                         'Case': {'alias': 'Select alias', 'status': False},
                         'D': {'alias': 'd', 'status': True},
                         'DF': {'alias': 'df', 'status': True},
                         'F': {'alias': 'f', 'status': True},
                         'L': {'alias': 'l', 'status': True},
                         'QR': {'alias': 'qr', 'status': True},
                         'RR': {'alias': 'rr', 'status': True},
                         'Status': {'alias': 'Select alias', 'status': False},
                         'V': {'alias': 'v', 'status': True},
                         'XB': {'alias': 'xb', 'status': True},
                         'XD': {'alias': 'xd', 'status': True}}
