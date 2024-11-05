# TODO: Перенести логику changes_made полностью в контроллер table_controller

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QStyledItemDelegate, QLineEdit, \
    QTableWidgetItem, QListWidgetItem

from app.models import Employee, MotivationProgram, Department, MotivationThreshold
from app.models.control_models import delete_motivation_program, get_current_roles_by_department_code, thresholds_clear
from app.ui.controllers.table_controller import ThresholdsTableController
from app.ui.main_window_ui import Ui_MainWindow
from app.helpers.helpers import get_icon_from_svg, set_departments, get_department_code
from app.db import get_session
from app.ui.styles import CONFIRM_DIALOG_STYLE, WARNING_DIALOG_STYLE

with get_session() as session:
    EMPLOYEES_INIT = session.query(Employee).all()
    ROLES_INIT = session.query(MotivationProgram).all()
    DEPARTMENTS_INIT = session.query(Department).all()


class NumericDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        validator = QIntValidator(0, 1000000, editor)  # Измените диапазон по мере необходимости
        editor.setValidator(validator)
        return editor


class SalaryReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.changes_made = False  # При изменении данных в таблице, флаг становится True, при сохранении/отмене - False
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.threshold_table_controller = ThresholdsTableController(self.ui.table_motivate_settings)

        # Выпадающий список выбора отдела
        set_departments(self.ui.department, DEPARTMENTS_INIT)
        self.ui.department.currentIndexChanged.connect(  # При выборе отдела выводим список его программ
            self.set_current_roles
        )

        # Программы мотивации(Список)
        self.set_current_roles()  # На старте выводим список программ выбранного отдела
        self.ui.roles_list.currentItemChanged.connect(  # Заполняем таблицу при выборе роли
            self.fill_role_settings_table
        )

        self.ui.roles_list.itemChanged.connect(self.update_role_in_db)
        self.ui.roles_add_button.clicked.connect(self.add_role)
        self.ui.roles_delete.clicked.connect(self.delete_role)

        # Таблица настройки мотивации
        self.ui.table_motivate_settings.setColumnCount(3)
        self.ui.table_motivate_settings.setHorizontalHeaderLabels(
            ["Выручка в руб.", "Сумма вознаграждения(руб.)", "no_role"]
        )
        # Скрываем третий столбец, он для технических нужд:
        self.ui.table_motivate_settings.setColumnHidden(2, True)
        # Выбираем первую роль в списке и заполняем таблицу на открытии
        self.ui.roles_list.setCurrentRow(0)
        self.fill_role_settings_table()

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

        self.ui.button_settings_save.clicked.connect(lambda: self.save_table_data_to_db(on_save_button_push=True))

    def set_current_roles(self):
        """
        Функция колбэк для заполнения списка ролей.
        Вызывается при изменении индекса выбранного элемента списка отделов.(Выборе отдела, отличного от текущего)
        Также применяется когда нужно заполнить список ролей(программ мотивации)
        в соответствии с выбранным в выпадающем списке отделом.
        """
        # Отчищаем список ролей
        self.ui.roles_list.clear()
        # Получаем код выбранного отдела
        department_code = get_department_code(self.ui.department)
        # Получаем роли привязанные к выбранному отделу по коду отдела
        current_roles = get_current_roles_by_department_code(department_code)
        # Заполняем список ролей
        for role in current_roles:
            item = QListWidgetItem(role.name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            item.setData(Qt.ItemDataRole.UserRole, {
                "role_id": role.id,
            })
            self.ui.roles_list.addItem(item)
        self.ui.roles_list.setCurrentRow(0)  # По умолчанию выбираем первый элемент списка

    def add_role(self) -> None:
        """
        Функция колбэк для кнопки добавления роли(Программы мотивации).
        Добавляет новую роль если такой нет.
        """
        try:
            current_department_code = get_department_code(self.ui.department)
        except Exception as e:
            print(f"[add_role] Ошибка при получении кода отдела {e}")
            # Если почему-то не выбран отдел выбрасываем сообщение
            confirm_dialog = QMessageBox(self)
            confirm_dialog.setWindowTitle("Ошибка, не выбран отдел")
            confirm_dialog.setText("Выберите отдел")
            confirm_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
            confirm_dialog.exec()
            return

        new_role_name = self.ui.roles_add_line.text()
        if not new_role_name:
            return

        with get_session() as session:
            # Получаем роли привязанные к выбранному отделу по коду отдела
            current_roles = get_current_roles_by_department_code(current_department_code)

            # Если на данном отделе еще нет роли с таким названием
            if new_role_name not in [role.name for role in current_roles]:
                motivation_program = MotivationProgram(name=new_role_name, department_code=current_department_code)
                session.add(motivation_program)
                session.commit()
            else:
                confirm_dialog = QMessageBox(self)
                confirm_dialog.setWindowTitle("Ошибка, роль уже существует")
                confirm_dialog.setText(f"Программа с именем '{new_role_name}' уже существует")
                confirm_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
                confirm_dialog.exec()
            self.ui.roles_add_line.clear()
            self.ui.roles_add_line.setFocus()
            self.set_current_roles()

    def delete_role(self) -> None:
        current_role = self.ui.roles_list.currentItem()

        if current_role:
            current_role_data = current_role.data(Qt.ItemDataRole.UserRole)
            role_id = current_role_data["role_id"]
            item_text = current_role.text()

            # Создание диалога подтверждения
            confirm_dialog = QMessageBox(self)
            confirm_dialog.setWindowTitle("Подтверждение")
            confirm_dialog.setText(f"Вы уверены, что хотите удалить программу'{item_text}'?")
            confirm_dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            button_yes = confirm_dialog.button(QMessageBox.StandardButton.Yes)
            button_no = confirm_dialog.button(QMessageBox.StandardButton.No)
            button_yes.setText("Удалить")
            button_no.setText("Отмена")

            # Установка стиля
            confirm_dialog.setStyleSheet(CONFIRM_DIALOG_STYLE)

            reply = confirm_dialog.exec()

            if reply == QMessageBox.StandardButton.Yes:
                # Выполняем удаление
                delete_motivation_program(role_id)
                # Обновляем список ролей(Программ мотивации) в UI
                self.set_current_roles()

                print(f"Удаление {item_text} выполнено!")
            else:
                print("Удаление отменено!")

        else:
            msg_box = QMessageBox(
                QMessageBox.Icon.Warning,
                "Предупреждение",
                "Выберите программу для удаления!",
                QMessageBox.StandardButton.Ok,
                self
            )

            msg_box.setStyleSheet(WARNING_DIALOG_STYLE)
            msg_box.exec()

    def update_role_in_db(self, item):
        """
        Функция колбэк для сохранения изменений роли (Программы мотивации).
        Сохраняет изменения роли в БД.
        """
        new_name = item.text()
        current_role_id = item.data(Qt.ItemDataRole.UserRole)["role_id"]

        with get_session() as session:
            current_roles = get_current_roles_by_department_code(self.ui.department.currentData()["department_code"])
            if new_name not in [role.name for role in current_roles]:
                session.query(MotivationProgram).filter(MotivationProgram.id == current_role_id
                                                        ).update({"name": new_name})
                session.commit()
                print(f"Изменение названия роли на '{new_name}' выполнено!")
                # Перерисовываем роли из БД, чтобы отразить актуальное состояние
            else:
                msg_box = QMessageBox(
                    QMessageBox.Icon.Warning,
                    "Предупреждение",
                    "Программа с таким именем уже существует!",
                    QMessageBox.StandardButton.Ok,
                    self
                )
                msg_box.setStyleSheet(WARNING_DIALOG_STYLE)
                msg_box.exec()
            self.set_current_roles()

    def add_row(self):
        """
        Функция колбэк для кнопки добавления строки в таблицу настроек мотивации.
        Добавляет новую строку в таблицу.
        """
        # Если выбрана программа добавляем строку
        if current_role := self.ui.roles_list.currentItem():
            current_role_data: dict = current_role.data(Qt.ItemDataRole.UserRole)
            current_role_id: str = str(current_role_data["role_id"])

            current_row_count = self.ui.table_motivate_settings.rowCount()
            self.ui.table_motivate_settings.insertRow(current_row_count)
            # Добавляем в header информацию о роли к которой привязана таблица
            # (3 столбец скрыт и используется длля хнанения роли)
            self.ui.table_motivate_settings.horizontalHeaderItem(2).setText(current_role_id)

        else:
            msg_box = QMessageBox(
                QMessageBox.Icon.Warning,
                "Предупреждение",
                "Пожалуйста, выберите программу к которой хотите добавить мотивацию.",
                QMessageBox.StandardButton.Ok,
                self
            )

            msg_box.setStyleSheet(WARNING_DIALOG_STYLE)
            msg_box.exec()

    def remove_selected_row(self):
        """
        Функция колбэк для кнопки удаления строки в таблице настроек мотивации.
        Удаляет выбранную строку в таблице.
        """
        selected_row = self.ui.table_motivate_settings.currentRow()
        if selected_row >= 0:
            self.ui.table_motivate_settings.removeRow(selected_row)
            self.threshold_table_controller.changes_made = True
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
        """
        # Проверяем есть ли несохраненные изменения
        if self.threshold_table_controller.changes_made:
            msg_box = QMessageBox(
                QMessageBox.Icon.Warning,
                "Предупреждение",
                f"Есть не сохраненные изменения программы мотивации.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                self
            )

            button_yes = msg_box.button(QMessageBox.StandardButton.Yes)
            button_no = msg_box.button(QMessageBox.StandardButton.No)
            #button_cancel = msg_box.button(QMessageBox.StandardButton.Cancel)
            button_yes.setText("Сохранить")
            button_no.setText("Отменить")
            #button_cancel.setText("Вернуться к редактированию программы мотивации")

            msg_box.setStyleSheet(WARNING_DIALOG_STYLE)
            reply = msg_box.exec()
            if reply == QMessageBox.StandardButton.Yes:
                self.save_table_data_to_db(on_save_button_push=False)  # Даём понять что сохранение не по кнопке
            elif reply == QMessageBox.StandardButton.No:
                self.threshold_table_controller.changes_made = False

        # Блокируем сигналы чтобы не перехватывать изменения в таблице
        self.ui.table_motivate_settings.blockSignals(True)

        # Отчищаем таблицу
        self.ui.table_motivate_settings.setRowCount(0)

        if current_role := self.ui.roles_list.currentItem():
            print(f"Current role :{current_role}")
            current_role_data: dict = current_role.data(Qt.ItemDataRole.UserRole)
            current_role_id: str = str(current_role_data["role_id"])
        else:
            print(f"Current role не указана, оставляем таблицу пустой")
            # Разблокируем сигналы
            self.ui.table_motivate_settings.blockSignals(False)
            return
        with get_session() as session:
            self.ui.table_motivate_settings.horizontalHeaderItem(2).setText(current_role_id)

            current_motivation_program: MotivationProgram = session.query(MotivationProgram).filter(
                MotivationProgram.id == current_role_id).first()

            # Загружаем данные в таблицу из db используя контроллер
            self.threshold_table_controller.load_data(current_motivation_program)

            # Разблокируем сигналы
            self.ui.table_motivate_settings.blockSignals(False)

    def save_table_data_to_db(self, on_save_button_push: bool = False):
        """
        Сохраняет данные таблицы в базу данных.

        Args:
            on_save_button_push (bool): Флаг, указывающий, было ли сохранение инициировано нажатием кнопки
        """
        try:
            # Получаем id программы мотивации из заголовка таблицы
            current_table_role_id = self.ui.table_motivate_settings.horizontalHeaderItem(2).text()

            # Проверяем, привязана ли таблица к программе мотивации
            if current_table_role_id == 'no_role':
                QMessageBox.warning(
                    self,
                    "Предупреждение",
                    "Таблица пуста и не привязана ни к одной программе мотивации",
                    QMessageBox.StandardButton.Ok
                )
                return

            with get_session() as session:
                # Получаем программу мотивации
                current_motivation_program = session.query(MotivationProgram).filter(
                    MotivationProgram.id == current_table_role_id
                ).first()

                # Если программа не найдена
                if not current_motivation_program:
                    raise ValueError("Программа мотивации не найдена")

                # Сохраняем данные используя контроллер таблицы
                if self.threshold_table_controller.save_data(current_motivation_program, session):
                    self.threshold_table_controller.changes_made = False

                    # Если сохранение было по кнопке, обновляем отображение таблицы
                    if on_save_button_push:
                        self.fill_role_settings_table()

                    msg_box = QMessageBox(
                        QMessageBox.Icon.Information,
                        "Успех",
                        "Данные успешно сохранены",
                        QMessageBox.StandardButton.Ok,
                        self
                    )

                    msg_box.setStyleSheet(WARNING_DIALOG_STYLE)  # TODO: Сделать шаблон  SUCCESS_DIALOG_STYLE
                    msg_box.exec()

        except Exception as e:
            msg_box = QMessageBox(
                QMessageBox.Icon.Critical,
                "Ошибка",
                f"Не удалось сохранить данные: {str(e)}",
                QMessageBox.StandardButton.Ok,
                self
            )

            msg_box.setStyleSheet(WARNING_DIALOG_STYLE)
            msg_box.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SalaryReader()
    window.show()
    sys.exit(app.exec())
