# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'modeltest.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(808, 351)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.tableView = QtWidgets.QTableView(Form)
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.tableView.setObjectName("tableView")
        self.gridLayout.addWidget(self.tableView, 0, 0, 3, 1)
        self.addRowPushButton = QtWidgets.QPushButton(Form)
        self.addRowPushButton.setObjectName("addRowPushButton")
        self.gridLayout.addWidget(self.addRowPushButton, 0, 1, 1, 1)
        self.removeRowPushButton = QtWidgets.QPushButton(Form)
        self.removeRowPushButton.setObjectName("removeRowPushButton")
        self.gridLayout.addWidget(self.removeRowPushButton, 1, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.addRowPushButton.setText(_translate("Form", "addRow"))
        self.removeRowPushButton.setText(_translate("Form", "delRow"))

