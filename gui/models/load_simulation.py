import re

import numpy as np
from PyQt5.QtGui import QStandardItem


def read_simulation_tree(filepath):
	# read the data
	with open(filepath, 'r') as file:
		data = file.readlines()

	data = [line.rstrip('\n') for line in data]  # remove newline delimiter

	return data


def spread_tree(base_branch_cells):
	"""
	This function receives de raw tree in list format and "sifts" it. Each depth level is associated to a column.

	Parameters
	----------
	base_branch_cells : list
		Input list containg treedata in raw format. Each line corresponds to a node

	Returns
	-------
	spread_tree_matrix : numpy.array(dtype=object)
		Array of size m-by-n where m is the number of lines in `base_branch_cells` and n is the deepest level of the
		branch.

	"""
	# search for lowest leaf and branch level. Starting from zero
	lowest_leaf_level = 0

	while len([i for i, e in enumerate(base_branch_cells)
			   if re.search('-- \({0}\.L\)'.format(lowest_leaf_level), e)]) == 0:
		lowest_leaf_level += 1

	max_leaf_level = lowest_leaf_level

	while True:
		if len([i for i, e in enumerate(base_branch_cells)
				if re.search('-- \({0}\.L\)'.format(max_leaf_level), e)]) != 0:
			max_leaf_level += 1
		else:
			max_leaf_level -= 1
			break

	lowest_branch_level = 0
	while len([i for i, e in enumerate(base_branch_cells)
			   if re.search('-- \({0}\.B\)'.format(lowest_branch_level), e)]) == 0:
		lowest_branch_level += 1

	spread_tree_matrix = np.full((len(base_branch_cells), len(np.arange(lowest_branch_level, max_leaf_level + 2))),
								 '', dtype=object)

	# fill branches first
	column_index = 0
	for j in np.arange(lowest_branch_level, max_leaf_level + 1):
		aux_branch_placeholder = [i for i, e in enumerate(base_branch_cells)
								  if re.search('-- \({0}\.B\)'.format(j), e)]
		spread_tree_matrix[aux_branch_placeholder, column_index] = [base_branch_cells[i]
																	for i in aux_branch_placeholder]

		if j >= lowest_leaf_level:  # fill leaves
			aux_leaf_placeholder = [i for i, e in enumerate(base_branch_cells)
									if re.search('-- \({0}\.L\)'.format(j), e)]
			spread_tree_matrix[aux_leaf_placeholder, column_index + 1] = [base_branch_cells[i]
																		  for i in aux_leaf_placeholder]

		column_index += 1

	return spread_tree_matrix


def build_node_level(nonempty_index, level_number, number_of_nodes, spread_tree_matrix):
	# TODO: (10/03/2019) Write documentation
	node_cell_vector = np.full((number_of_nodes, 1), '', dtype=object)

	for i in np.arange(nonempty_index.size):
		# construct the nodes individually
		node_raw = spread_tree_matrix[nonempty_index[i], level_number]
		branch_delimiter = re.search(' -- \(\d\.B\)', node_raw)

		if branch_delimiter is not None:  # is a branch
			node_name = node_raw[:branch_delimiter.span()[0]]
		else:
			leaf_delimiter = re.search(' = ', node_raw)
			node_name = node_raw[:leaf_delimiter.span()[0]]

		node_cell_vector[nonempty_index[i]] = QStandardItem(node_name)
		node_cell_vector[nonempty_index[i], 0].setEditable(False)

	return node_cell_vector


