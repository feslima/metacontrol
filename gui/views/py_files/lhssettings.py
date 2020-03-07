# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Felipe\PycharmProjects\metacontrol\gui\views\ui_files\lhssettings.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(268, 128)
        Dialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.lineEditNSamples = QtWidgets.QLineEdit(Dialog)
        self.lineEditNSamples.setObjectName("lineEditNSamples")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEditNSamples)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.lineEditNIter = QtWidgets.QLineEdit(Dialog)
        self.lineEditNIter.setObjectName("lineEditNIter")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEditNIter)
        self.gridLayout.addLayout(self.formLayout, 1, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 1)
        self.checkBoxIncVertices = QtWidgets.QCheckBox(Dialog)
        self.checkBoxIncVertices.setObjectName("checkBoxIncVertices")
        self.gridLayout.addWidget(self.checkBoxIncVertices, 2, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.lineEditNSamples, self.lineEditNIter)
        Dialog.setTabOrder(self.lineEditNIter, self.checkBoxIncVertices)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "LHS Settings"))
        self.label.setText(_translate("Dialog", "Number of samples:"))
        self.label_2.setText(_translate("Dialog", "Number of iterations:"))
        self.checkBoxIncVertices.setText(_translate("Dialog", "Include hypercube vertices"))
