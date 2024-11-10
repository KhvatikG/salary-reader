from PySide6.QtWidgets import QStyledItemDelegate, QLineEdit, QTableWidgetItem, QMessageBox, QTableWidget, \
    QAbstractItemView
from PySide6.QtGui import QIntValidator
from PySide6.QtCore import Qt

from app.models import MotivationThreshold, MotivationProgram


class NumericDelegate(QStyledItemDelegate):
    """
    Делегат для таблицы, который контролирует как данные отображаются и редактируются.
    Делегат - это посредник между данными и их визуальным представлением.
    """

    def createEditor(self, parent, option, index):
        """
        Создает виджет редактирования для ячейки.
        Вызывается когда пользователь начинает редактировать ячейку.

        parent - родительский виджет (таблица)
        option - параметры отображения
        index - индекс ячейки в модели данных
        """
        # Создаем поле для ввода текста
        editor = QLineEdit(parent)
        # Создаем валидатор, который разрешает вводить только целые числа от 0 до 1000000
        validator = QIntValidator(0, 1000000, editor)
        # Устанавливаем валидатор для поля ввода
        editor.setValidator(validator)
        return editor

    def setEditorData(self, editor, index):
        """
        Устанавливает начальные данные в редактор.
        Вызывается когда начинается редактирование ячейки.

        editor - виджет редактирования (QLineEdit)
        index - индекс ячейки в модели данных
        """
        # Получаем текущее значение из модели данных
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        # Если значение содержит форматирование (пробелы и 'руб.'), убираем их
        if isinstance(value, str):
            value = value.replace(" ", "").replace("руб.", "")
        # Устанавливаем очищенное значение в редактор
        editor.setText(str(value))

    def setModelData(self, editor, model, index):
        """
        Сохраняет отредактированные данные обратно в модель.
        Вызывается когда пользователь заканчивает редактирование.

        editor - виджет редактирования (QLineEdit)
        model - модель данных таблицы
        index - индекс ячейки
        """
        # Получаем введенное значение и преобразуем его в число
        value = int(editor.text())
        # Сохраняем значение в модель
        model.setData(index, value, Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        """
        Устанавливает размер и положение редактора.

        editor - виджет редактирования
        option - параметры отображения, включая прямоугольник ячейки
        index - индекс ячейки
        """
        # Устанавливаем геометрию редактора равной размеру ячейки
        editor.setGeometry(option.rect)

# TODO: Добавить метод table_init с настройкой начальных параметров
# TODO: Написать родительский класс для контроллеров
class ThresholdsTableController:
    """
    Контроллер таблицы, управляющий отображением и редактированием данных
    """

    def __init__(self, table_widget: QTableWidget):
        """
        Инициализация контроллера.

        :param table_widget: Виджет таблицы порогов
        """
        self.changes_made: bool = False
        # Сохраняем ссылку на таблицу
        self.table_widget = table_widget
        # Устанавливаем наш делегат для всей таблицы
        self.table_widget.setItemDelegate(NumericDelegate(self.table_widget))
        # Подключаем обработчик изменений в таблице
        self.table_widget.itemChanged.connect(self.on_item_changed)

    def on_item_changed(self, item):
        """
        Обрабатывает изменения в ячейках таблицы.
        Форматирует числа, добавляя разделители и обозначение валюты.

        item - измененный элемент таблицы
        """
        column = item.column()
        if column in [0, 1]:  # Если изменение в колонках с числами
            # Получаем значение как число
            value = item.data(Qt.ItemDataRole.EditRole)
            # Форматируем число, добавляя разделители групп разрядов и обозначение валюты
            formatted_value = f"{value:,} руб.".replace(",", " ")
            # Устанавливаем отформатированное значение ---------------------------------
            # Отключаем сигналы, чтобы не перехватывать вставку отформатированной строки
            self.table_widget.blockSignals(True)

            # Устанавливаем отформатированное значение
            item.setText(formatted_value)

            # Устанавливаем флаг о том что внесены не сохраненные изменения
            self.changes_made = True

            # Врубаем сигналы обратно
            self.table_widget.blockSignals(False)
            # --------------------------------------------------------------------------

    def load_data(self, motivation_program):
        """
        Загружает данные программы мотивации в таблицу.

        motivation_program - объект программы мотивации
        """
        # TODO: Перенести сюда логику получения данных из бд и передать сюда сессию
        # Устанавливаем количество строк равным количеству порогов
        self.table_widget.setRowCount(len(motivation_program.thresholds))

        # Для каждого порога создаем элементы таблицы
        for i, threshold in enumerate(motivation_program.thresholds):
            # Форматируем значения с разделителями и обозначением валюты
            revenue_value = f"{threshold.revenue_threshold:,} руб.".replace(",", " ")
            salary_value = f"{threshold.salary:,} руб.".replace(",", " ")

            # Создаем элементы таблицы
            revenue_item = QTableWidgetItem(revenue_value)
            salary_item = QTableWidgetItem(salary_value)

            # Устанавливаем элементы в таблицу
            self.table_widget.setItem(i, 0, revenue_item)
            self.table_widget.setItem(i, 1, salary_item)

    def save_data(self, motivation_program, session):
        """
        Сохраняет данные из таблицы в базу данных.

        Args:
            motivation_program (MotivationProgram): Программа мотивации, для которой сохраняются пороги
            session: Сессия SQLAlchemy для работы с базой данных
        """
        try:
            # Получаем количество строк в таблице
            row_count = self.table_widget.rowCount()

            # Очищаем существующие пороги для программы мотивации
            session.query(MotivationThreshold).filter(
                MotivationThreshold.motivation_program_id == motivation_program.id
            ).delete()

            # Если таблица пуста, просто сохраняем изменения и выходим
            if row_count == 0:
                session.commit()
                self.changes_made = False
                return True

            # Список для новых порогов
            new_thresholds = []

            # Проходим по всем строкам таблицы
            for row in range(row_count):
                try:
                    # Получаем элементы таблицы
                    revenue_item = self.table_widget.item(row, 0)
                    salary_item = self.table_widget.item(row, 1)

                    if revenue_item is None or salary_item is None:
                        continue

                    # Очищаем значения от форматирования
                    revenue = int(revenue_item.text().replace(" ", "").replace("руб.", ""))
                    salary = int(salary_item.text().replace(" ", "").replace("руб.", ""))

                    # Создаем новый порог
                    threshold = MotivationThreshold(
                        revenue_threshold=revenue,
                        salary=salary,
                        motivation_program_id=motivation_program.id
                    )

                    # Добавляем порог в список
                    new_thresholds.append(threshold)

                except (ValueError, AttributeError) as e:
                    # Если возникла ошибка при обработке строки, пропускаем её
                    print(f"Ошибка при обработке строки {row}: {e}")
                    continue

            # Проверяем, что пороги уникальны по revenue_threshold
            revenue_values = [t.revenue_threshold for t in new_thresholds]
            if len(revenue_values) != len(set(revenue_values)):
                raise ValueError("Обнаружены дублирующиеся значения выручки в порогах")

            # Сортируем пороги по возрастанию revenue_threshold
            new_thresholds.sort(key=lambda x: x.revenue_threshold)

            # Добавляем все новые пороги в сессию
            for threshold in new_thresholds:
                session.add(threshold)

            # Сохраняем изменения в базе данных
            session.commit()
            self.changes_made = False
            return True

        except Exception as e:
            # В случае ошибки откатываем изменения
            session.rollback()
            print(f"Ошибка при сохранении данных: {e}")
            # Можно также показать диалог с ошибкой пользователю
            self._show_error_dialog(str(e))
            return False

    def _show_error_dialog(self, message):
        """
        Показывает диалоговое окно с сообщением об ошибке.

        Args:
            message (str): Текст сообщения об ошибке
        """
        dialog = QMessageBox()
        dialog.setIcon(QMessageBox.Icon.Critical)
        dialog.setWindowTitle("Ошибка")
        dialog.setText(message)
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        dialog.setStyleSheet("""
            QMessageBox {
                background-color: #f0f0f0;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                min-height: 24px;
                background-color: #e1e1e1;
                border: 1px solid #b8b8b8;
                border-radius: 3px;
            }
            QMessageBox QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        dialog.exec_()


class EmployeesTableController():
    """
    Класс для управления таблицей сотрудников, привязанных к роли.
    """
    def __init__(self, table_widget: QTableWidget):
        """
        Инициализация контроллера

        :param table_widget: Виджет таблицы сотрудников
        """
        # Инициализация таблицы
        self.table_widget = table_widget
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(
            ["Табельный номер", "Имя", "Отделы"]
        )
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def load_data(self, motivation_program: MotivationProgram):
        """
        Загружает данные о пользователях привязанных к переданной motivation_program из базы данных в таблицу.
        :param motivation_program: Объект программы мотивации.
        """
        # TODO: Перенести сюда логику получения данных из бд и передать сюда сессию
        # Устанавливаем количество строк равным количеству порогов
        self.table_widget.setRowCount(len(motivation_program.employees))

        # Для каждого порога создаем элементы таблицы
        for i, employee in enumerate(motivation_program.employees):
            # Форматируем значения с разделителями и обозначением валюты
            code = str(employee.code)
            name = employee.name
            departments = str([department.name for department in employee.departments])

            # Создаем элементы таблицы
            code_item = QTableWidgetItem(code)
            name_item = QTableWidgetItem(name)
            departments_item = QTableWidgetItem(departments)

            # Устанавливаем элементы в таблицу
            self.table_widget.setItem(i, 0, code_item)
            self.table_widget.setItem(i, 1, name_item)
            self.table_widget.setItem(i, 2, departments_item)


