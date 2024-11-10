# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'edit_employes_in_role_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDialog, QFrame,
    QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(983, 594)
        Dialog.setStyleSheet(u"background-color: qlineargradient(spread:pad, x1:1, y1:1, x2:0, y2:0, stop:0 rgba(81, 0, 135, 255), stop:0.427447 rgba(41, 61, 132, 235), stop:1 rgba(155, 79, 165, 255));\n"
"")
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.frame_edit_employes_in_role = QFrame(Dialog)
        self.frame_edit_employes_in_role.setObjectName(u"frame_edit_employes_in_role")
        self.frame_edit_employes_in_role.setStyleSheet(u"background-color: rgba(255, 255, 255, 30);\n"
"border: 1px solid rgba(255, 255, 255, 40);\n"
"border-radius: 7px;\n"
"color: white;")
        self.horizontalLayout = QHBoxLayout(self.frame_edit_employes_in_role)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.layout_all_employees = QVBoxLayout()
        self.layout_all_employees.setObjectName(u"layout_all_employees")
        self.label_all_employeees = QLabel(self.frame_edit_employes_in_role)
        self.label_all_employeees.setObjectName(u"label_all_employeees")
        self.label_all_employeees.setStyleSheet(u"color: white;\n"
"font-weight: bold;\n"
"font-size: 11pt;\n"
"background-color: none;\n"
"border: none;")

        self.layout_all_employees.addWidget(self.label_all_employeees)

        self.search_all_employees = QLineEdit(self.frame_edit_employes_in_role)
        self.search_all_employees.setObjectName(u"search_all_employees")

        self.layout_all_employees.addWidget(self.search_all_employees)

        self.table_all_employees = QTableWidget(self.frame_edit_employes_in_role)
        self.table_all_employees.setObjectName(u"table_all_employees")
        self.table_all_employees.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_all_employees.setDragEnabled(True)
        self.table_all_employees.setDragDropOverwriteMode(False)
        self.table_all_employees.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.table_all_employees.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.table_all_employees.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_all_employees.setSortingEnabled(True)
        self.table_all_employees.verticalHeader().setVisible(False)

        self.layout_all_employees.addWidget(self.table_all_employees)


        self.horizontalLayout.addLayout(self.layout_all_employees)

        self.add_delete_employees_buttons = QVBoxLayout()
        self.add_delete_employees_buttons.setObjectName(u"add_delete_employees_buttons")
        self.button_add_to_role = QPushButton(self.frame_edit_employes_in_role)
        self.button_add_to_role.setObjectName(u"button_add_to_role")
        self.button_add_to_role.setMaximumSize(QSize(80, 16777215))
        self.button_add_to_role.setStyleSheet(u"QPushButton:hover {\n"
"background-color: rgba(255, 255, 255, 40)\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"background-color: rgba(255, 255, 255, 70)\n"
"}")
        self.button_add_to_role.setFlat(False)

        self.add_delete_employees_buttons.addWidget(self.button_add_to_role)

        self.button_delete_from_role = QPushButton(self.frame_edit_employes_in_role)
        self.button_delete_from_role.setObjectName(u"button_delete_from_role")
        self.button_delete_from_role.setMaximumSize(QSize(80, 16777215))
        self.button_delete_from_role.setStyleSheet(u"QPushButton:hover {\n"
"background-color: rgba(255, 255, 255, 40)\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"background-color: rgba(255, 255, 255, 70)\n"
"}")

        self.add_delete_employees_buttons.addWidget(self.button_delete_from_role)


        self.horizontalLayout.addLayout(self.add_delete_employees_buttons)

        self.layout_role_employes = QVBoxLayout()
        self.layout_role_employes.setObjectName(u"layout_role_employes")
        self.label_employes_in_role = QLabel(self.frame_edit_employes_in_role)
        self.label_employes_in_role.setObjectName(u"label_employes_in_role")
        self.label_employes_in_role.setStyleSheet(u"color: white;\n"
"font-weight: bold;\n"
"font-size: 11pt;\n"
"background-color: none;\n"
"border: none;")

        self.layout_role_employes.addWidget(self.label_employes_in_role)

        self.table_role_employees = QTableWidget(self.frame_edit_employes_in_role)
        self.table_role_employees.setObjectName(u"table_role_employes")
        self.table_role_employees.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_role_employees.setDragEnabled(True)
        self.table_role_employees.setDragDropOverwriteMode(False)
        self.table_role_employees.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.table_role_employees.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.table_role_employees.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_role_employees.verticalHeader().setVisible(False)

        self.layout_role_employes.addWidget(self.table_role_employees)


        self.horizontalLayout.addLayout(self.layout_role_employes)

        self.horizontalLayout.setStretch(1, 1)

        self.gridLayout.addWidget(self.frame_edit_employes_in_role, 0, 0, 1, 4)

        self.button_save = QPushButton(Dialog)
        self.button_save.setObjectName(u"button_save")
        self.button_save.setMaximumSize(QSize(100, 16777215))
        self.button_save.setStyleSheet(u"QPushButton {\n"
"background-color: rgba(255, 255, 255, 80);\n"
"border: 1 solid rgba(255, 255, 255, 80);\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"background-color: rgba(255, 255, 255, 40)\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"background-color: rgba(255, 255, 255, 70)\n"
"}")

        self.gridLayout.addWidget(self.button_save, 1, 3, 1, 1)

        self.button_cancel = QPushButton(Dialog)
        self.button_cancel.setObjectName(u"button_cancel")
        self.button_cancel.setMaximumSize(QSize(100, 16777215))
        self.button_cancel.setStyleSheet(u"QPushButton {\n"
"background-color: rgba(255, 255, 255, 80);\n"
"border: 1 solid rgba(255, 255, 255, 80);\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"background-color: rgba(255, 255, 255, 40)\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"background-color: rgba(255, 255, 255, 70)\n"
"}")
        self.button_cancel.setFlat(False)

        self.gridLayout.addWidget(self.button_cancel, 1, 2, 1, 1)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label_all_employeees.setText(QCoreApplication.translate("Dialog", u"\u0412\u0441\u0435 \u0440\u0430\u0431\u043e\u0442\u043d\u0438\u043a\u0438:", None))
        self.search_all_employees.setPlaceholderText(QCoreApplication.translate("Dialog", u"\u041f\u043e\u0438\u0441\u043a", None))
        self.button_add_to_role.setText(QCoreApplication.translate("Dialog", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c->", None))
        self.button_delete_from_role.setText(QCoreApplication.translate("Dialog", u"<-\u0423\u0434\u0430\u043b\u0438\u0442\u044c", None))
        self.label_employes_in_role.setText(QCoreApplication.translate("Dialog", u"\u0420\u0430\u0431\u043e\u0442\u043d\u0438\u043a\u0438 \u0432 \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u043e\u0439 \u0440\u043e\u043b\u0438:", None))
        self.button_save.setText(QCoreApplication.translate("Dialog", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c", None))
        self.button_cancel.setText(QCoreApplication.translate("Dialog", u"\u041e\u0442\u043c\u0435\u043d\u0438\u0442\u044c", None))
    # retranslateUi

