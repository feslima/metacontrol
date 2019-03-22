from gui.models.load_simulation import read_simulation_tree_from_fileobject
from gui.models.sim_connections import AspenConnection

filepath = r"C:\Users\Felipe\Desktop\GUI\python\infill.bkp"

asp_obj = AspenConnection(filepath)

streams_file_object = asp_obj.GenerateTreeFile(r"\Data\Streams")
# blocks_file_object = asp_obj.GenerateTreeFile(r"\Data\Blocks")

data_streams = read_simulation_tree_from_fileobject(streams_file_object)

