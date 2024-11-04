from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QTableWidgetItem, QComboBox

from ..models.models import Employee, Department


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


def get_icon_from_svg(path: str) -> QIcon:
    """
    Возвращает иконку из svg файла.
    С прозрачным фоном.
    :param path: Путь к файлу.
    :return: Иконка.
    """
    renderer = QSvgRenderer(path)
    pixmap = QPixmap(renderer.viewBox().size())
    pixmap.fill(Qt.GlobalColor.transparent)  # Заполняем фон прозрачным цветом
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


def set_departments(departments_combobox: QComboBox, departments_list: list[Department]):
    """
    Заполняет комбо-бокс отделами.
    Добавляет каждому отделу скрытое поле с кодом (Department.code в модели db).
    :param departments_combobox: Комбобокс.
    :param departments_list: Список отделов.
    """
    departments_combobox.clear()
    for department in departments_list:
        text = department.name
        data = {"department_code": department.code}
        departments_combobox.addItem(text, data)


def get_department_code(department) -> int | None:
    """
    Возвращает код отдела, хранящийся в скрытом поле.
    :param department: Ui элемент отдела
    :return: Код переданного ui объекта отдела.
    """
    # Получаем данные хранящиеся в поле UserRole
    data: dict = department.currentData(Qt.ItemDataRole.UserRole)
    if data:
        code = data.get("department_code")
        if not code:
            print("[get_department_code] Ошибка: Необнаружен код отдела")
            return None
    else:
        code = None
        print("[get_department_code] Ошибка: Необнаружены данные для отдела")
    return code
