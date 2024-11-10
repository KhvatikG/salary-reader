# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDateEdit, QFrame,
    QHBoxLayout, QHeaderView, QLabel, QLayout,
    QLineEdit, QListView, QListWidget, QListWidgetItem,
    QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1105, 630)
        MainWindow.setStyleSheet(u"\n"
"background-color: qlineargradient(spread:pad, x1:1, y1:1, x2:0, y2:0, stop:0 rgba(81, 0, 135, 255), stop:0.427447 rgba(41, 61, 132, 235), stop:1 rgba(155, 79, 165, 255));\n"
"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.department = QComboBox(self.centralwidget)
        self.department.addItem("")
        self.department.addItem("")
        self.department.addItem("")
        self.department.setObjectName(u"department")
        self.department.setStyleSheet(u"QComboBox { \n"
"background-color: rgba(255, 255, 255, 30);\n"
"border: 1px solid rgba(255, 255, 255, 40);\n"
"border-radius: 7px;\n"
"color: white;\n"
"font-weight: bold;\n"
"font-size: 16pt;\n"
"}\n"
"\n"
"QComboBox:item {\n"
"background-color: rgba(255, 255, 255, 70);\n"
"color: white;\n"
"}")

        self.verticalLayout_2.addWidget(self.department)

        self.main_frame = QFrame(self.centralwidget)
        self.main_frame.setObjectName(u"main_frame")
        self.main_frame.setStyleSheet(u"background-color: none;")
        self.verticalLayout = QVBoxLayout(self.main_frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.roles_settings = QWidget(self.main_frame)
        self.roles_settings.setObjectName(u"roles_settings")
        self.roles_settings.setStyleSheet(u"background-color: rgba(255, 255, 255, 0);\n"
"border: 1px solid  rgba(255, 255, 255, 70);\n"
"border-radius: 7px;\n"
"color: white;")
        self.horizontalLayout = QHBoxLayout(self.roles_settings)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.roles_frame = QFrame(self.roles_settings)
        self.roles_frame.setObjectName(u"roles_frame")
        self.roles_frame.setStyleSheet(u"background-color: rgba(255, 255, 255, 30);\n"
"border: 1px solid rgba(255, 255, 255, 40);\n"
"border-radius: 7px;")
        self.roles_layout = QVBoxLayout(self.roles_frame)
        self.roles_layout.setObjectName(u"roles_layout")
        self.roles_layout.setContentsMargins(9, 9, 9, 9)
        self.roles_label = QLabel(self.roles_frame)
        self.roles_label.setObjectName(u"roles_label")
        self.roles_label.setStyleSheet(u"color: white;\n"
"font-weight: bold;\n"
"font-size: 11pt;\n"
"background-color: none;\n"
"border: none;")

        self.roles_layout.addWidget(self.roles_label)

        self.roles_list = QListWidget(self.roles_frame)
        self.roles_list.setObjectName(u"roles_list")
        self.roles_list.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        self.roles_list.setStyleSheet(u"background-color: rgba(255, 255, 255, 0)")
        self.roles_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.roles_list.setMovement(QListView.Movement.Free)
        self.roles_list.setSortingEnabled(False)

        self.roles_layout.addWidget(self.roles_list)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.roles_add_line = QLineEdit(self.roles_frame)
        self.roles_add_line.setObjectName(u"roles_add_line")

        self.horizontalLayout_2.addWidget(self.roles_add_line)

        self.roles_add_button = QPushButton(self.roles_frame)
        self.roles_add_button.setObjectName(u"roles_add_button")
        self.roles_add_button.setStyleSheet(u"QPushButton:hover {\n"
"background-color: rgba(255, 255, 255, 40)\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"background-color: rgba(255, 255, 255, 70)\n"
"}")

        self.horizontalLayout_2.addWidget(self.roles_add_button)


        self.roles_layout.addLayout(self.horizontalLayout_2)

        self.RolesButtons = QHBoxLayout()
        self.RolesButtons.setObjectName(u"RolesButtons")
        self.roles_edit = QPushButton(self.roles_frame)
        self.roles_edit.setObjectName(u"roles_edit")
        self.roles_edit.setStyleSheet(u"QPushButton:hover {\n"
"background-color: rgba(255, 255, 255, 40)\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"background-color: rgba(255, 255, 255, 70)\n"
"}")

        self.RolesButtons.addWidget(self.roles_edit)

        self.roles_delete = QPushButton(self.roles_frame)
        self.roles_delete.setObjectName(u"roles_delete")
        self.roles_delete.setStyleSheet(u"QPushButton:hover {\n"
"background-color: rgba(255, 255, 255, 40)\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"background-color: rgba(255, 255, 255, 70)\n"
"}")

        self.RolesButtons.addWidget(self.roles_delete)


        self.roles_layout.addLayout(self.RolesButtons)


        self.horizontalLayout.addWidget(self.roles_frame)

        self.settings_frame = QFrame(self.roles_settings)
        self.settings_frame.setObjectName(u"settings_frame")
        self.settings_frame.setStyleSheet(u"background-color: rgba(255, 255, 255, 30);\n"
"border: 1px solid rgba(255, 255, 255, 40);\n"
"border-radius: 7px;")
        self.MainSettings = QVBoxLayout(self.settings_frame)
        self.MainSettings.setObjectName(u"MainSettings")
        self.MainSettings.setContentsMargins(9, 9, 9, 9)
        self.label_motivate_settings = QLabel(self.settings_frame)
        self.label_motivate_settings.setObjectName(u"label_motivate_settings")
        self.label_motivate_settings.setStyleSheet(u"color: white;\n"
"font-weight: bold;\n"
"font-size: 11pt;\n"
"background-color: none;\n"
"border: none;")

        self.MainSettings.addWidget(self.label_motivate_settings)

        self.table_motivate_settings = QTableWidget(self.settings_frame)
        self.table_motivate_settings.setObjectName(u"table_motivate_settings")
        font = QFont()
        font.setBold(True)
        font.setItalic(False)
        self.table_motivate_settings.setFont(font)
        self.table_motivate_settings.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.table_motivate_settings.setAutoFillBackground(False)
        self.table_motivate_settings.setStyleSheet(u"QTableWidget {\n"
"        gridline-color: rgba(255, 255, 255, 70);\n"
"    }\n"
"    QHeaderView::section {\n"
"        padding: 3px;  \n"
"    }")
        self.table_motivate_settings.setFrameShape(QFrame.Shape.StyledPanel)
        self.table_motivate_settings.setSortingEnabled(True)
        self.table_motivate_settings.setRowCount(0)
        self.table_motivate_settings.horizontalHeader().setCascadingSectionResizes(True)
        self.table_motivate_settings.horizontalHeader().setMinimumSectionSize(170)
        self.table_motivate_settings.horizontalHeader().setDefaultSectionSize(170)
        self.table_motivate_settings.horizontalHeader().setHighlightSections(True)
        self.table_motivate_settings.horizontalHeader().setProperty(u"showSortIndicator", True)
        self.table_motivate_settings.horizontalHeader().setStretchLastSection(True)
        self.table_motivate_settings.verticalHeader().setVisible(False)
        self.table_motivate_settings.verticalHeader().setCascadingSectionResizes(False)

        self.MainSettings.addWidget(self.table_motivate_settings)

        self.SettingsButtons = QHBoxLayout()
        self.SettingsButtons.setObjectName(u"SettingsButtons")
        self.button_add_threshhold = QPushButton(self.settings_frame)
        self.button_add_threshhold.setObjectName(u"button_add_threshhold")
        self.button_add_threshhold.setStyleSheet(u"QPushButton:hover {\n"
"background-color: rgba(255, 255, 255, 40)\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"background-color: rgba(255, 255, 255, 70)\n"
"}")

        self.SettingsButtons.addWidget(self.button_add_threshhold)

        self.button_delete_threshold = QPushButton(self.settings_frame)
        self.button_delete_threshold.setObjectName(u"button_delete_threshold")
        self.button_delete_threshold.setStyleSheet(u"QPushButton:hover {\n"
"background-color: rgba(255, 255, 255, 40)\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"background-color: rgba(255, 255, 255, 70)\n"
"}")

        self.SettingsButtons.addWidget(self.button_delete_threshold)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.SettingsButtons.addItem(self.horizontalSpacer)

        self.button_settings_save = QPushButton(self.settings_frame)
        self.button_settings_save.setObjectName(u"button_settings_save")
        self.button_settings_save.setStyleSheet(u"QPushButton:hover {\n"
"background-color: rgba(255, 255, 255, 40)\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"background-color: rgba(255, 255, 255, 70)\n"
"}")

        self.SettingsButtons.addWidget(self.button_settings_save)

        self.button_settings_cancel = QPushButton(self.settings_frame)
        self.button_settings_cancel.setObjectName(u"button_settings_cancel")
        self.button_settings_cancel.setStyleSheet(u"QPushButton:hover {\n"
"background-color: rgba(255, 255, 255, 40)\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"background-color: rgba(255, 255, 255, 70)\n"
"}")

        self.SettingsButtons.addWidget(self.button_settings_cancel)

        self.SettingsButtons.setStretch(0, 3)
        self.SettingsButtons.setStretch(1, 3)
        self.SettingsButtons.setStretch(2, 20)
        self.SettingsButtons.setStretch(3, 10)
        self.SettingsButtons.setStretch(4, 10)

        self.MainSettings.addLayout(self.SettingsButtons)


        self.horizontalLayout.addWidget(self.settings_frame)

        self.employees = QFrame(self.roles_settings)
        self.employees.setObjectName(u"employees")
        self.employees.setStyleSheet(u"background-color: rgba(255, 255, 255, 30);\n"
"border: 1px solid rgba(255, 255, 255, 40);\n"
"border-radius: 7px;")
        self.employees_layout = QVBoxLayout(self.employees)
        self.employees_layout.setObjectName(u"employees_layout")
        self.employees_label = QLabel(self.employees)
        self.employees_label.setObjectName(u"employees_label")
        self.employees_label.setStyleSheet(u"color: white;\n"
"font-weight: bold;\n"
"font-size: 11pt;\n"
"background-color: none;\n"
"border: none;")

        self.employees_layout.addWidget(self.employees_label)

        self.employees_table = QTableWidget(self.employees)
        self.employees_table.setObjectName(u"employees_table")
        self.employees_table.setStyleSheet(u"QTableWidget {\n"
"        gridline-color: rgba(255, 255, 255, 70);\n"
"    }\n"
"    QHeaderView::section {\n"
"        padding: 3px;  \n"
"    }")
        self.employees_table.setSortingEnabled(True)
        self.employees_table.horizontalHeader().setCascadingSectionResizes(False)
        self.employees_table.horizontalHeader().setMinimumSectionSize(50)
        self.employees_table.horizontalHeader().setStretchLastSection(True)
        self.employees_table.verticalHeader().setVisible(False)

        self.employees_layout.addWidget(self.employees_table)

        self.button_employees_edit = QPushButton(self.employees)
        self.button_employees_edit.setObjectName(u"button_employees_edit")
        self.button_employees_edit.setStyleSheet(u"QPushButton:hover {\n"
"background-color: rgba(255, 255, 255, 40)\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"background-color: rgba(255, 255, 255, 70)\n"
"}")

        self.employees_layout.addWidget(self.button_employees_edit)


        self.horizontalLayout.addWidget(self.employees)


        self.verticalLayout.addWidget(self.roles_settings)

        self.salary_panel = QFrame(self.main_frame)
        self.salary_panel.setObjectName(u"salary_panel")
        self.salary_panel.setStyleSheet(u"background-color:  none;")
        self.horizontalLayout_3 = QHBoxLayout(self.salary_panel)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label = QLabel(self.salary_panel)
        self.label.setObjectName(u"label")
        self.label.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label.setStyleSheet(u"color: white;\n"
"font-weight: bold;\n"
"font-size: 11pt;\n"
"background-color: none;\n"
"border: none;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_3.addWidget(self.label)

        self.date_from = QDateEdit(self.salary_panel)
        self.date_from.setObjectName(u"date_from")
        self.date_from.setStyleSheet(u"")

        self.horizontalLayout_3.addWidget(self.date_from)

        self.label_2 = QLabel(self.salary_panel)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setStyleSheet(u"color: white;\n"
"font-weight: bold;\n"
"font-size: 11pt;\n"
"background-color: none;\n"
"border: none;")
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_3.addWidget(self.label_2)

        self.date_to = QDateEdit(self.salary_panel)
        self.date_to.setObjectName(u"date_to")
        self.date_to.setStyleSheet(u"")

        self.horizontalLayout_3.addWidget(self.date_to)

        self.refresh_salary = QPushButton(self.salary_panel)
        self.refresh_salary.setObjectName(u"refresh_salary")

        self.horizontalLayout_3.addWidget(self.refresh_salary)

        self.pushButton_3 = QPushButton(self.salary_panel)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.horizontalLayout_3.addWidget(self.pushButton_3)

        self.get_full_salary_blanc = QPushButton(self.salary_panel)
        self.get_full_salary_blanc.setObjectName(u"get_full_salary_blanc")

        self.horizontalLayout_3.addWidget(self.get_full_salary_blanc)

        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 5)
        self.horizontalLayout_3.setStretch(2, 1)
        self.horizontalLayout_3.setStretch(3, 5)
        self.horizontalLayout_3.setStretch(4, 5)
        self.horizontalLayout_3.setStretch(5, 5)
        self.horizontalLayout_3.setStretch(6, 5)
        self.date_from.raise_()
        self.label_2.raise_()
        self.date_to.raise_()
        self.refresh_salary.raise_()
        self.pushButton_3.raise_()
        self.get_full_salary_blanc.raise_()
        self.label.raise_()

        self.verticalLayout.addWidget(self.salary_panel)

        self.salar_table = QTableWidget(self.main_frame)
        self.salar_table.setObjectName(u"salar_table")
        self.salar_table.setStyleSheet(u"background-color: rgba(255, 255, 255, 30);\n"
"border-radius: 7px;")

        self.verticalLayout.addWidget(self.salar_table)


        self.verticalLayout_2.addWidget(self.main_frame)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.roles_list.setCurrentRow(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"SalaryReader", None))
        self.department.setItemText(0, QCoreApplication.translate("MainWindow", u"GONZO", None))
        self.department.setItemText(1, QCoreApplication.translate("MainWindow", u"\u041a\u0443\u043b\u044c\u0442 \u0415\u0434\u044b", None))
        self.department.setItemText(2, QCoreApplication.translate("MainWindow", u"\u041a\u0420\u0423\u0413", None))

        self.roles_label.setText(QCoreApplication.translate("MainWindow", u"\u041f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u044b \u043c\u043e\u0442\u0438\u0432\u0430\u0446\u0438\u0438:", None))
        self.roles_add_button.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
        self.roles_edit.setText(QCoreApplication.translate("MainWindow", u"\u0420\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c", None))
        self.roles_delete.setText(QCoreApplication.translate("MainWindow", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c", None))
        self.label_motivate_settings.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u0432\u043e\u0437\u043d\u0430\u0433\u0440\u043e\u0436\u0434\u0435\u043d\u0438\u0439 \u0434\u043b\u044f \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u043e\u0439 \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u044b:", None))
        self.button_add_threshhold.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.button_delete_threshold.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.button_settings_save.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c", None))
        self.button_settings_cancel.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0442\u043c\u0435\u043d\u0438\u0442\u044c", None))
        self.employees_label.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0442\u0440\u0443\u0434\u043d\u0438\u043a\u0438 \u0432 \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u043e\u0439 \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u0435:", None))
        self.button_employees_edit.setText(QCoreApplication.translate("MainWindow", u"\u0420\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0442:", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e:", None))
        self.refresh_salary.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0431\u043d\u043e\u0432\u0438\u0442\u044c", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"\u041f\u0435\u0447\u0430\u0442\u044c", None))
        self.get_full_salary_blanc.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0434\u0440\u043e\u0431\u043d\u044b\u0439 \u043e\u0442\u0447\u0435\u0442", None))
    # retranslateUi

