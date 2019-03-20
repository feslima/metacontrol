# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'loadSimulationTree.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1024, 768)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 1, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.pushButtonOK = QtWidgets.QPushButton(Dialog)
        self.pushButtonOK.setMaximumSize(QtCore.QSize(60, 22))
        self.pushButtonOK.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.pushButtonOK.setObjectName("pushButtonOK")
        self.horizontalLayout_2.addWidget(self.pushButtonOK)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 2, 1, 1)
        self.tableWidgetInput = QtWidgets.QTableWidget(Dialog)
        self.tableWidgetInput.setStyleSheet("")
        self.tableWidgetInput.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidgetInput.setRowCount(0)
        self.tableWidgetInput.setObjectName("tableWidgetInput")
        self.tableWidgetInput.setColumnCount(3)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetInput.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetInput.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetInput.setHorizontalHeaderItem(2, item)
        self.tableWidgetInput.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidgetInput.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.tableWidgetInput, 0, 2, 1, 1)
        self.tableWidgetOutput = QtWidgets.QTableWidget(Dialog)
        self.tableWidgetOutput.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidgetOutput.setObjectName("tableWidgetOutput")
        self.tableWidgetOutput.setColumnCount(2)
        self.tableWidgetOutput.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetOutput.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetOutput.setHorizontalHeaderItem(1, item)
        self.tableWidgetOutput.horizontalHeader().setMinimumSectionSize(61)
        self.tableWidgetOutput.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.tableWidgetOutput, 1, 2, 1, 1)
        self.treeViewInput = QtWidgets.QTreeView(Dialog)
        self.treeViewInput.setMinimumSize(QtCore.QSize(300, 0))
        self.treeViewInput.setMaximumSize(QtCore.QSize(300, 16777215))
        self.treeViewInput.setStyleSheet("")
        self.treeViewInput.setObjectName("treeViewInput")
        self.gridLayout.addWidget(self.treeViewInput, 0, 0, 1, 1)
        self.treeViewOutput = QtWidgets.QTreeView(Dialog)
        self.treeViewOutput.setMinimumSize(QtCore.QSize(300, 0))
        self.treeViewOutput.setMaximumSize(QtCore.QSize(300, 16777215))
        self.treeViewOutput.setObjectName("treeViewOutput")
        self.gridLayout.addWidget(self.treeViewOutput, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButtonOK.setText(_translate("Dialog", "OK"))
        self.tableWidgetInput.setSortingEnabled(True)
        item = self.tableWidgetInput.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Variable Path"))
        item = self.tableWidgetInput.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "Alias"))
        item = self.tableWidgetInput.horizontalHeaderItem(2)
        item.setText(_translate("Dialog", "Type"))
        self.tableWidgetOutput.setSortingEnabled(True)
        item = self.tableWidgetOutput.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Variable Path"))
        item = self.tableWidgetOutput.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "Alias"))

