# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'blackjack.ui'
##
## Created by: Qt User Interface Compiler version 6.12.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QPushButton,
    QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(511, 422)
        self.btn_pedir = QPushButton(Dialog)
        self.btn_pedir.setObjectName(u"btn_pedir")
        self.btn_pedir.setGeometry(QRect(350, 360, 100, 32))
        self.btn_plantar = QPushButton(Dialog)
        self.btn_plantar.setObjectName(u"btn_plantar")
        self.btn_plantar.setGeometry(QRect(50, 360, 100, 32))
        self.lbl_carta = QLabel(Dialog)
        self.lbl_carta.setObjectName(u"lbl_carta")
        self.lbl_carta.setGeometry(QRect(190, 210, 101, 131))
        self.lbl_carta.setScaledContents(False)
        self.lbl_carta_dealer = QLabel(Dialog)
        self.lbl_carta_dealer.setObjectName(u"lbl_carta_dealer")
        self.lbl_carta_dealer.setGeometry(QRect(190, 20, 111, 121))
        self.lbl_puntaje_jugador = QLabel(Dialog)
        self.lbl_puntaje_jugador.setObjectName(u"lbl_puntaje_jugador")
        self.lbl_puntaje_jugador.setGeometry(QRect(190, 360, 131, 16))
        self.lbl_puntaje_dealer = QLabel(Dialog)
        self.lbl_puntaje_dealer.setObjectName(u"lbl_puntaje_dealer")
        self.lbl_puntaje_dealer.setGeometry(QRect(190, 150, 111, 20))
        self.lbl_tiempo = QLabel(Dialog)
        self.lbl_tiempo.setObjectName(u"lbl_tiempo")
        self.lbl_tiempo.setGeometry(QRect(370, 20, 121, 20))
        self.lbl_mazo = QLabel(Dialog)
        self.lbl_mazo.setObjectName(u"lbl_mazo")
        self.lbl_mazo.setGeometry(QRect(20, 50, 58, 16))

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.btn_pedir.setText(QCoreApplication.translate("Dialog", u"Pedir carta", None))
        self.btn_plantar.setText(QCoreApplication.translate("Dialog", u"Plantarse", None))
        self.lbl_carta.setText("")
        self.lbl_carta_dealer.setText("")
        self.lbl_puntaje_jugador.setText(QCoreApplication.translate("Dialog", u"jugador", None))
        self.lbl_puntaje_dealer.setText(QCoreApplication.translate("Dialog", u"dealer", None))
        self.lbl_tiempo.setText(QCoreApplication.translate("Dialog", u"TIEMPO", None))
        self.lbl_mazo.setText("")
    # retranslateUi

