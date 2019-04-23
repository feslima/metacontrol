from gui.models.sampling import runCase
from gui.models.sim_connections import AspenConnection
from gui.models.data_storage import DataStorage

from tests_.gui.mock_data import simulation_data, input_table_data, output_table_data, expr_table_data, doe_table_data


mock = DataStorage()
mock.simulation_data = simulation_data
mock.input_table_data = input_table_data
mock.output_table_data = output_table_data
mock.expression_table_data = expr_table_data
mock.doe_data = doe_table_data

sim_file_name = r'C:\Users\Felipe\Desktop\GUI\python\infill.bkp'

aspen_con = AspenConnection(sim_file_name)

tst = runCase(mock, [11., 0.75], aspen_con.GetConnectionObject())
