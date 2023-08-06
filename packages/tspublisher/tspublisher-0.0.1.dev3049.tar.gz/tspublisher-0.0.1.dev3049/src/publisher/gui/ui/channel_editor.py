# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'channel_editor.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from builtins import object
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from publisher.gui.widgets import TSTitle
from publisher.gui.widgets import CustomGraphicsView


class Ui_channel_editor(object):
    def setupUi(self, channel_editor):
        if not channel_editor.objectName():
            channel_editor.setObjectName(u"channel_editor")
        channel_editor.resize(536, 425)
        self.add_row = QAction(channel_editor)
        self.add_row.setObjectName(u"add_row")
        self.delete_row = QAction(channel_editor)
        self.delete_row.setObjectName(u"delete_row")
        self.verticalLayout_2 = QVBoxLayout(channel_editor)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.header = QFrame(channel_editor)
        self.header.setObjectName(u"header")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)
        self.header.setFrameShape(QFrame.StyledPanel)
        self.header.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.header)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = TSTitle(self.header)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(20)
        self.label.setFont(font)

        self.verticalLayout.addWidget(self.label)

        self.line = QFrame(self.header)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout.addWidget(self.line)


        self.verticalLayout_2.addWidget(self.header)

        self.channel_tbl = QTableView(channel_editor)
        self.channel_tbl.setObjectName(u"channel_tbl")
        self.channel_tbl.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.channel_tbl.setAlternatingRowColors(True)
        self.channel_tbl.setSortingEnabled(True)
        self.channel_tbl.horizontalHeader().setStretchLastSection(False)
        self.channel_tbl.verticalHeader().setVisible(False)

        self.verticalLayout_2.addWidget(self.channel_tbl)

        self.display_images = QCheckBox(channel_editor)
        self.display_images.setObjectName(u"display_images")

        self.verticalLayout_2.addWidget(self.display_images)

        self.badge_banner_widget = QWidget(channel_editor)
        self.badge_banner_widget.setObjectName(u"badge_banner_widget")
        self.gridLayout = QGridLayout(self.badge_banner_widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.badge = CustomGraphicsView(self.badge_banner_widget)
        self.badge.setObjectName(u"badge")

        self.gridLayout.addWidget(self.badge, 1, 0, 1, 1)

        self.banner = CustomGraphicsView(self.badge_banner_widget)
        self.banner.setObjectName(u"banner")

        self.gridLayout.addWidget(self.banner, 1, 1, 1, 1)

        self.label_3 = QLabel(self.badge_banner_widget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)

        self.label_4 = QLabel(self.badge_banner_widget)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 0, 1, 1, 1)


        self.verticalLayout_2.addWidget(self.badge_banner_widget)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.label_2 = QLabel(channel_editor)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_2)

        self.msg = QPlainTextEdit(channel_editor)
        self.msg.setObjectName(u"msg")
        sizePolicy.setHeightForWidth(self.msg.sizePolicy().hasHeightForWidth())
        self.msg.setSizePolicy(sizePolicy)
        self.msg.setMaximumSize(QSize(16777215, 50))

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.msg)


        self.verticalLayout_2.addLayout(self.formLayout)

        self.submit_btn = QPushButton(channel_editor)
        self.submit_btn.setObjectName(u"submit_btn")

        self.verticalLayout_2.addWidget(self.submit_btn)

        QWidget.setTabOrder(self.channel_tbl, self.msg)
        QWidget.setTabOrder(self.msg, self.submit_btn)

        self.retranslateUi(channel_editor)

        QMetaObject.connectSlotsByName(channel_editor)
    # setupUi

    def retranslateUi(self, channel_editor):
        channel_editor.setWindowTitle(QCoreApplication.translate("channel_editor", u"Channel Editor", None))
        self.add_row.setText(QCoreApplication.translate("channel_editor", u"Add Row", None))
        self.delete_row.setText(QCoreApplication.translate("channel_editor", u"Delete Row", None))
        self.label.setText(QCoreApplication.translate("channel_editor", u"Channel Editor", None))
        self.display_images.setText(QCoreApplication.translate("channel_editor", u"Display Images", None))
        self.label_3.setText(QCoreApplication.translate("channel_editor", u"Badge", None))
        self.label_4.setText(QCoreApplication.translate("channel_editor", u"Banner", None))
        self.label_2.setText(QCoreApplication.translate("channel_editor", u"Comment", None))
        self.submit_btn.setText(QCoreApplication.translate("channel_editor", u"Save Changes", None))
    # retranslateUi

