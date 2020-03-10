# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Felipe\metacontrol\gui\views\ui_files\loadsimulationtree.ui'
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
        self.pushButtonLoadTreeFromFile = QtWidgets.QPushButton(Dialog)
        self.pushButtonLoadTreeFromFile.setObjectName("pushButtonLoadTreeFromFile")
        self.gridLayout.addWidget(self.pushButtonLoadTreeFromFile, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 1, 1, 1)
        self.treeViewInput = QtWidgets.QTreeView(Dialog)
        self.treeViewInput.setMinimumSize(QtCore.QSize(300, 0))
        self.treeViewInput.setMaximumSize(QtCore.QSize(300, 16777215))
        self.treeViewInput.setStyleSheet("")
        self.treeViewInput.setHeaderHidden(False)
        self.treeViewInput.setObjectName("treeViewInput")
        self.gridLayout.addWidget(self.treeViewInput, 1, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 2, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.pushButtonOK = QtWidgets.QPushButton(Dialog)
        self.pushButtonOK.setMaximumSize(QtCore.QSize(60, 22))
        self.pushButtonOK.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.pushButtonOK.setObjectName("pushButtonOK")
        self.horizontalLayout_2.addWidget(self.pushButtonOK)
        self.gridLayout.addLayout(self.horizontalLayout_2, 3, 2, 1, 3)
        self.treeViewOutput = QtWidgets.QTreeView(Dialog)
        self.treeViewOutput.setMinimumSize(QtCore.QSize(300, 0))
        self.treeViewOutput.setMaximumSize(QtCore.QSize(300, 16777215))
        self.treeViewOutput.setObjectName("treeViewOutput")
        self.gridLayout.addWidget(self.treeViewOutput, 2, 0, 1, 1)
        self.tableViewInput = QtWidgets.QTableView(Dialog)
        self.tableViewInput.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.tableViewInput.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableViewInput.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.tableViewInput.setObjectName("tableViewInput")
        self.tableViewInput.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.tableViewInput, 1, 2, 1, 3)
        self.tableViewOutput = QtWidgets.QTableView(Dialog)
        self.tableViewOutput.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.tableViewOutput.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableViewOutput.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.tableViewOutput.setObjectName("tableViewOutput")
        self.tableViewOutput.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.tableViewOutput, 2, 2, 1, 3)
        self.savePushButton = QtWidgets.QPushButton(Dialog)
        self.savePushButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/sampling/save_icon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.savePushButton.setIcon(icon)
        self.savePushButton.setObjectName("savePushButton")
        self.gridLayout.addWidget(self.savePushButton, 0, 3, 1, 1)
        self.openSimGUICheckBox = QtWidgets.QCheckBox(Dialog)
        self.openSimGUICheckBox.setObjectName("openSimGUICheckBox")
        self.gridLayout.addWidget(self.openSimGUICheckBox, 0, 4, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Load Simulation"))
        self.pushButtonLoadTreeFromFile.setToolTip(_translate("Dialog", "Opens the connection with the simulation file and loads the variable tree."))
        self.pushButtonLoadTreeFromFile.setText(_translate("Dialog", "Load Variable Tree"))
        self.pushButtonOK.setText(_translate("Dialog", "OK"))
        self.openSimGUICheckBox.setText(_translate("Dialog", "Open Simulator GUI"))

from gui.resources import icons_rc
