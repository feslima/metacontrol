# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Felipe\metacontrol\gui\views\ui_files\hessianextractiontab.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(982, 544)
        self.gridLayout_3 = QtWidgets.QGridLayout(Form)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.trainMetamodelPushButton = QtWidgets.QPushButton(self.groupBox)
        self.trainMetamodelPushButton.setObjectName("trainMetamodelPushButton")
        self.gridLayout.addWidget(self.trainMetamodelPushButton, 2, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 1, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_6 = QtWidgets.QGroupBox(Form)
        self.groupBox_6.setTitle("")
        self.groupBox_6.setObjectName("groupBox_6")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.groupBox_6)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.label_8 = QtWidgets.QLabel(self.groupBox_6)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.gridLayout_7.addWidget(self.label_8, 0, 0, 1, 1)
        self.genGradHessPushButton = QtWidgets.QPushButton(self.groupBox_6)
        self.genGradHessPushButton.setObjectName("genGradHessPushButton")
        self.gridLayout_7.addWidget(self.genGradHessPushButton, 2, 0, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_7.addItem(spacerItem2, 3, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_7.addItem(spacerItem3, 1, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_6, 0, 2, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(Form)
        self.groupBox_3.setTitle("")
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.line = QtWidgets.QFrame(self.groupBox_3)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_4.addWidget(self.line, 1, 0, 1, 2)
        self.gyTableView = QtWidgets.QTableView(self.groupBox_3)
        self.gyTableView.setObjectName("gyTableView")
        self.gridLayout_4.addWidget(self.gyTableView, 3, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox_3)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout_4.addWidget(self.label_3, 0, 0, 1, 1)
        self.gydTableView = QtWidgets.QTableView(self.groupBox_3)
        self.gydTableView.setObjectName("gydTableView")
        self.gridLayout_4.addWidget(self.gydTableView, 3, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox_3)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout_4.addWidget(self.label_5, 2, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox_3)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.gridLayout_4.addWidget(self.label_6, 2, 1, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_3, 1, 0, 1, 4)
        self.groupBox_4 = QtWidgets.QGroupBox(Form)
        self.groupBox_4.setTitle("")
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.line_2 = QtWidgets.QFrame(self.groupBox_4)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout_5.addWidget(self.line_2, 1, 0, 1, 2)
        self.judTableView = QtWidgets.QTableView(self.groupBox_4)
        self.judTableView.setObjectName("judTableView")
        self.gridLayout_5.addWidget(self.judTableView, 4, 1, 1, 1)
        self.juuTableView = QtWidgets.QTableView(self.groupBox_4)
        self.juuTableView.setObjectName("juuTableView")
        self.gridLayout_5.addWidget(self.juuTableView, 4, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox_4)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridLayout_5.addWidget(self.label_4, 0, 0, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.groupBox_4)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setAlignment(QtCore.Qt.AlignCenter)
        self.label_10.setObjectName("label_10")
        self.gridLayout_5.addWidget(self.label_10, 2, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.groupBox_4)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.gridLayout_5.addWidget(self.label_9, 2, 1, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_4, 2, 0, 1, 4)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem4, 3, 0, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem5, 3, 2, 1, 1)
        self.groupBox_5 = QtWidgets.QGroupBox(Form)
        self.groupBox_5.setTitle("")
        self.groupBox_5.setObjectName("groupBox_5")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.groupBox_5)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_7 = QtWidgets.QLabel(self.groupBox_5)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.gridLayout_6.addWidget(self.label_7, 0, 0, 1, 1)
        self.cholmodPushButton = QtWidgets.QPushButton(self.groupBox_5)
        self.cholmodPushButton.setObjectName("cholmodPushButton")
        self.gridLayout_6.addWidget(self.cholmodPushButton, 1, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_5, 3, 1, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(Form)
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.autoDiffRadioButton = QtWidgets.QRadioButton(self.groupBox_2)
        self.autoDiffRadioButton.setObjectName("autoDiffRadioButton")
        self.gridLayout_2.addWidget(self.autoDiffRadioButton, 4, 0, 1, 1)
        self.numericDiffRadioButton = QtWidgets.QRadioButton(self.groupBox_2)
        self.numericDiffRadioButton.setObjectName("numericDiffRadioButton")
        self.gridLayout_2.addWidget(self.numericDiffRadioButton, 3, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.krigingHessRadioButton = QtWidgets.QRadioButton(self.groupBox_2)
        self.krigingHessRadioButton.setChecked(True)
        self.krigingHessRadioButton.setObjectName("krigingHessRadioButton")
        self.gridLayout_2.addWidget(self.krigingHessRadioButton, 2, 0, 1, 1)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem6, 5, 0, 1, 1)
        spacerItem7 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem7, 1, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_2, 0, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Reduced space metamodel training"))
        self.trainMetamodelPushButton.setText(_translate("Form", "Open training dialog"))
        self.label_8.setText(_translate("Form", "Gradient and Hessian"))
        self.genGradHessPushButton.setText(_translate("Form", "Estimate Gradient and Hessian"))
        self.label_3.setText(_translate("Form", "Gradient results"))
        self.label_5.setText(_translate("Form", "G<sup>y</sup>"))
        self.label_6.setText(_translate("Form", "G<sup>y</sup><sub>d</sub>"))
        self.label_4.setText(_translate("Form", "Hessian results"))
        self.label_10.setText(_translate("Form", "J<sub>uu</sub>"))
        self.label_9.setText(_translate("Form", "J<sub>ud</sub>"))
        self.label_7.setText(_translate("Form", "Hessian matrix positive-definite correction"))
        self.cholmodPushButton.setText(_translate("Form", "Cholesky Modification"))
        self.autoDiffRadioButton.setText(_translate("Form", "Automatic (autograd)"))
        self.numericDiffRadioButton.setText(_translate("Form", "Numeric (numdifftools)"))
        self.label_2.setText(_translate("Form", "Differentiation method"))
        self.krigingHessRadioButton.setText(_translate("Form", "Aproximate analytical (Kriging predictions equations)"))

