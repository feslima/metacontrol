# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Felipe\PycharmProjects\metacontrol\gui\views\ui_files\soctab.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
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
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label = QtWidgets.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.disturbanceMagTableView = QtWidgets.QTableView(self.groupBox)
        self.disturbanceMagTableView.setObjectName("disturbanceMagTableView")
        self.gridLayout_3.addWidget(self.disturbanceMagTableView, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)
        self.groupBox_2 = QtWidgets.QGroupBox(Form)
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.measurementErrTableView = QtWidgets.QTableView(self.groupBox_2)
        self.measurementErrTableView.setObjectName("measurementErrTableView")
        self.gridLayout_2.addWidget(self.measurementErrTableView, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_2, 0, 2, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(Form)
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
        self.subsetSizingTableView = QtWidgets.QTableView(self.groupBox_3)
        self.subsetSizingTableView.setObjectName("subsetSizingTableView")
        self.gridLayout_4.addWidget(self.subsetSizingTableView, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_3, 2, 0, 1, 3)
        self.generateResultsPushButton = QtWidgets.QPushButton(Form)
        self.generateResultsPushButton.setObjectName("generateResultsPushButton")
        self.gridLayout.addWidget(self.generateResultsPushButton, 3, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Disturbances magnitude"))
        self.label_2.setText(_translate("Form", "Measurements error"))
        self.label_3.setText(_translate("Form", "Subsets sizing options"))
        self.generateResultsPushButton.setText(_translate("Form", "Generate results"))
