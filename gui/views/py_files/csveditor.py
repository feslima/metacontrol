# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Felipe\PycharmProjects\metacontrol\gui\views\ui_files\csveditor.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(1024, 768)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.openCsvFilePushButton = QtWidgets.QPushButton(Dialog)
        self.openCsvFilePushButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/sampling/open_icon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.openCsvFilePushButton.setIcon(icon)
        self.openCsvFilePushButton.setObjectName("openCsvFilePushButton")
        self.gridLayout.addWidget(self.openCsvFilePushButton, 0, 1, 1, 1)
        self.lineEditCsvFilePath = QtWidgets.QLineEdit(Dialog)
        self.lineEditCsvFilePath.setReadOnly(True)
        self.lineEditCsvFilePath.setObjectName("lineEditCsvFilePath")
        self.gridLayout.addWidget(self.lineEditCsvFilePath, 0, 0, 1, 1)
        self.loadFilePushButton = QtWidgets.QPushButton(Dialog)
        self.loadFilePushButton.setObjectName("loadFilePushButton")
        self.gridLayout.addWidget(self.loadFilePushButton, 0, 2, 1, 1)
        self.csvTableWidget = QtWidgets.QTableWidget(Dialog)
        self.csvTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.csvTableWidget.setObjectName("csvTableWidget")
        self.csvTableWidget.setColumnCount(0)
        self.csvTableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.csvTableWidget, 1, 0, 1, 3)
        self.okPushButton = QtWidgets.QPushButton(Dialog)
        self.okPushButton.setObjectName("okPushButton")
        self.gridLayout.addWidget(self.okPushButton, 2, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.loadFilePushButton.setText(_translate("Dialog", "Load file"))
        self.okPushButton.setText(_translate("Dialog", "OK"))

from gui.resources import icons_rc
