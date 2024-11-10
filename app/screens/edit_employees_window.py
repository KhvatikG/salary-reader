###################################################################################################
# Окно добавления сотрудников к программе мотивации(роли).                                        #
###################################################################################################
import json
from PySide6.QtCore import QMimeData, Qt
from PySide6.QtWidgets import QDialog, QAbstractItemView, QTableWidgetItem, QMessageBox, QTableWidget
from PySide6.QtGui import QDrag, QPixmap, QPainter

from app.db import get_session
from app.models import Employee, MotivationProgram
from app.models.control_models import assign_motivation_program
from app.ui.edit_employes_in_role_dialog import Ui_Dialog
from app.ui.styles import WARNING_DIALOG_STYLE


class EditEmployeesWindow(QDialog, Ui_Dialog):
    def __init__(self, role_id: str):
        """
        :param role_id: id роли для которой открыто окно редактирования сотрудников.
        """
        super().__init__()
        self.setupUi(self)
        print(f"В новом окне {role_id=}")
        self.current_role_id = role_id

        self._configurate_tables()  # Настройка таблиц.

        # Кнопки сохранения и отмены.
        self.button_save.clicked.connect(self.save)
        self.button_cancel.clicked.connect(self.close)

        # Настройка drag and drop#####################################################################
        self.table_all_employees.setDragEnabled(True)
        self.table_all_employees.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.table_all_employees.dragMoveEvent = self.drag_move_event
        # С помощью lambda передаем ссылку на таблицу.
        self.table_all_employees.startDrag = lambda *args: self.drag_start(*args, table=self.table_all_employees)
        self.table_all_employees.dropEvent = lambda event: self.drop_event(event, table=self.table_all_employees)
        self.table_all_employees.dragEnterEvent = lambda event: self.drag_enter_event(
            event, table=self.table_all_employees)

        self.table_role_employees.setAcceptDrops(True)
        self.table_role_employees.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.table_role_employees.dragMoveEvent = self.drag_move_event
        # С помощью lambda передаем ссылку на таблицу.
        self.table_role_employees.startDrag = lambda *args: self.drag_start(*args, table=self.table_role_employees)
        self.table_role_employees.dropEvent = lambda event: self.drop_event(event, table=self.table_role_employees)
        self.table_role_employees.dragEnterEvent = lambda event: self.drag_enter_event(
            event, table=self.table_role_employees)
        ################################################################################################

    def _configurate_tables(self):
        """
        Настройка таблиц.
        :return:
        """
        # Таблица всех сотрудников.
        self.table_all_employees.setColumnCount(5)
        self.table_all_employees.setHorizontalHeaderLabels(["ФИО", "Должность", "Отдел", "Табельный", "id"])
        #self.table_all_employees.setColumnHidden(4, True)  # Скрываем id.
        self.search_all_employees.textChanged.connect(self.search)
        self.fill_left_table()

        # Таблица сотрудников привязанных к роли
        self.table_role_employees.setColumnCount(5)
        self.table_role_employees.setHorizontalHeaderLabels(["ФИО", "Должность", "Отдел", "Табельный", "id"])
        #self.table_role_employes.setColumnHidden(4, True)  # Скрываем id.
        self.fill_right_table()

    def drag_start(self, *args, table: QTableWidget = None):
        """
        Событие при начале перетаскивания.
        :param args: Аргументы передаваемые событием
        :param table: Экземпляр таблицы передаваемый через lambda
        """
        print("Тащим сотрудника")
        print(table.objectName())

        drag = QDrag(table)
        mimeData = QMimeData()

        drag_data: dict = {"source_data_table": table.objectName(), "rows": []}
        for index in table.selectionModel().selectedRows():
            row: dict = {}

            name_item = table.item(index.row(), 0)
            position_item = table.item(index.row(), 1)
            departments_item = table.item(index.row(), 2)
            code_item = table.item(index.row(), 3)
            id_item = table.item(index.row(), 4)

            row["name"] = name_item.text()
            row["position"] = position_item.text()
            row["departments"] = departments_item.text()
            row["code"] = code_item.text()
            row["id"] = id_item.text()

            drag_data["rows"].append(row)

        mimeData.setText(json.dumps(drag_data))
        drag.setMimeData(mimeData)
        # Создаем скриншот выделенных строк для отображения рядом с курсором
        pixmap = self.create_drag_pixmap(table)
        drag.setPixmap(pixmap)
        result = drag.exec(Qt.MoveAction)
        if result == Qt.MoveAction:
            print("Перетащили")
            self.remove_rows_from_table(table)
        else:
            print("Не перетащили")

    def drag_enter_event(self, event, table: QTableWidget):
        """
        Событие при входе курсора в таблицу при перетаскивании.
        :param event: Данные события перетаскивания.
        :param table: Экземпляр таблицы передаваемый через lambda
        :return:
        """
        event_mime_data = event.mimeData()
        event_data = json.loads(event_mime_data.text())
        if event_data["source_data_table"] != table.objectName():
            event.accept()
        else:
            event.ignore()

    def drag_move_event(self, event):

        event.setDropAction(Qt.DropAction.MoveAction)
        event.accept()

    def drop_event(self, event, table: QTableWidget):

        event_mime_data: QMimeData = event.mimeData()
        event_data = json.loads(event_mime_data.text())
        print(f"Получено: {event_data}")

        # Получаем id работников уже находящихся в таблице table
        table_ids = {table.item(row, 4).text() for row in range(table.rowCount())}
        print(table_ids)
        print(type(table_ids))


        if event_data["source_data_table"] != table.objectName():
            for row_data in event_data["rows"]:
                # Получаем данные строки

                employee_name = row_data.get("name")
                employee_position = row_data.get("position")
                employee_departments = row_data.get("departments")
                employee_code = row_data.get("code")
                employee_id = row_data.get("id")

                # Если в таблице уже присутствует этот работник, то пропускаем дальнейшие действия
                if employee_id in table_ids:
                    continue

                print(employee_id)
                row = table.rowCount()
                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem(employee_name))
                table.setItem(row, 1, QTableWidgetItem(employee_position))
                table.setItem(row, 2, QTableWidgetItem(employee_departments))
                table.setItem(row, 3, QTableWidgetItem(employee_code))
                table.setItem(row, 4, QTableWidgetItem(employee_id))


            event.setDropAction(Qt.DropAction.MoveAction)
            event.accept()
        else:
            event.ignore()

    def remove_rows_from_table(self, table: QTableWidget):
        """
        Удаление выбранных строк из таблицы.
        :param table: Таблица в которой необходимо удалить выбранные строки.
        """
        selected_indexes = sorted([index.row() for index in table.selectionModel().selectedRows()], reverse=True)
        for row in selected_indexes:
            table.removeRow(row)

    def create_drag_pixmap(self, table: QTableWidget):
        selected_rows = sorted(index.row() for index in table.selectionModel().selectedRows())
        # Создаем виджет для отображения всех строк как картинку
        pixmap = QPixmap(table.viewport().size())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        for row in selected_rows:
            rect = table.visualRect(table.model().index(row, 0))
            painter.drawPixmap(rect.topLeft(), table.viewport().grab(rect))
        painter.end()
        return pixmap

    def fill_left_table(self):
        """
        Заполнение таблицы всех сотрудников.
        """
        with get_session() as session:

            all_employees = session.query(Employee).all()
            role_employees = session.query(Employee).filter(Employee.motivation_program.has(id=self.current_role_id)).all()

            # Если сотрудник не привязан к роли, то добавляем его в таблицу, со всеми сотрудниками.
            for employee in all_employees:
                if employee not in role_employees and employee.code:
                    self.table_all_employees.insertRow(self.table_all_employees.rowCount())
                    self.table_all_employees.setItem(self.table_all_employees.rowCount() - 1, 0,
                                                     QTableWidgetItem(employee.name))
                    self.table_all_employees.setItem(self.table_all_employees.rowCount() - 1, 1,
                                                     QTableWidgetItem(employee.position))
                    self.table_all_employees.setItem(self.table_all_employees.rowCount() - 1, 3,
                                                     QTableWidgetItem(str(employee.code)))
                    self.table_all_employees.setItem(self.table_all_employees.rowCount() - 1, 4,
                                                     QTableWidgetItem(str(employee.id)))
                    # Подготавливаем строку отделов.
                    departments_string = ""
                    for department in employee.departments:
                        departments_string += department.name + " "
                    # Добавляем строку отделов.
                    self.table_all_employees.setItem(self.table_all_employees.rowCount() - 1, 2,
                                                     QTableWidgetItem(departments_string))

    def fill_right_table(self):
        """
        Заполнение таблицы сотрудников привязанных к роли.
        """
        with get_session() as session:
            role_employees = session.query(Employee).filter(Employee.motivation_program.has(id=self.current_role_id)).all()
            for employee in role_employees:
                self.table_role_employees.insertRow(self.table_role_employees.rowCount())
                self.table_role_employees.setItem(self.table_role_employees.rowCount() - 1, 0,
                                                  QTableWidgetItem(employee.name))
                self.table_role_employees.setItem(self.table_role_employees.rowCount() - 1, 1,
                                                  QTableWidgetItem(employee.position))
                self.table_role_employees.setItem(self.table_role_employees.rowCount() - 1, 3,
                                                  QTableWidgetItem(str(employee.code)))
                self.table_role_employees.setItem(self.table_role_employees.rowCount() - 1, 4,
                                                  QTableWidgetItem(str(employee.id)))

                # Подготавливаем строку отделов.
                departments_string = ""
                for department in employee.departments:
                    departments_string += department.name + " "
                # Добавляем строку отделов.
                self.table_role_employees.setItem(self.table_role_employees.rowCount() - 1, 2,
                                                  QTableWidgetItem(departments_string))

    def search(self, text):
        """
        Поиск по таблице всех сотрудников.
        :param text:
        :return:
        """
        text = text.lower()
        for row in range(self.table_all_employees.rowCount()):
            hidden = True
            for column in range(self.table_all_employees.columnCount()):
                item = self.table_all_employees.item(row, column)
                if text in item.text().lower():
                    hidden = False
                    break
            self.table_all_employees.setRowHidden(row, hidden)

    def save(self):
        """
        Сохраняет изменения внесенные в таблицу связи сотрудников с ролями(Программами мотивации).
        """

        current_role_id = self.current_role_id

        with get_session() as session:
            # Получаем уже привязанных к данной роли сотрудников
            assigned_employees = session.query(Employee).filter(Employee.motivation_program_id == current_role_id)
            # Получаем список id сотрудников из таблицы
            table_employees_id = [self.table_role_employees.item(row, 4).text() for row in
                                  range(self.table_role_employees.rowCount())]
            # Проверяем не исключили ли уже существующих из таблицы
            for assigned_employee in assigned_employees:
                if assigned_employee.id not in table_employees_id:  # Если исключили, то отвязываем
                    assign_motivation_program(
                        session=session, employee_id=assigned_employee.id, motivation_program_id=None)

            current_role = session.query(MotivationProgram).filter(MotivationProgram.id == current_role_id).first()
            current_role_name = current_role.name

            for row in range(self.table_role_employees.rowCount()):
                employee_id = self.table_role_employees.item(row, 4).text()
                employee = session.query(Employee).filter(Employee.id == employee_id).first()
                if not employee.motivation_program:  # Если нет связи с ролями, то добавляем.
                    assign_motivation_program(
                        session=session, employee_id=employee_id, motivation_program_id=current_role_id)
                else:  # Если сотрудник уже связан с другой ролью, то спрашиваем заменить или оставить его как есть.
                    if employee.motivation_program.id != int(current_role_id):
                        employee_name = employee.name
                        employee_role_name = employee.motivation_program.name
                        # Выбрасываем окно с предупреждением
                        msg_box = QMessageBox(
                            QMessageBox.Icon.Warning,
                            "Предупреждение",
                            f"Сотруднику {employee_name} уже назначена программа {employee_role_name}\nЗаменить ее?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                            self
                        )

                        button_yes = msg_box.button(QMessageBox.StandardButton.Yes)
                        button_no = msg_box.button(QMessageBox.StandardButton.No)
                        button_yes.setText(f"Заменить на {current_role_name}")
                        button_no.setText(f"Оставить {employee_role_name}")

                        msg_box.setStyleSheet(WARNING_DIALOG_STYLE)
                        reply = msg_box.exec()

                        if reply == QMessageBox.StandardButton.Yes:
                            assign_motivation_program(
                                session=session, employee_id=employee_id, motivation_program_id=current_role_id)
                        else:
                            continue

            self.close()
