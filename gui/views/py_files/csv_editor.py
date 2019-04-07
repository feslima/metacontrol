# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_files\csv_editor.ui'
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
        self.csvTableWidget = QtWidgets.QTableWidget(Dialog)
        self.csvTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.csvTableWidget.setObjectName("csvTableWidget")
        self.csvTableWidget.setColumnCount(0)
        self.csvTableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.csvTableWidget, 0, 0, 1, 2)
        self.okPushButton = QtWidgets.QPushButton(Dialog)
        self.okPushButton.setObjectName("okPushButton")
        self.gridLayout.addWidget(self.okPushButton, 1, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.okPushButton.setText(_translate("Dialog", "OK"))

