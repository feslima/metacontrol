import sys
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import Qt, QEvent
from gui.views.loadSimulationTree import *
from gui.models.load_simulation import construct_tree_items, read_simulation_tree


class LoadSimulationTreeDialog(QDialog):
	def __init__(self, streams_file_path, blocks_file_path):
		super().__init__()  # initialize the QDialog
		self.ui = Ui_Dialog()  # instantiate the Dialog Window
		self.ui.setupUi(self)  # call the setupUi function to create and lay the window

		self.ui.pushButtonOK.clicked.connect(self.close)  # closes window when button is pressed

		self.ui.treeViewInput.doubleClicked.connect(self.treeDoubleClick)  # assign double click event
		self.ui.treeViewOutput.doubleClicked.connect(self.treeDoubleClick)

		self.ui.tableWidgetInput.setColumnWidth(0, 550)  # first column resizing
		self.ui.tableWidgetOutput.setColumnWidth(0, 550)

		# create the model for the tree
		model_tree_input = QStandardItemModel()
		model_tree_output = QStandardItemModel()

		model_tree_input.setHorizontalHeaderLabels(['Input variables'])
		model_tree_output.setHorizontalHeaderLabels(['Output variables'])

		self.ui.treeViewInput.setModel(model_tree_input)
		self.ui.treeViewOutput.setModel(model_tree_output)

		# make the qtreeview headers bold
		self.ui.treeViewInput.header().setStyleSheet('QWidget { font: bold }')
		self.ui.treeViewOutput.header().setStyleSheet('QWidget { font: bold }')

		# Populate the data

		# load the stream tree
		stream_raw = read_simulation_tree(streams_file_path)
		stream_input, stream_output = construct_tree_items(stream_raw)
		model_tree_input.appendRow(stream_input)
		model_tree_output.appendRow(stream_output)

		# load the blocks tree
		blocks_raw = read_simulation_tree(blocks_file_path)
		blocks_input, blocks_output = construct_tree_items(blocks_raw)
		model_tree_input.appendRow(blocks_input)
		model_tree_output.appendRow(blocks_output)

	def keyPressEvent(self, event):
		if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Delete:  # if delete key was pressed
			if self.ui.tableWidgetInput.hasFocus():  # and is inside the table widget
				table_model = self.ui.tableWidgetInput.selectionModel()
				indices = table_model.selectedRows()

				for index in indices:
					self.ui.tableWidgetInput.removeRow(index.row())  # delete selected rows

	def treeDoubleClick(self):
		"""
		Event handling associated with a double click of a single LEAF node of the tree
		"""
		tree_name = self.sender().objectName()

		tree_view = self.ui.treeViewInput if tree_name == 'treeViewInput' else self.ui.treeViewOutput

		table_view = self.ui.tableWidgetInput if tree_name == 'treeViewInput' else self.ui.tableWidgetOutput

		# get QModelIndex object of selected item. (It's a "pointer" in the QStandardModelItem)
		index_selected = tree_view.currentIndex()

		# get tree model
		tree_model = tree_view.model()

		if not tree_model.itemFromIndex(index_selected).hasChildren():
			# Only proceed if the selected node is a leaf (i.e. has no children)

			# get QStandardItem of the node clicked
			parent_node_std_item = tree_model.itemFromIndex(index_selected).parent()

			# construct the node path
			branch_list = [tree_model.data(index_selected).lstrip()]  # initialization

			while parent_node_std_item is not None:
				parent_node_name = parent_node_std_item.text().lstrip()
				branch_list.append(parent_node_name)
				parent_node_std_item = parent_node_std_item.parent()

			# create full path name
			branch_str = '\\' + '\\'.join(list(reversed(branch_list)))

			# verify if the entry is already in the table
			row_position = table_view.rowCount()  # count the current number of rows

			if row_position != 0:  # table is not empty
				row_list = []
				for i in range(row_position):
					row_list.append(table_view.model().index(i, 0).data())  # get all rows in table

				if branch_str not in row_list:  # there isn't the value in table. Insert it
					table_view.insertRow(row_position)

					table_item_path = QtWidgets.QTableWidgetItem(branch_str)

					table_item_path.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # disable edit of the first col
					table_view.setItem(row_position, 0, table_item_path)
					table_view.setItem(row_position, 1, QtWidgets.QTableWidgetItem('Alias_' + str(row_position)))

				else:
					# warn the user
					msg_box = QtWidgets.QMessageBox()
					msg_box.setIcon(QtWidgets.QMessageBox.Warning)
					msg_box.setText("The selected variable is already the table!")
					msg_box.setWindowTitle("Duplicated variable")
					msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)

					msg_box.exec()
			else:
				table_view.insertRow(row_position)  # insert an empty row

				table_item_path = QtWidgets.QTableWidgetItem(branch_str)

				table_item_path.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # disable edit of the first col
				table_view.setItem(row_position, 0, table_item_path)
				table_view.setItem(row_position, 1, QtWidgets.QTableWidgetItem('Alias_' + str(row_position)))



if __name__ == '__main__':
	app = QApplication(sys.argv)

	stream_file = "/home/felipe/Desktop/GUI/python/AspenTreeStreams - Input _ Output.txt"
	blocks_file = "/home/felipe/Desktop/GUI/python/AspenTreeBlocks - Input _ Output.txt"
	w = LoadSimulationTreeDialog(stream_file, blocks_file)
	w.show()

	sys.exit(app.exec_())
