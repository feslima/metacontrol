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
def loadsim_mock():
    # loasim and sampling(doe) tabs
    LOADSIM_SAMPLING_MOCK_DS = DataStorage()
    LOADSIM_SAMPLING_MOCK_DS.load(MTC_FOLDER_PATH / 'loadsimtab.mtc')
    LOADSIM_SAMPLING_MOCK_DS.simulation_file = str(ASPEN_BKP_FILE_PATH)

    return LOADSIM_SAMPLING_MOCK_DS


def lhssettings_mock():
    # lhs settings dialog
    _mtc_lhs_settings = {'n_samples': 50, 'n_iter': 10, 'inc_vertices': False}
    LHSSETTINGS_MOCK_DS = DataStorage()
    LHSSETTINGS_MOCK_DS.doe_lhs_settings = _mtc_lhs_settings

    return LHSSETTINGS_MOCK_DS


def doetab_mock():
    # doetab and sampling assistant
    DOE_TAB_MOCK_DS = DataStorage()
    DOE_TAB_MOCK_DS.load(MTC_FOLDER_PATH / 'doetab_sampling_assistant.mtc')
    DOE_TAB_MOCK_DS.simulation_file = str(ASPEN_BKP_FILE_PATH)

    return DOE_TAB_MOCK_DS


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


def redspace_mock():
    # reduced space tab
    REDSPACE_TAB_MOCK_DS = DataStorage()
    REDSPACE_TAB_MOCK_DS.load(MTC_FOLDER_PATH / "reducedspacetab.mtc")
    REDSPACE_TAB_MOCK_DS.simulation_file = str(ASPEN_BKP_FILE_PATH)

    return REDSPACE_TAB_MOCK_DS


def hessian_mock():
    # hessian extraction tab
    HESSIAN_TAB_MOCK_DS = DataStorage()
    HESSIAN_TAB_MOCK_DS.load(MTC_FOLDER_PATH / "hessianextractiontab.mtc")
    HESSIAN_TAB_MOCK_DS.simulation_file = str(ASPEN_BKP_FILE_PATH)

    return HESSIAN_TAB_MOCK_DS


def soc_mock():
    # soc tab
    SOC_TAB_MOC_DS = DataStorage()
    SOC_TAB_MOC_DS.load(MTC_FOLDER_PATH / "soctab.mtc")
    SOC_TAB_MOC_DS.simulation_file = str(ASPEN_BKP_FILE_PATH)

    return SOC_TAB_MOC_DS


def indirect_mock():
    # C3 splitter column - indirect control
    INDIRECT_MOC_DS = DataStorage()
    INDIRECT_MOC_DS.load(MTC_FOLDER_PATH /
                         "indirect control - c3 splitter.mtc")

    return INDIRECT_MOC_DS
