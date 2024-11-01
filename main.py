import sys

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPalette, QColor, QIcon, QPixmap, QPainter, QIntValidator
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QComboBox, QStyledItemDelegate, QLineEdit, \
    QTableWidgetItem, QListWidget, QAbstractItemView, QListWidgetItem

from app.models import Employee, MotivationProgram, Department, MotivationThreshold
from app.models.control_models import delete_motivation_program, get_current_roles
from app.ui.main_window_ui import Ui_MainWindow
from app.helpers.helpers import fill_employees_table, get_icon_from_svg
from app.db import get_session
from app.ui.styles import CONFIRM_DIALOG_STYLE, WARNING_DIALOG_STYLE

with get_session() as session:
    employees = session.query(Employee).all()
    roles = session.query(MotivationProgram).all()
    departments = session.query(Department).all()


class NumericDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        validator = QIntValidator(0, 1000000, editor)  # Измените диапазон по мере необходимости
        editor.setValidator(validator)
        return editor


class SalaryReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Выпадающий список выбора отдела
        self.ui.department.clear()  # Удаляем предустановленные в дизайнере отделы(Удалить в дизайнере)
        self.ui.department.addItems([department.name for department in departments])
        self.ui.department.currentIndexChanged.connect(self.set_current_roles)

        # Программы мотивации(Список)
        self.set_current_roles()
        self.ui.roles_list.currentItemChanged.connect(  # Заполняем таблицу при выборе роли
                                        self.fill_role_settings_table
        )
        self.ui.roles_list.itemChanged.connect(self.update_role_in_db)
        self.ui.roles_list.setCurrentRow(0)  # По умолчанию выбираем первый элемент списка
        self.ui.roles_add_button.clicked.connect(self.add_role)
        self.ui.roles_delete.clicked.connect(self.delete_role)

        # Таблица настройки мотивации
        self.ui.table_motivate_settings.setColumnCount(2)
        self.ui.table_motivate_settings.setHorizontalHeaderLabels(["Выручка в руб.", "Сумма вознаграждения(руб.)"])
        # Установка валидации ввода для таблицы настройки мотивации
        numeric_delegate = NumericDelegate(self.ui.table_motivate_settings)
        self.ui.table_motivate_settings.setItemDelegateForColumn(0, numeric_delegate)
        self.ui.table_motivate_settings.setItemDelegateForColumn(1, numeric_delegate)

        # Подключаем кнопки добавления строк в таблицу настройки мотивации
        self.ui.button_add_threshhold.clicked.connect(self.add_row)
        self.ui.button_delete_threshold.clicked.connect(self.remove_selected_row)

        # Устанавливаем иконки для кнопки добавления строки в таблицу порогов мотивации
        icon = get_icon_from_svg("app/ui/icons/add.svg")
        self.ui.button_add_threshhold.setText("")
        self.ui.button_add_threshhold.setIcon(icon)
        # Устанавливаем иконку для кнопки удаления строки из таблицы порогов мотивации
        icon = get_icon_from_svg("app/ui/icons/delete.svg")
        self.ui.button_delete_threshold.setText("")
        self.ui.button_delete_threshold.setIcon(icon)

        self.ui.button_settings_save.clicked.connect(self.save_table_data_to_db)

    def set_current_roles(self):
        """
        Функция колбэк для заполнения списка ролей.
        Вызывается при изменении списка отделов.
        Также применяется когда нужно заполнить список ролей(программ мотивации)
        в соответствии с выбранным в выпадающем списке отделом.
        """
        # Отчищаем список ролей
        self.ui.roles_list.clear()
        # Получаем название выбранного отдела
        department_name = self.ui.department.currentText()
        # Получаем роли привязанные к выбранному отделу
        current_roles = get_current_roles(department_name)
        # Заполняем список ролей
        for role in current_roles:
            item = QListWidgetItem(role.name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            item.setData(Qt.ItemDataRole.UserRole, role.name)
            self.ui.roles_list.addItem(item)

    def add_role(self) -> None:
        """
        Функция колбэк для кнопки добавления роли(Программы мотивации).
        Добавляет новую роль если такой нет.
        """
        department_name = self.ui.department.currentText()
        if department_name:
            with get_session() as session:
                department_code = session.query(Department).filter(Department.name == department_name).first().code
        new_role = self.ui.roles_add_line.text()
        if new_role:
            with get_session() as session:
                roles = session.query(MotivationProgram).all()
                if new_role not in [role.name for role in roles]:
                    session.add(MotivationProgram(name=new_role, department_code=department_code))
                    session.commit()
                self.ui.roles_add_line.clear()
                self.ui.roles_add_line.setFocus()
                self.set_current_roles()

    def delete_role(self) -> None:
        selected_item = self.ui.roles_list.currentItem()

        if selected_item:
            item_text = selected_item.text()

            # Создание диалога подтверждения
            confirm_dialog = QMessageBox(self)
            confirm_dialog.setWindowTitle("Подтверждение")
            confirm_dialog.setText(f"Вы уверены, что хотите удалить '{item_text}'?")
            confirm_dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            button_yes = confirm_dialog.button(QMessageBox.StandardButton.Yes)
            button_no = confirm_dialog.button(QMessageBox.StandardButton.No)
            button_yes.setText("Удалить")
            button_no.setText("Отмена")

            # Установка стиля с помощью QPalette
            palette = confirm_dialog.palette()
            palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 0))  # Прозрачный фон
            palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))  # Белый текст
            confirm_dialog.setPalette(palette)

            # Установка стиля с помощью QStyleSheet
            confirm_dialog.setStyleSheet(CONFIRM_DIALOG_STYLE)

            reply = confirm_dialog.exec()

            if reply == QMessageBox.StandardButton.Yes:
                # Выполняем удаление
                delete_motivation_program(name=item_text)
                # Обновляем список ролей(Программ мотивации) в UI
                self.set_current_roles()

                print(f"Удаление {item_text} выполнено!")
            else:
                print("Удаление отменено!")

        else:
            msg_box = QMessageBox(
                QMessageBox.Icon.Warning,
                "Предупреждение",
                "Выберите элемент для удаления!",
                QMessageBox.StandardButton.Ok,
                self
            )

            msg_box.setStyleSheet(WARNING_DIALOG_STYLE)
            msg_box.exec()

    def update_role_in_db(self, item):
        """
        Функция колбэк для сохранения изменений в таблице настроек мотивации.
        Сохраняет изменения в таблице настроек мотивации в БД.
        """
        new_name = item.text()
        original_name = item.data(Qt.ItemDataRole.UserRole)

        if new_name != original_name:
            with get_session() as session:
                session.query(MotivationProgram).filter(MotivationProgram.name == original_name).update(
                    {"name": new_name})
                session.commit()
                print(f"Изменение названия роли с '{original_name}' на '{new_name}' выполнено!")
        else:
            print("Изменение названия роли отменено!")

    def add_row(self):
        """
        Функция колбэк для кнопки добавления строки в таблицу настроек мотивации.
        Добавляет новую строку в таблицу.
        :return:
        """
        current_row_count = self.ui.table_motivate_settings.rowCount()
        self.ui.table_motivate_settings.insertRow(current_row_count)

    def remove_selected_row(self):
        """
        Функция колбэк для кнопки удаления строки в таблице настроек мотивации.
        Удаляет выбранную строку в таблице.
        :return:
        """
        selected_row = self.ui.table_motivate_settings.currentRow()
        if selected_row >= 0:
            self.ui.table_motivate_settings.removeRow(selected_row)
        else:
            msg_box = QMessageBox(
                QMessageBox.Icon.Warning,
                "Предупреждение",
                "Пожалуйста, выберите строку для удаления.",
                QMessageBox.StandardButton.Ok,
                self
            )

            msg_box.setStyleSheet(WARNING_DIALOG_STYLE)
            msg_box.exec()

    def fill_role_settings_table(self):
        """
        Функция заполнения таблицы настроек мотивации.
        Заполняет таблицу настройками мотивации для выбранной роли.
        :return:
        """
        if current_role := self.ui.roles_list.currentItem():
            current_role_name: str = current_role.text()
        else:
            self.ui.table_motivate_settings.clear()
            return
        with get_session() as session:
            role: MotivationProgram = session.query(MotivationProgram).filter(
                MotivationProgram.name == current_role_name).first()
            self.ui.table_motivate_settings.setRowCount(len(role.thresholds))
            for i, threshold in enumerate(role.thresholds):
                self.ui.table_motivate_settings.setItem(i, 0, QTableWidgetItem(str(threshold.revenue_threshold)))
                self.ui.table_motivate_settings.setItem(i, 1, QTableWidgetItem(str(threshold.salary)))

    def save_table_data_to_db(self):
        """
        Функция обновления настроек мотивации из таблицы.
        Обновляет настройки мотивации из таблицы в БД, если есть запись с таким порогом привязанная к роли.
        И создает новую если нет
        :return:
        """
        if current_role := self.ui.roles_list.currentItem():
            current_role_name: str = current_role.text()
        else:
            msg_box = QMessageBox(
                QMessageBox.Icon.Warning,
                "Предупреждение",
                "Ни одна программа не была выбрана, чтобы настроить мотивацию, сначала выберите программу",
                QMessageBox.StandardButton.Ok,
                self
            )

            msg_box.setStyleSheet(WARNING_DIALOG_STYLE)
            msg_box.exec()
            return

        row_count = self.ui.table_motivate_settings.rowCount()

        with get_session() as session:
            for row in range(row_count):
                # Поскольку, у нас есть две колонки: revenue_threshold и salary
                revenue_threshold_item = self.ui.table_motivate_settings.item(row, 0)
                salary_item = self.ui.table_motivate_settings.item(row, 1)

                thresholds_record = session.query(
                    MotivationThreshold).join(MotivationProgram).filter(
                    MotivationProgram.name == current_role_name,
                    MotivationThreshold.revenue_threshold == int(revenue_threshold_item.text())
                ).first()

                if thresholds_record:
                    thresholds_record.salary = int(salary_item.text())
                else:
                    current_motivation_program = session.query(MotivationProgram).filter(
                        MotivationProgram.name == current_role_name).first()

                    session.add(MotivationThreshold(revenue_threshold=int(revenue_threshold_item.text()),
                                                   salary=int(salary_item.text()),
                                                   motivation_program=current_motivation_program))
                session.commit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SalaryReader()
    window.show()
    sys.exit(app.exec())
