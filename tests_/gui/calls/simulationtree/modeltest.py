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
        self.tableView = QtWidgets.QTableView(Form)
        self.tableView.setGeometry(QtCore.QRect(110, 60, 256, 192))
        self.tableView.setObjectName("tableView")
        self.addRowPushButton = QtWidgets.QPushButton(Form)
        self.addRowPushButton.setGeometry(QtCore.QRect(490, 80, 75, 23))
        self.addRowPushButton.setObjectName("addRowPushButton")
        self.removeRowPushButton = QtWidgets.QPushButton(Form)
        self.removeRowPushButton.setGeometry(QtCore.QRect(490, 120, 75, 23))
        self.removeRowPushButton.setObjectName("removeRowPushButton")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.addRowPushButton.setText(_translate("Form", "addRow"))
        self.removeRowPushButton.setText(_translate("Form", "delRow"))

