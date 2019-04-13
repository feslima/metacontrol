# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_files\doetab.ui'
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
        self.radioButton_3 = QtWidgets.QRadioButton(self.groupBox_3)
        self.radioButton_3.setChecked(False)
        self.radioButton_3.setObjectName("radioButton_3")
        self.gridLayout_6.addWidget(self.radioButton_3, 4, 1, 1, 1)
        self.radioButton_4 = QtWidgets.QRadioButton(self.groupBox_3)
        self.radioButton_4.setChecked(True)
        self.radioButton_4.setObjectName("radioButton_4")
        self.gridLayout_6.addWidget(self.radioButton_4, 2, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem, 2, 0, 1, 1)
        self.label_18 = QtWidgets.QLabel(self.groupBox_3)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_18.setFont(font)
        self.label_18.setObjectName("label_18")
        self.gridLayout_6.addWidget(self.label_18, 0, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        self.gridLayout_6.addItem(spacerItem1, 5, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout_6.addItem(spacerItem2, 3, 1, 1, 1)
        self.groupBox_6 = QtWidgets.QGroupBox(self.groupBox_3)
        self.groupBox_6.setEnabled(True)
        self.groupBox_6.setTitle("")
        self.groupBox_6.setObjectName("groupBox_6")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.genLhsPushButton = QtWidgets.QPushButton(self.groupBox_6)
        self.genLhsPushButton.setEnabled(False)
        self.genLhsPushButton.setObjectName("genLhsPushButton")
        self.horizontalLayout_2.addWidget(self.genLhsPushButton)
        self.lhsSettingsPushButton = QtWidgets.QPushButton(self.groupBox_6)
        self.lhsSettingsPushButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/sampling/settings_icon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.lhsSettingsPushButton.setIcon(icon)
        self.lhsSettingsPushButton.setObjectName("lhsSettingsPushButton")
        self.horizontalLayout_2.addWidget(self.lhsSettingsPushButton)
        self.sampleDataPushButton = QtWidgets.QPushButton(self.groupBox_6)
        self.sampleDataPushButton.setEnabled(False)
        self.sampleDataPushButton.setObjectName("sampleDataPushButton")
        self.horizontalLayout_2.addWidget(self.sampleDataPushButton)
        self.gridLayout_6.addWidget(self.groupBox_6, 2, 2, 1, 2)
        self.groupBox_8 = QtWidgets.QGroupBox(self.groupBox_3)
        self.groupBox_8.setEnabled(False)
        self.groupBox_8.setTitle("")
        self.groupBox_8.setObjectName("groupBox_8")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.groupBox_8)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.lineEditCsvFilePath = QtWidgets.QLineEdit(self.groupBox_8)
        self.lineEditCsvFilePath.setReadOnly(True)
        self.lineEditCsvFilePath.setObjectName("lineEditCsvFilePath")
        self.horizontalLayout_4.addWidget(self.lineEditCsvFilePath)
        self.openCsvFilePushButton = QtWidgets.QPushButton(self.groupBox_8)
        self.openCsvFilePushButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/sampling/open_icon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.openCsvFilePushButton.setIcon(icon1)
        self.openCsvFilePushButton.setObjectName("openCsvFilePushButton")
        self.horizontalLayout_4.addWidget(self.openCsvFilePushButton)
        self.csvEditorPushButton = QtWidgets.QPushButton(self.groupBox_8)
        self.csvEditorPushButton.setEnabled(False)
        self.csvEditorPushButton.setObjectName("csvEditorPushButton")
        self.horizontalLayout_4.addWidget(self.csvEditorPushButton)
        self.gridLayout_6.addWidget(self.groupBox_8, 4, 2, 1, 2)
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
        self.gridLayout.addWidget(self.groupBox_3, 0, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem3, 1, 0, 1, 1)
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

        self.retranslateUi(Form)
        self.radioButton_4.toggled['bool'].connect(self.groupBox_6.setEnabled)
        self.radioButton_3.toggled['bool'].connect(self.groupBox_8.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.radioButton_3.setText(_translate("Form", "Load data from CSV file:"))
        self.radioButton_4.setText(_translate("Form", "Generate input from LHS and sample the data:"))
        self.label_18.setText(_translate("Form", "Design of Experiments (DOE) Settings"))
        self.genLhsPushButton.setToolTip(_translate("Form", "<html><head/><body><p align=\"justify\">Generates the Latin Hypercube Sampling (LHS) when <span style=\" text-decoration: underline;\">all</span> the variables in the table above have their lower and upper bounds defined. Default number of points is 10 * number of variables. To change this, click on the settings button.</p></body></html>"))
        self.genLhsPushButton.setText(_translate("Form", "Generate LHS"))
        self.lhsSettingsPushButton.setToolTip(_translate("Form", "<html><head/><body><p>Latin Hypercube Sampling (LHS) settings</p></body></html>"))
        self.sampleDataPushButton.setToolTip(_translate("Form", "<html><head/><body><p>Query the simulation engine to sample the model. May take a while depending on model complexity and number of samples.</p></body></html>"))
        self.sampleDataPushButton.setText(_translate("Form", "Sample Data"))
        self.openCsvFilePushButton.setToolTip(_translate("Form", "<html><head/><body><p>Select .csv file to extract the data from</p></body></html>"))
        self.csvEditorPushButton.setToolTip(_translate("Form", "<html><head/><body><p>Opens the CSV editor to select which variables to use in the application.</p></body></html>"))
        self.csvEditorPushButton.setText(_translate("Form", "CSV editor"))
        item = self.tableWidgetInputVariables.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Variable"))
        item = self.tableWidgetInputVariables.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Lower bound"))
        item = self.tableWidgetInputVariables.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Upper bound"))
        self.label_17.setText(_translate("Form", "DOE Results"))

from gui.resources import icons_rc
