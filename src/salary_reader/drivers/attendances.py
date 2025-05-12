import enum
from datetime import datetime, date, timedelta
from typing import AnyStr, Union
from uuid import UUID

from PySide6.QtGui import QColor, Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView

from salary_reader.core.database import get_session
from salary_reader.core.models import MotivationProgram, MotivationThreshold, Employee
from salary_reader.core.control_models import get_department_by_code
from salary_reader.iiko_init import iiko_api
from salary_reader.core.logging_config import get_logger

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
    """
    Класс, представляющий собой явку сотрудника.

    Атрибуты класса:

    :var employee_id: Идентификатор сотрудника.
    :var date_from Дата и время начала явки.
    :var date_to Дата и время окончания явки.
    :var attendance_date Дата явки.
    :var duration Продолжительность явки.
    :var attendance_string Строковое представление явки.
    """

    def __init__(self, employee_id: EmployeeId, date_from: datetime, date_to: datetime):
        self.employee_id = employee_id

        # Если явка закрыта после 22 часов, то устанавливается 22 часа.(чтобы не учитывать время после смены)
        if date_to.hour > 22 or (date_to.hour == 22 and date_to.minute > 0):
            logger.warning(
                f"Время окончания явки сотрудника {employee_id} на {date_to.strftime('%d.%m.%Y')} больше 22:00. "
                f"Устанавливаем 22 часа."
            )
            self.date_to = date_to.replace(hour=22, minute=0, second=0, microsecond=0)
        else:
            logger.info(
                f"Время окончания явки сотрудника {employee_id} на {date_to.strftime('%d.%m.%Y')} меньше 22:00.")
            self.date_to = date_to

        if date_from.hour < 10 or (date_from.hour == 10 and date_from.minute < 20):
            logger.warning(
                f"Время явки сотрудника {employee_id} на {date_from.strftime('%d.%m.%Y')} меньше 10:00."
                f"Устанавливаем 10 часов."
            )
            self.date_from = date_from.replace(hour=10, minute=0, second=0, microsecond=0)
        else:
            logger.info(f"Время явки сотрудника {employee_id} на {date_from.strftime('%d.%m.%Y')} больше 10:00.")
            self.date_from = date_from

        self.attendance_date = date_from.date()
        # Продолжительность явки
        if date_from.date() == date_to.date():
            if self.date_from.hour < 22:
                self.duration: timedelta = self.date_to - self.date_from
            else:  # Если смена открыта после 22 часов, то продолжительность явки будет 0 часов.
                self.duration = timedelta(hours=0)
        else:
            error_msg = f"Явка сотрудника {employee_id} на {date_from.strftime('%d.%m.%Y')} больше одного дня."
            logger.exception(error_msg)
            self.duration = timedelta(hours=0)

        # Округление длительности явки до 30 минут(если остаток больше 15 минут, то округляем до 30 минут)
        minutes = self.duration.total_seconds() / 60
        rounded_minutes = round(minutes / 30) * 30
        self.duration = timedelta(minutes=rounded_minutes)

        # Строка отражающая период явки
        self.attendance_string = f'{self.date_from.strftime("%H:%M")} - {self.date_to.strftime("%H:%M")}'

        if (self.duration > timedelta(hours=6)) and (self.date_to.hour > 20):

            self.is_taxi_paid = True
        else:
            self.is_taxi_paid = False

    def __str__(self):
        return f'Явка сотрудника {self.employee_id}: {self.attendance_string}'


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
        Возвращает строку таблицы с агрегированными данными по всем явкам employee_id сохраненным в attendances

        :param employee_id: Идентификатор сотрудника
        :return:
        """
        employee_attendances = self.attendances[employee_id]

        employee_attendances_data = {
            "warnings": False,
            "full_shifts_count": 0,
            "full_shifts_count_from_1": 0,
            "full_shifts_count_from_16": 0,
            "half_shifts_count": 0,
            "half_shifts_count_from_1": 0,
            "half_shifts_count_from_16": 0,
            "total_shifts_count": 0,
            "total_shifts_count_from_1": 0,
            "total_shifts_count_from_16": 0,
            "total_duration_seconds": 0,
            "shifts": {},
            "taxi_paid_count": 0,
            "taxi_paid_sum": 0
        }

        for date_ in employee_attendances:
            duration_ = timedelta()
            is_taxi_paid = False
            if len(employee_attendances[date_]) > 1:
                employee_attendances_data["warnings"] = True
                for attendance_ in employee_attendances[date_]:
                    duration_ += attendance_.duration
                    if attendance_.is_taxi_paid:
                        is_taxi_paid = True
            else:
                duration_ = employee_attendances[date_][0].duration
                if employee_attendances[date_][0].is_taxi_paid:
                    is_taxi_paid = True

            # TODO: Вынести в настройки пороги длительности явки
            hours_duration = duration_.total_seconds() / 3600

            employee_attendances_data["total_duration_seconds"] += duration_.total_seconds()

            if is_taxi_paid:
                employee_attendances_data["taxi_paid_count"] += 1
                employee_attendances_data["taxi_paid_sum"] += 150

            if hours_duration >= FULL_SHIFT_HOURS:
                if 1 <= date_.day <= 15:
                    employee_attendances_data["full_shifts_count_from_1"] += 1
                elif 16 <= date_.day <= 31:
                    employee_attendances_data["full_shifts_count_from_16"] += 1
                employee_attendances_data["full_shifts_count"] += 1
                employee_attendances_data["shifts"].update({
                    date_: {"shift_type": ShiftType("full"),
                            "hours_duration": hours_duration,
                            }
                })
            elif hours_duration >= HALF_SHIFT_HOURS:
                if 1 <= date_.day <= 15:
                    employee_attendances_data["half_shifts_count_from_1"] += 1
                elif 16 <= date_.day <= 31:
                    employee_attendances_data["half_shifts_count_from_16"] += 1
                employee_attendances_data["half_shifts_count"] += 1
                employee_attendances_data["shifts"].update({
                    date_: {"shift_type": ShiftType("half"),
                            "hours_duration": hours_duration,
                            }
                })
            else:
                employee_attendances_data["warnings"] = True
                employee_attendances_data["shifts"].update({
                    date_: {"shift_type": ShiftType("warning"),
                            "hours_duration": hours_duration,
                            }
                })

        return employee_attendances_data

    def get_employee_detailed_data(self, employee_id: EmployeeId) -> dict[date, list[Attendance]]:
        """
        Возвращает данные по явкам сотрудника
        :param employee_id: Идентификатор сотрудника в iiko
        :return: Словарь с датами и явками в эти даты
        """
        logger.info(f"Получение данных по явкам сотрудника {employee_id}")
        logger.info(f"{self.attendances=}")
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
        # Пересоздаем список явок, чтобы отчистить от старых данных
        self.employees_attendances = AttendancesList()
        for attendance in self.api_attendances:
            employee_id = EmployeeId(attendance['employeeId'])
            # TODO: Дублирование кода, исправить, скорее всего можно просто удалить его повтор далее
            with get_session() as session:
                # Найти сотрудника и его мотивационную программу
                employee = session.query(Employee).filter(Employee.id == employee_id).first()
                if not employee:
                    logger.warning(f"Сотрудник с ID={employee_id} не найден в базе данных")
                    continue

                if not employee.motivation_program:
                    logger.warning(f"Сотрудник {employee.name} (ID={employee.id}) не имеет привязанных программ"
                                   f"Не добавляем его в список отчищенных явок")
                    continue

            logger.debug(f"Обработка явки:\n  {attendance=}")
            date_from = datetime.fromisoformat(attendance['dateFrom'])
            # Если у смены нет времени закрытия, то ставим время открытия(скорее всего это сегодняшняя смена)
            date_to = datetime.fromisoformat(attendance.get('dateTo', attendance['dateFrom']))
            # TODO: Вынести расписание в настройки
            # Если открыта в промежуток между 07:00 и 22:00
            if 7 <= date_from.hour <= 22:
                attendance_obj = Attendance(employee_id=employee_id, date_from=date_from, date_to=date_to)
                logger.debug(f"Условия по расписанию выполнены создана явка:"
                             f"\n  {employee_id=}\n  {date_from=}\n  {date_to=}\n  {attendance_obj=}")
                self.employees_attendances.add_attendance(attendance_obj)
                logger.debug(f"Явка {attendance_obj} добавлена в список явок,"
                             f" в нем {len(self.employees_attendances)} явок.")
            else:
                logger.debug(f"Условия по расписанию НЕ выполнены, явка НЕ создана:\n"
                             f"  {employee_id=}\n  {date_from=}\n  {date_to=}")

        logger.debug(f"Подготовка явок окончена:\n"
                     f"  кол-во явок в списке:{len(self.employees_attendances)}\n"
                     f"  Явки{self.employees_attendances.attendances}\n\n")

    def calculate_salary(
            self, employee_id: EmployeeId,
            date_: date,
            shift_type: ShiftType,
            duration_seconds: int = None,
            per_hour: bool = False
    ) -> int:
        """
        Считает вознаграждение сотрудника по его мотивационной программе за определенную дату.

        :param duration_seconds: Продолжительность явки в секундах
        :param per_hour: Почасовой расчет вознаграждения, если включен, то расчет происходит по часам работы сотрудника
        :param employee_id: Id сотрудника
        :param date_: Дата
        :param shift_type: Тип смены: полный день или половина дня full | half
        :return: Вознаграждение
        """

        with get_session() as session:
            # Найти сотрудника и его мотивационную программу
            employee = session.query(Employee).filter(Employee.id == employee_id).first()

            if not employee:
                logger.warning(f"Сотрудник с id={employee_id} не найден")
                return 0  # TODO: Почему возвращаем 0?

            if not employee.motivation_program:
                logger.warning(f"Сотрудник {employee.name} (ID={employee.id}) не имеет привязанных программ")
                return 0  # TODO: Почему возвращаем 0?

            # Получить мотивационную программу
            motivation_program = employee.motivation_program
            logger.debug(f"Мотивационная программа {employee.name} (ID={employee.id}): "
                         f"{motivation_program.name} (ID={motivation_program.id})")

            # Извлечь выручку за заданную дату
            revenue = self.sales.get(date_, 0)
            logger.debug(f"Выручка за {date_}: {revenue}")

            # Найти соответствующий порог мотивации
            threshold: MotivationThreshold = session.query(MotivationThreshold).filter(
                MotivationThreshold.motivation_program_id == motivation_program.id,
                MotivationThreshold.revenue_threshold <= revenue
            ).order_by(MotivationThreshold.revenue_threshold.desc()).first()

            if threshold:
                logger.debug(f"Порог при данной выручке для данной программы: "
                             f"{threshold.revenue_threshold=} {threshold.salary=} {threshold.id=}")

                logger.debug(f"Тип смены: {shift_type}")
                if duration_seconds > 12 * 3600:
                    duration_seconds = 12 * 3600
                if per_hour:
                    if duration_seconds > 0:
                        duration_hours = duration_seconds / 3600
                        return int(threshold.salary / 12 * duration_hours)
                    else:
                        return 0
                else:
                    match shift_type:
                        case ShiftType.FULL:
                            logger.debug(f"Полная смена возвращаем: {threshold.salary}")
                            return threshold.salary
                        case ShiftType.HALF:
                            logger.debug(f"Пол смены получаем половину: {threshold.salary / 2}")
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
                logger.warning(f"Сотрудник {employee_id} не имеет департаментов")
                continue

            if not employee_.get('mainRoleId', None):
                # Если сотрудник не имеет роли в iiko пропускаем
                # Подразумевается что всем кому считаем зп выделены роли в iiko
                logger.warning(f"Сотрудник {employee_.get('name', 'Не удалось получить имя')}"
                               f" (ID={employee_id}) не имеет роли в iiko")
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
                    logger.warning(f"Сотрудник {employee_.get('name', 'Не удалось получить имя')}"
                                   f" (ID={employee_id}) не имеет привязанных программ мотивации")
                    continue

            employee_attendances_data = self.employees_attendances.get_general_row_data(employee_id)
            logger.debug(f"Данные по явкам сотрудника {employee_.get('name', 'Не удалось получить имя')}"
                         f" (ID={employee_id}): {employee_attendances_data}")

            total_salary = 0
            from_1_total_salary = 0
            from_16_total_salary = 0

            # TODO: Возможно стоит перенести
            self.employees_shifts[employee_.get("id")] = employee_attendances_data['shifts'].copy()
            for date_, data in employee_attendances_data['shifts'].items():

                shift_type = data['shift_type']
                hours_duration = data['hours_duration']
                if date_ in self.sales:
                    salary_ = self.calculate_salary(
                        employee_id,
                        date_,
                        shift_type,
                        per_hour=True,
                        duration_seconds=hours_duration * 3600
                    )
                    logger.debug(f"ЗП за {date_}: {salary_} продолжительность: {hours_duration}")
                else:
                    logger.warning(f"Дата {date_} не найдена в отчете о продажах")
                    logger.debug(f"Тип переменной даты: {type(date_)=}")
                    logger.debug(f"Словарь в котором ищем дату:{self.sales}")
                    # TODO: Создать кастомное исключение для этого и обработать это исключение в ui - выбросить окно
                    raise ValueError(f"Дата {date_} не найдена в отчете о продажах")
                total_salary += salary_
                if 1 <= date_.day <= 15:
                    from_1_total_salary += salary_
                elif 16 <= date_.day <= 31:
                    from_16_total_salary += salary_

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
                "from_1_salary": from_1_total_salary,
                "from_16_salary": from_16_total_salary,

            })
            rows.append(employee_attendances_data)
        return rows

    def render_general_table(self) -> None:
        """
        Выводит данные сводного отчета по зарплате в таблицу.
        """
        try:
            rows = self.get_general_table_rows()
        except Exception as err:
            logger.exception(f"Произошла ошибка при получении данных для сводной таблицы:\n{err}")
            raise err

        self.general_table.setRowCount(0)
        self.general_table.setRowCount(len(rows))
        self.general_table.setColumnCount(19)

        for row_index, row_data in enumerate(rows):

            self.general_table.setItem(row_index, 0, QTableWidgetItem(str(row_data['name'])))
            self.general_table.setItem(row_index, 1, QTableWidgetItem(str(row_data['full_name'])))
            self.general_table.setItem(row_index, 2, QTableWidgetItem(str(row_data['from_1_salary'])))
            self.general_table.setItem(row_index, 3, QTableWidgetItem(str(row_data['full_shifts_count_from_1'])))
            self.general_table.setItem(row_index, 4, QTableWidgetItem(str(row_data['half_shifts_count_from_1'])))
            self.general_table.setItem(row_index, 5, QTableWidgetItem(str(row_data['from_16_salary'])))
            self.general_table.setItem(row_index, 6, QTableWidgetItem(str(row_data['full_shifts_count_from_16'])))
            self.general_table.setItem(row_index, 7, QTableWidgetItem(str(row_data['half_shifts_count_from_16'])))
            self.general_table.setItem(row_index, 8, QTableWidgetItem(str(row_data['salary'])))
            self.general_table.setItem(row_index, 9, QTableWidgetItem(str(row_data['full_shifts_count'])))
            self.general_table.setItem(row_index, 10, QTableWidgetItem(str(row_data['half_shifts_count'])))
            self.general_table.setItem(row_index, 11, QTableWidgetItem(str(row_data['taxi_paid_count'])))
            self.general_table.setItem(row_index, 12, QTableWidgetItem(str(row_data['taxi_paid_sum'])))
            self.general_table.setItem(row_index, 13, QTableWidgetItem(str(row_data['role'])))
            self.general_table.setItem(row_index, 14, QTableWidgetItem(str(row_data['departments'])))
            self.general_table.setItem(row_index, 15, QTableWidgetItem(str(row_data['code'])))
            self.general_table.setItem(row_index, 16, QTableWidgetItem(str(row_data['id'])))
            self.general_table.setItem(row_index, 17, QTableWidgetItem('0'))
            self.general_table.setItem(row_index, 18, QTableWidgetItem('0'))

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
        employee_id = self.general_table.item(item.row(), 16).text()
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
        return ShiftType(self.employees_shifts[employee_id][date_]["shift_type"])

    def get_detailed_table_rows(self, employee_id: str) -> list:
        """
        Возвращает список словарей с данными для вывода в таблицу с подробной информацией о зарплате.
        """
        rows = []
        employee_id = EmployeeId(employee_id)
        employee_attendances_data = self.employees_attendances.get_employee_detailed_data(employee_id)

        logger.debug(f"Смены сотрудника {employee_id}:\n  {self.employees_shifts[employee_id]}")

        is_taxi_paid = False

        for date_, employee_attendance in employee_attendances_data.items():
            warning = False
            logger.debug(f"Обрабатываем дату {date_}")
            # Если количество явок за дату date_ больше 1
            if len(employee_attendance) > 1:
                is_taxi_paid = "?"
                logger.debug(f"Обнаружено больше одной явки у {employee_id} за дату: {date_}")
                warning = True
                period = [attendance.attendance_string for attendance in employee_attendance]
                period = "\n".join(period)
                logger.debug(f"Строка периода явок сформирована: {period}")
                attendance_duration = sum([attendance.duration.total_seconds() for attendance in employee_attendance])
            else:
                is_taxi_paid = employee_attendance[0].is_taxi_paid
                period = employee_attendance[0].attendance_string
                attendance_duration = employee_attendance[0].duration.total_seconds()

            shift_type = self.get_shift_type(employee_id, date_)
            salary = self.calculate_salary(
                employee_id,
                date_,
                shift_type,
                per_hour=True,
                duration_seconds=attendance_duration
            )

            rows.append({
                "date": date_,
                "shift_type": str(shift_type),
                "period": period,
                "salary": salary,
                "is_taxi_paid": is_taxi_paid,
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
        self.detailed_table.setColumnCount(5)
        self.detailed_table.setHorizontalHeaderLabels(["Дата", "Смена", "Период", "Зарплата", "Такси"])

        for row, row_data in enumerate(rows):
            logger.debug(f"Такси оплачено: {row_data['is_taxi_paid']}")
            if row_data['is_taxi_paid']:
                if row_data['is_taxi_paid'] == "?":
                    self.detailed_table.setItem(row, 4, QTableWidgetItem("?"))
                else:
                    self.detailed_table.setItem(row, 4, QTableWidgetItem("150"))
            else:
                self.detailed_table.setItem(row, 4, QTableWidgetItem("0"))

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
