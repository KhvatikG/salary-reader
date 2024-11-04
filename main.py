import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QStyledItemDelegate, QLineEdit, \
    QTableWidgetItem, QListWidgetItem

from app.models import Employee, MotivationProgram, Department, MotivationThreshold
from app.models.control_models import delete_motivation_program, get_current_roles_by_department_code, thresholds_clear
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
        # Установка валидации ввода для таблицы настройки мотивации:
        numeric_delegate = NumericDelegate(self.ui.table_motivate_settings)
        self.ui.table_motivate_settings.setItemDelegateForColumn(0, numeric_delegate)
        self.ui.table_motivate_settings.setItemDelegateForColumn(1, numeric_delegate)
        self.ui.table_motivate_settings.itemChanged.connect(self.on_table_item_changes)
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
            self.ui.table_motivate_settings.setItem(current_row_count, 0, QTableWidgetItem("0"))
            self.ui.table_motivate_settings.setItem(current_row_count, 1, QTableWidgetItem("0"))
            self.ui.table_motivate_settings.setItem(current_row_count, 2, QTableWidgetItem(current_role_id))
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
        self.changes_made = True
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
        """
        # Проверяем есть ли несохраненные изменения
        if self.changes_made:
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
                self.changes_made = False

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

            role: MotivationProgram = session.query(MotivationProgram).filter(
                MotivationProgram.id == current_role_id).first()

            self.ui.table_motivate_settings.setRowCount(len(role.thresholds))

            for i, threshold in enumerate(role.thresholds):
                self.ui.table_motivate_settings.setItem(i, 0, QTableWidgetItem(str(threshold.revenue_threshold)))
                self.ui.table_motivate_settings.setItem(i, 1, QTableWidgetItem(str(threshold.salary)))
                self.ui.table_motivate_settings.setItem(i, 2, QTableWidgetItem(current_role_id))
            # Разблокируем сигналы
            self.ui.table_motivate_settings.blockSignals(False)

    def save_table_data_to_db(self, on_save_button_push: bool = False):
        """
        Функция обновления настроек мотивации из таблицы.
        Обновляет пороги мотивации из таблицы порогов в БД, если есть запись с таким порогом привязанная к роли.
        И создает новый порог если нет.

        Если сохранение произошло с кнопки(on_save_button_push=True) то отрисует таблицу для current_role.

        Current_role - в данном контексте это роль которая в данный момент выбрана в списке ролей.
        Не одно и тоже что current_table_role_name - эта переменная содержит имя роли к которой привязана
        таблица, и хранящееся в самой таблице.
        :param on_save_button_push Если функцию использует не нажатие кнопки под таблицей порогов,
         то его необходимо установить в false.
         Это необходимо для корректного обновления(отрисовки) таблицы в интерфейсе после сохранения.
         Если параметр on_save_button_push == True, то запускается отрисовка таблицы.
        :return:
        """
        self.changes_made = False
        # Извлекаем заложенное в заголовок третьего столбца id роли к которой привязана таблица
        current_table_role_id = self.ui.table_motivate_settings.horizontalHeaderItem(2).text()
        # Если заголовок третьего столбца нетронут, значит строки еще не добавлялись
        if current_table_role_id == 'no_role':
            msg_box = QMessageBox(
                QMessageBox.Icon.Warning,
                "Предупреждение",
                "Таблица пуста и не привязана ни к одной роли",
                QMessageBox.StandardButton.Ok,
                self
            )

            msg_box.setStyleSheet(WARNING_DIALOG_STYLE)
            msg_box.exec()
            return

        row_count = self.ui.table_motivate_settings.rowCount()

        with get_session() as session:
            # Получаем программу
            current_motivation_program = session.query(MotivationProgram).filter(
                MotivationProgram.id == current_table_role_id).first()
            # Отчищаем пороги
            thresholds_clear(current_motivation_program, session)
            if row_count == 0:  # Если таблица пуста (уже привязана, но отчищена)
                session.commit()  # То сохраняем без порогов и выходим
                return

            else:  # Если таблица не пуста
                for row in range(row_count):
                    print(f"Строка {row}")
                    # Поскольку, у нас есть две колонки: revenue_threshold и salary
                    revenue_threshold_item = self.ui.table_motivate_settings.item(row, 0)
                    salary_item = self.ui.table_motivate_settings.item(row, 1)

                    thresholds_record = session.query(
                        MotivationThreshold).join(MotivationProgram).filter(
                        MotivationProgram.id == current_table_role_id,
                        MotivationThreshold.revenue_threshold == int(revenue_threshold_item.text())
                    ).first()

                    if thresholds_record:
                        print(f"Найден порог {thresholds_record}")
                        thresholds_record.salary = int(salary_item.text())
                    else:
                        print("Порог не найден")
                        # Сохраняем измененные
                        session.add(MotivationThreshold(revenue_threshold=int(revenue_threshold_item.text()),
                                                        salary=int(salary_item.text()),
                                                        motivation_program=current_motivation_program))
                session.commit()
        # После сохранения актуализируем таблицу если она была сохранена кнопкой под таблицей
        if on_save_button_push:
            print("Была нажата кнопка")
            self.fill_role_settings_table()

    def on_table_item_changes(self, item):
        """
        Функция для отслеживания несохраненных изменений в таблице мотивации.
        Фиксирует факт несохраненных изменений.
        Устанавливает флаг changes_made в True
        После сохранения или отмены этот флаг должен быть сброшен.
        :return:
        """
        self.changes_made = True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SalaryReader()
    window.show()
    sys.exit(app.exec())
