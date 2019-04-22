import pathlib
from gui.models.data_storage import DataStorage, read_data, write_data

from tests_.gui.mock_data import simulation_data, input_table_data, output_table_data, expr_table_data, doe_table_data, \
    sim_file_name

mock = DataStorage()

# mock.setDoeData(doe_table_data)
mock.setSimulationDataDictionary(simulation_data)
mock.setInputTableData(input_table_data)
mock.setOutputTableData(output_table_data)
mock.setExpressionTableData(expr_table_data)
mock.setDoeData(doe_table_data)

out_file = pathlib.Path(__file__).parent / "test_file.mtc"

write_data(out_file, sim_file_name, mock)
read_data(out_file, DataStorage())
