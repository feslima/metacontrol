from PyQt5.QtGui import QStandardItemModel


class DataStorage(object):
    """
    Application data storage. This is for reuse of application data such as tree models, simulation data, aliases,
    expressions, etc.
    """
    def __init__(self):
        self._input_tree_model = None
        self._output_tree_model = None
        self._simulation_data = None
        self._input_table_data = None
        self._output_table_data = None
        self._expression_table_data = None
        self._doe_data = None

    def getInputTreeModel(self):
        return self._input_tree_model

    def setInputTreeModel(self, tree_model):

        if isinstance(tree_model, QStandardItemModel):
            self._input_tree_model = tree_model
        else:
            raise TypeError("Input must be a QStandardItemModel class object.")

    def getOutputTreeModel(self):
        return self._output_tree_model

    def setOutputTreeModel(self, tree_model):

        if isinstance(tree_model, QStandardItemModel):
            self._output_tree_model = tree_model
        else:
            raise TypeError("Input must be a QStandardItemModel class object.")

    def getSimulationDataDictionary(self):
        return self._simulation_data

    def setSimulationDataDictionary(self, simulation_dictionary):

        if isinstance(simulation_dictionary, dict):
            self._simulation_data = simulation_dictionary
        else:
            raise TypeError("Input must be a dictionary object.")

    def getInputTableData(self):
        return self._input_table_data

    def setInputTableData(self, table_model):

        if isinstance(table_model, list):
            self._input_table_data = table_model
        else:
            raise TypeError("Input must be a list.")

    def getOutputTableData(self):
        return self._output_table_data

    def setOutputTableData(self, table_model):

        if isinstance(table_model, list):
            self._output_table_data = table_model
        else:
            raise TypeError("Input must be a list.")

    def getExpressionTableData(self):
        return self._expression_table_data

    def setExpressionTableData(self, expression_data):

        if isinstance(expression_data, list):
            self._expression_table_data = expression_data
        else:
            raise TypeError("Input must be a list.")

    def getDoeData(self):
        return self._doe_data

    def setDoeData(self, doe_data):

        if isinstance(doe_data, dict):
            self._doe_data = doe_data
        else:
            raise TypeError("Input must be a dictionary object.")
