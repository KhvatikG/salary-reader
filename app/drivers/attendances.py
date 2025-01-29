import enum
import logging
from datetime import datetime, date, timedelta
from typing import AnyStr, Union
from uuid import UUID

from PySide6.QtGui import QColor, Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView

from app.db import get_session
from app.models import MotivationProgram, MotivationThreshold, Employee
from app.models.control_models import get_department_by_code
from iiko_api import iiko_api

from iiko_api.core.config.logging_config import get_logger

# TODO: Вынести в settings(Для настроек нужна отдельная таблица в бд)
FULL_SHIFT_HOURS = 10
HALF_SHIFT_HOURS = 5

logger = get_logger(__name__, level="DEBUG")


class ShiftType(enum.Enum):
    FULL = "full"
    HALF = "half"
    WARNING = "warning"

    def __str__(self):
        if self == ShiftType.FULL:
            return "ПОЛНАЯ"
        elif self == ShiftType.HALF:
            return "Пол смены"
        elif self == ShiftType.WARNING:
            return "ОБРАТИТЬ ВНИМАНИЕ"
        else:
            return "Неизвестный"


class EmployeeId(str):
    """
    Тип данных, представляющий собой строку в формате UUID.
    Используется для хранения и валидации идентификатора сотрудника.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: AnyStr) -> Union[str, None]:
        if not isinstance(value, str):
            raise TypeError(f'Значение должно быть строкой, получено: {type(value)}')
        try:
            UUID(value)
        except ValueError as e:
            raise ValueError(f'Некорректный UUID: {value}') from e
        return value


class Attendance:
    def __init__(self, employee_id: EmployeeId, date_from: datetime, date_to: datetime):
        self.employee_id = employee_id
        self.date_from = date_from
        self.date_to = date_to
        self.attendance_date = date_from.date()
        # Продолжительность явки
        self.duration: timedelta = self.date_to - self.date_from
        # Строка отражающая период явки
        self.attendance_string = f'{self.date_from.strftime("%H:%M")} - {self.date_to.strftime("%H:%M")}'


class AttendancesList:
    def __init__(self):
        self.attendances: dict[EmployeeId, dict[date, list[Attendance]]] = {}

    def __len__(self) -> int:
        """
        Возвращает количество явок в списке
        :return: Кол-во хранящихся явок.
            Возвращает 0, если список пуст.
        """
        _len = 0
        for employee_id in self.attendances:
            for date_ in self.attendances[employee_id]:
                _len += len(self.attendances[employee_id][date_])
        return _len

    def add_attendance(self, attendance: Attendance) -> None:
        if attendance.employee_id in self.attendances:
            if attendance.attendance_date in self.attendances[attendance.employee_id]:
                self.attendances[attendance.employee_id][attendance.attendance_date].append(attendance)
            else:
                self.attendances[attendance.employee_id][attendance.attendance_date] = [attendance]
        else:
            self.attendances[attendance.employee_id] = {attendance.attendance_date: [attendance]}

    def get_general_row_data(self, employee_id: EmployeeId):
        """
        Возвращает строку с агрегированными данными по всем явкам employee_id сохраненным в attendances

        :param employee_id: Идентификатор сотрудника
        :return:
        """
        employee_attendances = self.attendances[employee_id]

        employee_attendances_data = {
            "warnings": False,
            "full_shifts_count": 0,
            "half_shifts_count": 0,
            "total_shifts_count": 0,
            "total_duration_seconds": 0,
            "shifts": {},
        }

        for date_ in employee_attendances:
            duration_ = timedelta()
            if len(employee_attendances[date_]) > 1:
                employee_attendances_data["warnings"] = True
                for attendance_ in employee_attendances[date_]:
                    duration_ += attendance_.duration
            else:
                duration_ = employee_attendances[date_][0].duration

            # TODO: Вынести в настройки пороги длительности явки
            hours_duration = duration_.total_seconds() / 3600
            if hours_duration >= FULL_SHIFT_HOURS:
                employee_attendances_data["full_shifts_count"] += 1
                employee_attendances_data["total_duration_seconds"] += duration_.total_seconds()
                employee_attendances_data["shifts"].update({date_: ShiftType("full")})
            elif hours_duration >= HALF_SHIFT_HOURS:
                employee_attendances_data["half_shifts_count"] += 1
                employee_attendances_data["total_duration_seconds"] += duration_.total_seconds()
                employee_attendances_data["shifts"].update({date_: ShiftType("half")})
            else:
                employee_attendances_data["warnings"] = True
                employee_attendances_data["shifts"].update({date_: ShiftType("warning")})

        return employee_attendances_data

    def get_employee_detailed_data(self, employee_id: EmployeeId):
        return self.attendances[employee_id]


class AttendancesDataDriver:
    def __init__(self, general_table: QTableWidget):
        self.general_table: QTableWidget = general_table
        self.iiko_api = iiko_api
        self.api_attendances: list[dict] = []
        self.sales: dict[date, int] = {}
        self.employees_shifts: dict = {}
        self.employees_attendances: AttendancesList = AttendancesList()

    def update_data(self, date_from: datetime, date_to: datetime, department_code: str) -> None:
        """
        Получает данные по явкам за период.
        :param date_from: Дата начала периода
        :param date_to: Дата окончания периода
        :param department_code: Код отдела
        """
        logger.info(f"[update_data] Запущено обновление данных")

        if date_from <= date_to:
            with get_session() as session:
                department = get_department_by_code(session, department_code)

            self.api_attendances = self.iiko_api.employees.get_attendances_for_department(
                department_code=department_code,
                date_from=date_from,
                date_to=date_to
            )

            self.prepare_data()
            self.sales = self.iiko_api.reports.get_sales_report(
                date_from=date_from,
                date_to=date_to,
                department_id=department.id
            )
        else:
            raise ValueError("Дата начала периода больше даты окончания периода")
        logger.info(f"[update_data] Обновление данных завершено: \n  {self.api_attendances=}\n\n  {self.sales=}\n\n")

    def prepare_data(self) -> None:
        """
        Подготавливает данные для выгрузки в QTableWidget.
        """
        logger.info(f"Запущенна подготовка данных... \n  {self.api_attendances=}\n")
        self.employees_attendances = AttendancesList()
        for attendance in self.api_attendances:
            print(attendance)
            date_from = datetime.fromisoformat(attendance['personalDateFrom'])
            # Если у смены нет времени закрытия, то ставим время открытия(скорее всего это сегодняшняя смена)
            date_to = datetime.fromisoformat(attendance.get('personalDateTo', attendance['personalDateFrom']))
            employee_id = EmployeeId(attendance['employeeId'])
            # TODO: Вынести расписание в настройки
            # Если открыта в промежуток между 07:00 и 22:00
            if 7 <= date_from.hour <= 22:
                attendance_obj = Attendance(employee_id=employee_id, date_from=date_from, date_to=date_to)
                logger.debug(f"Условия по расписанию выполнены создана явка:"
                             f"\n  {employee_id=}\n  {date_from=}\n  {date_to=}\n  {attendance_obj=}")
                self.employees_attendances.add_attendance(attendance_obj)
                logger.debug(f"Явка {attendance_obj} добавлена в список явок, в нем {len(self.employees_attendances)} явок.")
        logger.debug(f"Подготовка явок окончена:\n"
                     f"  кол-во явок в списке:{len(self.employees_attendances)}\n  Явки{self.employees_attendances.attendances}\n\n")

    def calculate_salary(self, employee_id: EmployeeId, date_: date, shift_type: ShiftType) -> int:
        """
        Считает вознаграждение сотрудника по его мотивационной программе за определенную дату.
        :param employee_id: Id сотрудника
        :param date_: Дата
        :param shift_type: Тип смены: полный день или половина дня full | half
        :return: Вознаграждение
        """

        with get_session() as session:
            # Найти сотрудника и его мотивационную программу
            employee = session.query(Employee).filter(Employee.id == employee_id).first()

            if not employee or not employee.motivation_program:
                print(f"[calculate_salary]Сотрудник {employee_id} не найден или не имеет привязанных программ")
                return 0

            # Получить мотивационную программу
            motivation_program = employee.motivation_program
            print(f"[calculate_salary]Мотивационная программа {employee.name} (ID={employee.id})")

            # Извлечь выручку за заданную дату
            revenue = self.sales.get(date_, 0)
            print(f"[calculate_salary]Выручка за {date_}: {revenue}")

            # Найти соответствующий порог мотивации
            threshold: MotivationThreshold = session.query(MotivationThreshold).filter(
                MotivationThreshold.motivation_program_id == motivation_program.id,
                MotivationThreshold.revenue_threshold <= revenue
            ).order_by(MotivationThreshold.revenue_threshold.desc()).first()

            if threshold:
                print(f"Порог {threshold.revenue_threshold=} {threshold.salary=} {threshold.id=}")
                print(f"Выручка {revenue}")
                print(f"Смена {shift_type}")
                match shift_type:
                    case ShiftType.FULL:
                        print(f"Полная смена возвращаем {threshold.salary}")
                        return threshold.salary
                    case ShiftType.HALF:
                        print(f"Получаем половину {threshold.salary / 2}")
                        return int(threshold.salary / 2)

            return 0

    def get_general_table_rows(self) -> list[dict]:
        """
        Возвращает список словарей с данными для вывода в сводную таблицу зарплаты(QTableWidget).
        """
        rows = []
        for employee_id in self.employees_attendances.attendances:
            # TODO: Получать сотрудников из внутренней базы данных
            employee_ = iiko_api.employees.get_employee_by_id(employee_id)

            if not employee_:
                # TODO: Перехватить в интерфейсе и выбросить окно
                raise ValueError(f"Сотрудник {employee_id} не найден")

            if not employee_.get('departmentCodes', None):
                # Если сотрудник не имеет департаментов(служебные аккаунты и менеджеры) пропускаем
                continue

            if not employee_.get('mainRoleId', None):
                # Если сотрудник не имеет роли в iiko пропускаем
                # Подразумевается что всем кому считаем зп выделены роли в iiko
                continue

            with get_session() as session:
                departments = [
                    get_department_by_code(session, department_code).name for department_code in
                    employee_['departmentCodes']]

                motivation_program = session.query(MotivationProgram).filter(
                    MotivationProgram.employees.any(Employee.id == employee_id)
                ).one_or_none()

                if not motivation_program:
                    # Если нет программы мотивации, то пропускаем
                    continue

            employee_attendances_data = self.employees_attendances.get_general_row_data(employee_id)

            total_salary = 0

            # TODO: Возможно стоит перенести
            self.employees_shifts[employee_.get("id")] = employee_attendances_data['shifts'].copy()

            for date_, shift_type in employee_attendances_data['shifts'].items():

                if date_ in self.sales:
                    salary_ = self.calculate_salary(employee_id, date_, shift_type)
                    print(f"ЗП за {date_}: {salary_}")
                else:
                    print(f"{type(date_)=}")
                    print(f"{self.sales}")
                    # TODO: Обработать это исключение в ui - выбросить окно
                    raise ValueError(f"Дата {date_} не найдена в отчете о продажах")
                total_salary += salary_

            first_name = employee_.get('firstName', " ")
            last_name = employee_.get('lastName', " ")

            employee_attendances_data.update({
                "name": employee_['name'],
                "full_name": first_name + ' ' + last_name,
                "role": self.iiko_api.roles.get_role_by_id(employee_['mainRoleId'])['name'],
                "code": employee_['code'],
                "departments": " ".join(departments),
                "id": employee_id,
                "salary": total_salary,
            })
            rows.append(employee_attendances_data)
        return rows

    def render_general_table(self) -> None:
        """
        Выводит данные сводного отчета по зарплате в таблицу.
        """
        rows = self.get_general_table_rows()
        self.general_table.setRowCount(0)
        self.general_table.setRowCount(len(rows))
        self.general_table.setColumnCount(9)

        for row_index, row_data in enumerate(rows):

            self.general_table.setItem(row_index, 0, QTableWidgetItem(str(row_data['name'])))
            self.general_table.setItem(row_index, 1, QTableWidgetItem(str(row_data['full_name'])))
            self.general_table.setItem(row_index, 2, QTableWidgetItem(str(row_data['salary'])))
            self.general_table.setItem(row_index, 3, QTableWidgetItem(str(row_data['full_shifts_count'])))
            self.general_table.setItem(row_index, 4, QTableWidgetItem(str(row_data['half_shifts_count'])))
            self.general_table.setItem(row_index, 5, QTableWidgetItem(str(row_data['role'])))
            self.general_table.setItem(row_index, 6, QTableWidgetItem(str(row_data['departments'])))
            self.general_table.setItem(row_index, 7, QTableWidgetItem(str(row_data['code'])))
            self.general_table.setItem(row_index, 8, QTableWidgetItem(str(row_data['id'])))

            if row_data['warnings']:  # Если есть предупреждение
                for col_index in range(self.general_table.columnCount()):
                    # Окрашиваем строку в красный цвет
                    self.general_table.item(row_index, col_index).setBackground(QColor(255, 10, 10, 80))

        self.general_table.resizeColumnsToContents()
        self.general_table.resizeRowsToContents()

        self.general_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.general_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.general_table.itemDoubleClicked.connect(self.on_general_table_double_clicked)

    def on_general_table_double_clicked(self, item: QTableWidgetItem) -> None:
        """
        Вызывается при двойном клике на строке таблицы с общей информацией о зарплате.
        """
        employee_id = self.general_table.item(item.row(), 8).text()
        employee_name = self.general_table.item(item.row(), 0).text()
        self.render_detailed_table(
            parent=self.general_table,
            employee_id=employee_id,
            employee_name=employee_name
        )

    def get_shift_type(self, employee_id: EmployeeId, date_: date) -> ShiftType:
        """
        Возвращает тип смены для сотрудника на заданную дату: full | half
        :param employee_id: Id сотрудника
        :param date_: Дата явки
        :return: Тип смены
        """
        return ShiftType(self.employees_shifts[employee_id][date_])

    def get_detailed_table_rows(self, employee_id: str) -> list:
        """
        Возвращает список словарей с данными для вывода в таблицу с подробной информацией о зарплате.
        """
        rows = []
        employee_id = EmployeeId(employee_id)
        employee_attendances_data = self.employees_attendances.get_employee_detailed_data(employee_id)

        for date_, employee_attendance in employee_attendances_data.items():
            warning = False

            if len(employee_attendance) > 1:
                warning = True
                period = [attendance.attendance_string for attendance in employee_attendance]
                period = "\n".join(period)
            else:
                period = employee_attendance[0].attendance_string
            print("================================")
            print(date_)
            print(self.employees_shifts[employee_id])
            print("================================")

            shift_type = self.get_shift_type(employee_id, date_)
            salary = self.calculate_salary(employee_id, date_, shift_type)

            rows.append({
                "date": date_,
                "shift_type": str(shift_type),
                "period": period,
                "salary": salary,
                "warning": warning,
            })
        return rows

    def render_detailed_table(self, parent, employee_id: str, employee_name: str) -> None:
        """
        Выводит данные подробного отчета по зарплате в таблицу.
        """
        rows = self.get_detailed_table_rows(employee_id)
        # Создаем всплывающее окно с таблицей
        self.detailed_table = QTableWidget()
        self.detailed_table.setRowCount(len(rows))
        self.detailed_table.setColumnCount(4)
        self.detailed_table.setHorizontalHeaderLabels(["Дата", "Смена", "Период", "Зарплата"])

        for row, row_data in enumerate(rows):
            self.detailed_table.setItem(row, 0, QTableWidgetItem(str(row_data['date'])))
            self.detailed_table.setItem(row, 1, QTableWidgetItem(str(row_data['shift_type'])))
            self.detailed_table.setItem(row, 2, QTableWidgetItem(str(row_data['period'])))
            self.detailed_table.setItem(row, 3, QTableWidgetItem(str(row_data['salary'])))
            if row_data['warning']:
                for column in range(self.detailed_table.columnCount()):
                    self.detailed_table.item(row, column).setBackground(QColor(255, 10, 10, 80))

        self.detailed_table.resizeColumnsToContents()
        self.detailed_table.resizeRowsToContents()
        self.detailed_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.detailed_table.verticalHeader().setHidden(True)
        self.detailed_table.setWindowTitle(f"{employee_name} - Детализация")
        self.detailed_table.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.detailed_table.setStyleSheet("""
                    background-color: rgba(255, 255, 255, 30);
                    border-radius: 7px;
                    
                    QTableWidget {
                            gridline-color: rgba(255, 255, 255, 70);
                        };
                    
                    QHeaderView::section {
                            padding: 3px;  
                        };
                    
                    color: white;
        """)
        # Устанавливаем размер окна по размеру таблицы
        self.detailed_table.resize(self.detailed_table.size())
        self.detailed_table.show()


