"""
Модуль для методов работы с моделями
"""

# TODO: Необходимо привести к виду в котором сессия создается либо только в функциях
#  либо тольок принимается ими
#  (Полагаю лучше сделать так чтобы все функции в этом модуле принимали объект сессии)
#  иначе возникают конфликты, когда сессия создается над функцией и повторно в ней
from typing import Any, Type

from sqlalchemy.orm import Session

from loguru import logger
from .database import get_session
from .models import Employee, Department, MotivationProgram
from salary_reader.iiko_init import iiko_api


def save_employee(session: Session, employee_data: dict[str, Any]) -> None:
    """
    Сохраняет объект Employee вместе с его департаментами.

    :param session: SQLAlchemy сессия для взаимодействия с базой данных.
    :param employee_data: Данные сотрудника, содержащие ID, имя и список департаментов.
    """
    # Получаем или создаем объект Employee
    employee = session.query(Employee).filter_by(id=employee_data['id']).first()
    if not employee:
        employee = Employee(id=employee_data['id'])

    # Обновляем атрибуты Employee
    employee.name = employee_data['name']

    # Очистка предыдущих связей с департаментами
    employee.departments.clear()

    # Присваиваем департаменты
    department_codes = employee_data.get('department_code', [])
    for dept_code in department_codes:
        department = session.query(Department).filter_by(code=dept_code).first()
        if department:
            employee.departments.append(department)

    # Добавляем или обновляем объект в сессии
    session.add(employee)

    # Сохраняем изменения
    session.commit()


def assign_motivation_program(session: Session, employee_id: str, motivation_program_id: str | None) -> None:
    """
    Назначает мотивационную программу сотруднику.

    :param session: SQLAlchemy сессия для взаимодействия с базой данных.
    :param employee_id: ID сотрудника, которому нужно назначить мотивационную программу.
    :param motivation_program_id: ID мотивационной программы, которую нужно назначить.
        Если None, то отвязывает мотивационную программу.
    """
    # Получаем сотрудника по ID
    employee = session.query(Employee).filter_by(id=employee_id).first()
    if not employee:
        raise ValueError("Сотрудник с указанным ID не найден.")

    if motivation_program_id is None:
        # Открепляем мотивационную программу
        employee.motivation_program = None
    else:
        # Получаем мотивационную программу по ID
        motivation_program = session.query(MotivationProgram).filter_by(id=motivation_program_id).first()
        if not motivation_program:
            raise ValueError("Мотивационная программа с указанным ID не найдена.")

        # Назначаем мотивационную программу сотруднику
        employee.motivation_program = motivation_program


def delete_motivation_program(role_id):
    """
    Удаляет программу мотивации и все связанные с ней пороги.
    Поднимает исключение, если программа не найдена.
    :param role_id: id программы мотивации.
    """
    # Находим существующую программу мотивации
    with get_session() as session:
        motivation_program = session.query(
            MotivationProgram).filter_by(id=role_id).one_or_none()

        if motivation_program:
            try:
                # Удаляем связь сотрудников с этой программой
                for employee in motivation_program.employees:
                    employee.motivation_program = None

                # Удаляем саму программу мотивации (это также удалит связанные пороги)
                session.delete(motivation_program)

                # Подтверждаем изменения
                session.commit()
            except Exception as e:
                logger.error(f"Ошибка удаления программы мотивации: {e}")
                raise f"Ошибка удаления программы мотивации:\n {e}"

        else:
            logger.error(f"Мотивационная программа не найдена")
            raise "Мотивационная программа не найдена"


def get_current_roles_by_department_code(department_code: str) -> list[MotivationProgram]:
    """
    Возвращает список ролей, привязанных к данному отделу.
    :param department_code: Код отдела, для которого нужно получить список ролей.
    :return: Список ролей, привязанных к данному отделу.
    """
    with get_session() as session:
        roles = session.query(
            MotivationProgram).join(Department).filter(Department.code == department_code).all()

    return roles


def thresholds_clear(program: MotivationProgram, session: Session):
    """
    Удаляет пороги мотивации для указанной программы.
    :param program: Программа мотивации, для которой нужно удалить пороги.
    """
    for threshold in program.thresholds:
        session.delete(threshold)
    session.commit()


def get_employees_by_motivation_program_id(session: Session, motivation_program_id: int) -> list[Type[Employee]]:
    """
    Возвращает список сотрудников, привязанных к указанной программе мотивации.
    :param session: Сессия SQLAlchemy.
    :param motivation_program_id: ID программы мотивации.
    """
    employees = session.query(Employee).join(MotivationProgram).filter(
        MotivationProgram.id == motivation_program_id).all()

    return employees


def get_department_by_code(session: Session, department_code: str) -> Type[Department]:
    """
    Возвращает отдел по его ID.

    :param session: Session SQLAlchemy.
    :param department_code: Код отдела.
    :return: Отдел.(Department)
    """
    return session.query(Department).filter_by(code=department_code).one_or_none()


def get_employee_name_by_id(employee_id: str) -> str:
    """
    Возвращает имя сотрудника по его ID, из iiko,
    позже реализую из внутренней БД.

    :param session: Session SQLAlchemy.
    :param employee_id: ID сотрудника.
    :return: Полное имя сотрудника.
    """
    # TODO: Получать из внутренней БД
    if iiko_api is None:
        return f"Сотрудник {employee_id} (iiko_api недоступен)"
        
    employee = iiko_api.employees.get_employee_by_id(employee_id)
    if employee:
        system_name = employee.get("name", "Не задано")
        tabel = employee.get("code", "Не задан")
        first_name = employee.get("firstName", f"Имя не задано в iiko (Системное имя: {system_name})")
        last_name = employee.get("lastName", f"Фамилия не задано в iiko (Табель: {tabel})")
        full_name = first_name + " " + last_name
        return full_name
    else:
        # TODO: Добавить исключение
        logger.error(f"Сотрудник с ID {employee_id} не найден")
        return ""
