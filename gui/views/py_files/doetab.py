# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Felipe\PycharmProjects\metacontrol\gui\views\ui_files\doetab.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1043, 814)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.groupBox_4 = QtWidgets.QGroupBox(Form)
        self.groupBox_4.setStyleSheet("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 9px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 10px;\n"
"    top: 5px;\n"
"    padding: 0 3px 0 3px;\n"
"}")
        self.groupBox_4.setTitle("")
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.tableWidgetResultsDoe = QtWidgets.QTableWidget(self.groupBox_4)
        self.tableWidgetResultsDoe.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidgetResultsDoe.setObjectName("tableWidgetResultsDoe")
        self.tableWidgetResultsDoe.setColumnCount(0)
        self.tableWidgetResultsDoe.setRowCount(0)
        self.tableWidgetResultsDoe.horizontalHeader().setVisible(False)
        self.tableWidgetResultsDoe.horizontalHeader().setStretchLastSection(True)
        self.gridLayout_9.addWidget(self.tableWidgetResultsDoe, 1, 0, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.groupBox_4)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_17.setFont(font)
        self.label_17.setObjectName("label_17")
        self.gridLayout_9.addWidget(self.label_17, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_4, 2, 0, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(Form)
        self.groupBox_3.setStyleSheet("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 9px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 10px;\n"
"    top: 5px;\n"
"    padding: 0 3px 0 3px;\n"
"}")
        self.groupBox_3.setTitle("")
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.csvEditorRadioButton = QtWidgets.QRadioButton(self.groupBox_3)
        self.csvEditorRadioButton.setChecked(False)
        self.csvEditorRadioButton.setObjectName("csvEditorRadioButton")
        self.gridLayout_6.addWidget(self.csvEditorRadioButton, 4, 1, 1, 1)
        self.samplingAssistantRadioButton = QtWidgets.QRadioButton(self.groupBox_3)
        self.samplingAssistantRadioButton.setChecked(True)
        self.samplingAssistantRadioButton.setObjectName("samplingAssistantRadioButton")
        self.gridLayout_6.addWidget(self.samplingAssistantRadioButton, 2, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem1, 2, 0, 1, 1)
        self.label_18 = QtWidgets.QLabel(self.groupBox_3)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_18.setFont(font)
        self.label_18.setObjectName("label_18")
        self.gridLayout_6.addWidget(self.label_18, 0, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        self.gridLayout_6.addItem(spacerItem2, 5, 1, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout_6.addItem(spacerItem3, 3, 1, 1, 1)
        self.groupBox_6 = QtWidgets.QGroupBox(self.groupBox_3)
        self.groupBox_6.setEnabled(True)
        self.groupBox_6.setTitle("")
        self.groupBox_6.setObjectName("groupBox_6")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.openSamplerPushButton = QtWidgets.QPushButton(self.groupBox_6)
        self.openSamplerPushButton.setObjectName("openSamplerPushButton")
        self.horizontalLayout_2.addWidget(self.openSamplerPushButton)
        self.gridLayout_6.addWidget(self.groupBox_6, 2, 2, 1, 2)
        self.tableWidgetInputVariables = QtWidgets.QTableWidget(self.groupBox_3)
        self.tableWidgetInputVariables.setObjectName("tableWidgetInputVariables")
        self.tableWidgetInputVariables.setColumnCount(3)
        self.tableWidgetInputVariables.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetInputVariables.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetInputVariables.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetInputVariables.setHorizontalHeaderItem(2, item)
        self.tableWidgetInputVariables.horizontalHeader().setStretchLastSection(True)
        self.gridLayout_6.addWidget(self.tableWidgetInputVariables, 1, 1, 1, 3)
        self.groupBox = QtWidgets.QGroupBox(self.groupBox_3)
        self.groupBox.setEnabled(False)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.csvImportPushButton = QtWidgets.QPushButton(self.groupBox)
        self.csvImportPushButton.setObjectName("csvImportPushButton")
        self.gridLayout_2.addWidget(self.csvImportPushButton, 0, 0, 1, 1)
        self.gridLayout_6.addWidget(self.groupBox, 4, 2, 1, 2)
        self.gridLayout.addWidget(self.groupBox_3, 0, 0, 1, 1)

        self.retranslateUi(Form)
        self.samplingAssistantRadioButton.toggled['bool'].connect(self.groupBox_6.setEnabled)
        self.csvEditorRadioButton.toggled['bool'].connect(self.groupBox.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_17.setText(_translate("Form", "DOE Results"))
        self.csvEditorRadioButton.setText(_translate("Form", "Load data from CSV file:"))
        self.samplingAssistantRadioButton.setText(_translate("Form", "Generate input from LHS and sample the data:"))
        self.label_18.setText(_translate("Form", "Design of Experiments (DOE) Settings"))
        self.openSamplerPushButton.setText(_translate("Form", "Open Sampling Assistant"))
        item = self.tableWidgetInputVariables.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Variable"))
        item = self.tableWidgetInputVariables.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Lower bound"))
        item = self.tableWidgetInputVariables.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Upper bound"))
        self.csvImportPushButton.setText(_translate("Form", "Import from CSV"))

import icons_rc