def build_nodes(spread_tree_matrix):
	# TODO: (10/03/2019) Write documentation
	number_of_nodes, number_of_levels = spread_tree_matrix.shape

	for j in np.arange(number_of_levels - 1, 0, -1):  # start from the deepest level
		# get non-empty element indexes
		nonempty_current_level = np.nonzero(spread_tree_matrix[:, j] != '')[0]
		nonempty_previous_level = np.nonzero(spread_tree_matrix[:, j - 1] != '')[0]

		# identify parents of the current levels in previous levels. First column is the row number of the child,
		# second column is the row number of the parent
		child_parent_address = np.full((nonempty_current_level.size, 2), '', dtype=object)

		for k in np.arange(nonempty_current_level.size):
			index_probe = nonempty_current_level[k]

			while True:
				if spread_tree_matrix[index_probe, j - 1] == '':
					index_probe -= 1
				else:
					child_parent_address[k, :] = np.hstack((nonempty_current_level[k], index_probe))
					break

		# create cell node vector for each level

		if j == number_of_levels - 1:  # if j is the first, initialize current level
			current_level_node_vector = build_node_level(nonempty_current_level, j,
														 number_of_nodes, spread_tree_matrix)
		else:  # otherwise, set the previous level as the current one
			current_level_node_vector = previous_level_node_vector

		previous_level_node_vector = build_node_level(nonempty_previous_level, j - 1,
													  number_of_nodes, spread_tree_matrix)

		# bind child to parent
		for p in np.arange(nonempty_current_level.size):
			previous_level_node_vector[child_parent_address[p, 1], 0].appendRow(
				current_level_node_vector[child_parent_address[p, 0], 0])

	return previous_level_node_vector


def construct_tree_items(data_list):
	"""
	Only working for Aspen plus tree

	Parameters
	----------
	data_list ; list
		String list containg the raw data tree. The first line has to be a single root node.

	Returns
	-------
	out : tuple
		Tuple containing input and output nodes.
	"""
	# equipment or streams name - level 1 (Branch)
	# input or output - level 2 (Branch)
	# vars - level 2 (leaf) or 3 onwards (Branch or leaf)

	# get all indexes of all equipments / streams
	level_1_index = [index for index, e in enumerate(data_list) if re.search(' -- \(1\.B\)', e)]

	# get input indexes (level 2)
	inpt_index = [index for index, e in enumerate(data_list) if re.search('Input -- \(2\.B\)', e)]

	# get output start and end indexes
	outpt_start_index = [index for index, e in enumerate(data_list) if re.search('Output -- \(2\.B\)', e)]
	outpt_end_index = [index for index, e in enumerate(data_list) if re.search('CC Nodes -- \(2\.B\)', e)]

	input_section = []
	output_section = []

	for i in range(len(inpt_index)):
		# extract leaves and branches from raw data list
		inpt_vars_raw = data_list[inpt_index[i]:(outpt_start_index[i])]
		outpt_vars_raw = data_list[outpt_start_index[i]:(outpt_end_index[i])]

		input_nodes_cell = build_nodes(spread_tree(inpt_vars_raw))
		output_nodes_cell = build_nodes(spread_tree(outpt_vars_raw))

		# assign nodes to equipments
		equip_name_raw = data_list[level_1_index[i]]
		equip_delimiter = re.search(' -- \(1\.B\)', equip_name_raw)
		equip_name = equip_name_raw[:equip_delimiter.span()[0]]

		input_section.append(QStandardItem(equip_name))
		input_section[-1].setEditable(False)
		for j in np.arange(input_nodes_cell.size):
			if input_nodes_cell[j, 0] != '':
				input_section[i].appendRow(input_nodes_cell[j, 0])

		output_section.append(QStandardItem(equip_name))
		output_section[-1].setEditable(False)
		for j in np.arange(output_nodes_cell.size):
			if output_nodes_cell[j, 0] != '':
				output_section[i].appendRow(output_nodes_cell[j, 0])

	root_name_raw = data_list[0]
	root_delimiter = re.search(' -- \(0\.B\)', root_name_raw)
	root_name = root_name_raw[:root_delimiter.span()[0]]

	root_input_node = (QStandardItem(root_name))
	root_input_node.setEditable(False)
	root_output_node = (QStandardItem(root_name))
	root_output_node.setEditable(False)

	for i in np.arange(len(input_section)):
		root_input_node.appendRow(input_section[i])
		root_output_node.appendRow(output_section[i])

	return root_input_node, root_output_node
