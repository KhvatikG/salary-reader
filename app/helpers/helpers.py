from sqlalchemy.orm import Session
from typing import Dict, Any

from app.models import Employee, Department, MotivationProgram


def save_employee(session: Session, employee_data: Dict[str, Any]) -> None:
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


def assign_motivation_program(session: Session, employee_id: int, motivation_program_id: int) -> None:
    """
    Назначает мотивационную программу сотруднику.

    :param session: SQLAlchemy сессия для взаимодействия с базой данных.
    :param employee_id: ID сотрудника, которому нужно назначить мотивационную программу.
    :param motivation_program_id: ID мотивационной программы, которую нужно назначить.
    """
    # Получаем сотрудника по ID
    employee = session.query(Employee).filter_by(id=employee_id).first()
    if not employee:
        raise ValueError("Сотрудник с указанным ID не найден.")

    # Получаем мотивационную программу по ID
    motivation_program = session.query(MotivationProgram).filter_by(motivation_id=motivation_program_id).first()
    if not motivation_program:
        raise ValueError("Мотивационная программа с указанным ID не найдена.")

    # Назначаем мотивационную программу сотруднику
    employee.motivation_program = motivation_program

    # Сохраняем изменения
    session.commit()