from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem

from ..models.models import Employee


def fill_employees_table(table_widget, employees_list: list[Employee]):
    """
    Заполняет таблицу сотрудников
    :param table_widget: Таблица которую необходимо заполнить.
    :param employees_list: Список сотрудников.
    """
    table_widget.setRowCount(len(employees_list))
    table_widget.setColumnCount(3)  # ID, Name, Departments

    # Задаем заголовки столбцов
    table_widget.setHorizontalHeaderLabels(['ID', 'Name', 'Departments'])

    for row, employee in enumerate(employees_list):
        table_widget.setItem(row, 0, QTableWidgetItem(str(employee.id)))
        table_widget.setItem(row, 1, QTableWidgetItem(employee.name))
        # Объединяем департаменты в строку, если нужно
        departments_str = ', '.join(employee.departments)
        table_widget.setItem(row, 2, QTableWidgetItem(departments_str))

        # Выравнивание текста по центру
        for col in range(3):
            table_widget.item(row, col).setTextAlignment(Qt.AlignCenter)
