# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ts_title.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from __future__ import absolute_import
from builtins import object
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from . import icons_rc

class Ui_ts_title(object):
    def setupUi(self, ts_title):
        if not ts_title.objectName():
            ts_title.setObjectName(u"ts_title")
        ts_title.resize(543, 51)
        self.horizontalLayout = QHBoxLayout(ts_title)
        self.horizontalLayout.setSpacing(12)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(5, -1, -1, -1)
        self.icon = QLabel(ts_title)
        self.icon.setObjectName(u"icon")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.icon.sizePolicy().hasHeightForWidth())
        self.icon.setSizePolicy(sizePolicy)
        self.icon.setMinimumSize(QSize(32, 32))
        self.icon.setPixmap(QPixmap(u":/icons/icons/TSIcon.png"))

        self.horizontalLayout.addWidget(self.icon)

        self.label = QLabel(ts_title)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(20)
        self.label.setFont(font)

        self.horizontalLayout.addWidget(self.label)


        self.retranslateUi(ts_title)

        QMetaObject.connectSlotsByName(ts_title)
    # setupUi

    def retranslateUi(self, ts_title):
        ts_title.setWindowTitle(QCoreApplication.translate("ts_title", u"Form", None))
        self.icon.setText("")
        self.label.setText(QCoreApplication.translate("ts_title", u"Title", None))
    # retranslateUi

