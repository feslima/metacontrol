# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Felipe\PycharmProjects\metacontrol\gui\views\ui_files\activeconstrainttab.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1024, 720)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setStyleSheet("QGroupBox {\n"
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
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.activeConstraintTableView = QtWidgets.QTableView(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.activeConstraintTableView.sizePolicy().hasHeightForWidth())
        self.activeConstraintTableView.setSizePolicy(sizePolicy)
        self.activeConstraintTableView.setMinimumSize(QtCore.QSize(0, 0))
        self.activeConstraintTableView.setMaximumSize(QtCore.QSize(16777215, 150))
        self.activeConstraintTableView.setObjectName("activeConstraintTableView")
        self.gridLayout_2.addWidget(self.activeConstraintTableView, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 1, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(Form)
        self.groupBox_2.setStyleSheet("QGroupBox {\n"
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
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.openSamplingPushButton = QtWidgets.QPushButton(self.groupBox_2)
        self.openSamplingPushButton.setObjectName("openSamplingPushButton")
        self.gridLayout_3.addWidget(self.openSamplingPushButton, 1, 4, 1, 1)
        self.radioButton = QtWidgets.QRadioButton(self.groupBox_2)
        self.radioButton.setChecked(True)
        self.radioButton.setObjectName("radioButton")
        self.gridLayout_3.addWidget(self.radioButton, 1, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 0, 0, 1, 1)
        self.redspaceSimFileLineEdit = QtWidgets.QLineEdit(self.groupBox_2)
        self.redspaceSimFileLineEdit.setReadOnly(True)
        self.redspaceSimFileLineEdit.setObjectName("redspaceSimFileLineEdit")
        self.gridLayout_3.addWidget(self.redspaceSimFileLineEdit, 1, 2, 1, 1)
        self.loadSimulationPushButton = QtWidgets.QPushButton(self.groupBox_2)
        self.loadSimulationPushButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/sampling/open_icon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.loadSimulationPushButton.setIcon(icon)
        self.loadSimulationPushButton.setObjectName("loadSimulationPushButton")
        self.gridLayout_3.addWidget(self.loadSimulationPushButton, 1, 3, 1, 1)
        self.radioButton_2 = QtWidgets.QRadioButton(self.groupBox_2)
        self.radioButton_2.setObjectName("radioButton_2")
        self.gridLayout_3.addWidget(self.radioButton_2, 2, 0, 1, 1)
        self.openCsvEditorPushButton = QtWidgets.QPushButton(self.groupBox_2)
        self.openCsvEditorPushButton.setEnabled(False)
        self.openCsvEditorPushButton.setObjectName("openCsvEditorPushButton")
        self.gridLayout_3.addWidget(self.openCsvEditorPushButton, 2, 2, 1, 3)
        self.gridLayout.addWidget(self.groupBox_2, 4, 1, 1, 1)
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
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_3 = QtWidgets.QLabel(self.groupBox_3)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout_4.addWidget(self.label_3, 0, 0, 1, 1)
        self.reducedDataResultTableView = QtWidgets.QTableView(self.groupBox_3)
        self.reducedDataResultTableView.setObjectName("reducedDataResultTableView")
        self.gridLayout_4.addWidget(self.reducedDataResultTableView, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_3, 6, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem, 5, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem1, 3, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem2, 7, 1, 1, 1)
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
        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_4 = QtWidgets.QLabel(self.groupBox_4)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridLayout_5.addWidget(self.label_4, 0, 0, 1, 1)
        self.disturbanceRangeTableView = QtWidgets.QTableView(self.groupBox_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.disturbanceRangeTableView.sizePolicy().hasHeightForWidth())
        self.disturbanceRangeTableView.setSizePolicy(sizePolicy)
        self.disturbanceRangeTableView.setMinimumSize(QtCore.QSize(0, 110))
        self.disturbanceRangeTableView.setMaximumSize(QtCore.QSize(16777215, 150))
        self.disturbanceRangeTableView.setObjectName("disturbanceRangeTableView")
        self.gridLayout_5.addWidget(self.disturbanceRangeTableView, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_4, 2, 1, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem3, 1, 1, 1, 1)

        self.retranslateUi(Form)
        self.radioButton.toggled['bool'].connect(self.redspaceSimFileLineEdit.setEnabled)
        self.radioButton_2.toggled['bool'].connect(self.openCsvEditorPushButton.setEnabled)
        self.radioButton.toggled['bool'].connect(self.loadSimulationPushButton.setEnabled)
        self.radioButton.toggled['bool'].connect(self.openSamplingPushButton.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Variable Activity"))
        self.openSamplingPushButton.setText(_translate("Form", "Open sampling assistant"))
        self.radioButton.setText(_translate("Form", "Simulation file"))
        self.label_2.setText(_translate("Form", "Data Source"))
        self.radioButton_2.setText(_translate("Form", "CSV file"))
        self.openCsvEditorPushButton.setText(_translate("Form", "Open CSV Editor"))
        self.label_3.setText(_translate("Form", "Reduced Space Sampled Data"))
        self.label_4.setText(_translate("Form", "Range of Disturbances"))

from gui.resources import icons_rc
