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
