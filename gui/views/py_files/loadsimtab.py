# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Felipe\PycharmProjects\metacontrol\gui\views\ui_files\loadsimtab.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1043, 814)
        self.gridLayout_2 = QtWidgets.QGridLayout(Form)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox = QtWidgets.QGroupBox(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QtCore.QSize(475, 500))
        self.groupBox.setMaximumSize(QtCore.QSize(800, 16777215))
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
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem, 3, 1, 1, 1)
        self.buttonLoadVariables = QtWidgets.QPushButton(self.groupBox)
        self.buttonLoadVariables.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonLoadVariables.sizePolicy().hasHeightForWidth())
        self.buttonLoadVariables.setSizePolicy(sizePolicy)
        self.buttonLoadVariables.setMinimumSize(QtCore.QSize(120, 30))
        self.buttonLoadVariables.setObjectName("buttonLoadVariables")
        self.gridLayout.addWidget(self.buttonLoadVariables, 2, 2, 1, 1)
        self.buttonOpenSimFile = QtWidgets.QPushButton(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonOpenSimFile.sizePolicy().hasHeightForWidth())
        self.buttonOpenSimFile.setSizePolicy(sizePolicy)
        self.buttonOpenSimFile.setMinimumSize(QtCore.QSize(120, 30))
        self.buttonOpenSimFile.setMaximumSize(QtCore.QSize(120, 30))
        self.buttonOpenSimFile.setStatusTip("")
        self.buttonOpenSimFile.setWhatsThis("")
        self.buttonOpenSimFile.setObjectName("buttonOpenSimFile")
        self.gridLayout.addWidget(self.buttonOpenSimFile, 1, 2, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem1, 6, 1, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.gridLayout.addWidget(self.label_13, 0, 1, 1, 1)
        self.textBrowserSimFile = QtWidgets.QTextBrowser(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textBrowserSimFile.sizePolicy().hasHeightForWidth())
        self.textBrowserSimFile.setSizePolicy(sizePolicy)
        self.textBrowserSimFile.setMinimumSize(QtCore.QSize(300, 75))
        self.textBrowserSimFile.setStyleSheet("")
        self.textBrowserSimFile.setObjectName("textBrowserSimFile")
        self.gridLayout.addWidget(self.textBrowserSimFile, 1, 1, 2, 1)
        self.label_11 = QtWidgets.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.gridLayout.addWidget(self.label_11, 4, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 1, 3, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 1, 0, 1, 1)
        self.tableViewAliasDisplay = QtWidgets.QTableView(self.groupBox)
        self.tableViewAliasDisplay.setObjectName("tableViewAliasDisplay")
        self.tableViewAliasDisplay.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.tableViewAliasDisplay, 5, 1, 1, 2)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(Form)
        self.groupBox_2.setMinimumSize(QtCore.QSize(475, 500))
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
        spacerItem4 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem4, 1, 0, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem5, 1, 2, 1, 1)
        spacerItem6 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout_3.addItem(spacerItem6, 2, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.gridLayout_3.addWidget(self.label_10, 3, 1, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_14.setFont(font)
        self.label_14.setObjectName("label_14")
        self.gridLayout_3.addWidget(self.label_14, 0, 1, 1, 1)
        spacerItem7 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout_3.addItem(spacerItem7, 5, 1, 1, 1)
        self.tableViewSimulationInfo = QtWidgets.QTableView(self.groupBox_2)
        self.tableViewSimulationInfo.setObjectName("tableViewSimulationInfo")
        self.tableViewSimulationInfo.horizontalHeader().setStretchLastSection(True)
        self.gridLayout_3.addWidget(self.tableViewSimulationInfo, 1, 1, 1, 1)
        self.tableViewSimulationData = QtWidgets.QTableView(self.groupBox_2)
        self.tableViewSimulationData.setObjectName("tableViewSimulationData")
        self.tableViewSimulationData.horizontalHeader().setStretchLastSection(True)
        self.gridLayout_3.addWidget(self.tableViewSimulationData, 4, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_2, 0, 1, 1, 1)
        self.groupBox_6 = QtWidgets.QGroupBox(Form)
        self.groupBox_6.setStyleSheet("QGroupBox {\n"
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
        self.groupBox_6.setTitle("")
        self.groupBox_6.setObjectName("groupBox_6")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.groupBox_6)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem8)
        self.buttonAddExpr = QtWidgets.QPushButton(self.groupBox_6)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/loadsim/add_icon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonAddExpr.setIcon(icon)
        self.buttonAddExpr.setObjectName("buttonAddExpr")
        self.horizontalLayout_2.addWidget(self.buttonAddExpr)
        self.gridLayout_7.addLayout(self.horizontalLayout_2, 0, 1, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.groupBox_6)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.gridLayout_7.addWidget(self.label_12, 0, 0, 1, 1)
        self.tableViewExpressions = QtWidgets.QTableView(self.groupBox_6)
        self.tableViewExpressions.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.tableViewExpressions.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableViewExpressions.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableViewExpressions.setObjectName("tableViewExpressions")
        self.tableViewExpressions.horizontalHeader().setStretchLastSection(True)
        self.gridLayout_7.addWidget(self.tableViewExpressions, 1, 0, 1, 2)
        self.gridLayout_2.addWidget(self.groupBox_6, 1, 0, 1, 2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.buttonLoadVariables.setToolTip(_translate("Form", "Opens a window that allows variable selection from the simulation file."))
        self.buttonLoadVariables.setText(_translate("Form", "Load Variables"))
        self.buttonOpenSimFile.setToolTip(_translate("Form", "Opens a file prompt to select an Aspen .bkp simulation file."))
        self.buttonOpenSimFile.setText(_translate("Form", "Open File"))
        self.label_13.setText(_translate("Form", "Load Simulation File"))
        self.textBrowserSimFile.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Select a simulation file.</span></p></body></html>"))
        self.label_11.setText(_translate("Form", "Selected variables aliases"))
        self.label_10.setText(_translate("Form", "Simulation Description"))
        self.label_14.setText(_translate("Form", "Simulation Info"))
        self.buttonAddExpr.setToolTip(_translate("Form", "<html><head/><body><p>Inserts a new expression slot</p></body></html>"))
        self.buttonAddExpr.setText(_translate("Form", "Add Expression"))
        self.label_12.setText(_translate("Form", "Function definitions"))

from gui.resources import icons_rc
