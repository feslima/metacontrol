from gui.models.load_simulation import construct_tree_items, read_simulation_tree

stream_file = "/home/felipe/Desktop/GUI/python/AspenTreeStreams - Input _ Output.txt"


def extract_name(node_string):
    end_index = node_string.find(' =')  # search for equal symbol first

    if end_index == -1:  # string has no equal
        end_index = node_string.find(' --')

    return node_string[:end_index].lstrip()  # the lstrip is to remove any leading whitespaces


dt = read_simulation_tree(stream_file)

input_node, output_node = construct_tree_items(dt)