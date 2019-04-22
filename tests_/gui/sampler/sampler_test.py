from gui.models.sampling import runCase
from gui.models.sim_connections import AspenConnection
from gui.models.data_storage import DataStorage

from tests_.gui.mock_data import simulation_data, input_table_data, output_table_data, expr_table_data, doe_table_data


mock = DataStorage()
mock.setSimulationDataDictionary(simulation_data)
mock.setInputTableData(input_table_data)
mock.setOutputTableData(output_table_data)
mock.setExpressionTableData(expr_table_data)
mock.setDoeData(doe_table_data)

sim_file_name = r'C:\Users\Felipe\Desktop\GUI\python\infill.bkp'

aspen_con = AspenConnection(sim_file_name)

tst = runCase(mock, [11., 0.75], aspen_con.GetConnectionObject())
