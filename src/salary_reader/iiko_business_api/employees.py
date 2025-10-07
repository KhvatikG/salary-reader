from typing import Type

from sqlalchemy.orm import Session

from ..core.models import Employee, Department
from salary_reader.iiko_init import iiko_api
from salary_reader.core.logging_config import get_logger

logger = get_logger(__name__, level="DEBUG")


def update_employees_from_api(session: Session):
    try:
        logger.info(f"Обновление сотрудников...")

        existing_employees: list[Type[Employee]] = (
            session.query(Employee)
            .all()
        )

        logger.debug(f"Существующие сотрудники: {existing_employees}")
        existing_employees_dict = {emp.id: emp for emp in existing_employees}

        with iiko_api.auth_context():
            logger.debug(f"Получение ролей iiko")
            roles = iiko_api.roles.get_roles()
            roles_name_dict = {role["id"]: role["name"] for role in roles}
            logger.debug(f"Роили iiko получены {roles_name_dict}")

        logger.debug(f"Получение сотрудников из iiko...")
        api_employees: list[dict] = iiko_api.employees.get_employees()
        logger.debug(f"Сотрудники получены из iiko:\n  {api_employees}\n")

        for employee_data in api_employees:
            if not employee_data.get("departmentCodes"):
                logger.debug(f"Сотрудник {employee_data} не имеет отдела(скорее всего служебный аккаунт) -> пропускаем")
                continue
            if not employee_data.get("code"):
                logger.debug(
                    f"Сотрудник {employee_data} не имеет табельного(скорее всего служебный аккаунт) -> пропускаем")
                continue
            logger.debug(f"Обработка сотрудника {employee_data}")
            employee_id: str = employee_data.get("id")

            if employee_id in existing_employees_dict:
                logger.debug(f"Сотрудник обнаружен -> обновление существующего сотрудника {employee_data}...")
                existing_employee: Type[Employee] = existing_employees_dict.pop(employee_id)
                existing_employee.name = employee_data.get("name")
                existing_employee.position = roles_name_dict.get(employee_data.get("mainRoleId"))
                existing_employee.code = employee_data.get("code")

                department_codes = employee_data.get("departmentCodes")
                new_departments: list[Type[Department]] = []

                for department_code in department_codes:
                    department = session.query(Department).filter_by(code=department_code).first()
                    if department:
                        new_departments.append(department)
                logger.debug(
                    f"Обновление отделов сотрудника {employee_data}\n {existing_employee.departments}\n->\n {new_departments}\n")
                existing_employee.departments = new_departments

                logger.debug(f"Обновление существующего сотрудника {existing_employee} завершено")

            elif employee_id:
                logger.debug(f"Сотрудник не обнаружен -> создание нового сотрудника {employee_data}...")
                employee = Employee(
                    id=employee_id,
                    name=employee_data.get("name"),
                    position=roles_name_dict.get(employee_data.get("mainRoleId")),
                    code=employee_data.get("code"),
                )

                department_codes = employee_data.get("departmentCodes")
                for department_code in department_codes:
                    department = session.query(Department).filter_by(code=department_code).first()
                    if department:
                        employee.departments.append(department)

                session.add(employee)
                logger.debug(f"Создание нового сотрудника {employee} завершено")

        for employee in existing_employees_dict.values():
            logger.debug(f"Удаление сотрудника {employee}...")
            session.delete(employee)
            logger.debug(f"Удаление сотрудника {employee} завершено")

        logger.info(f" Обновление сотрудников завершено")
    except Exception as e:
        logger.error(f"Ошибка обновления сотрудников: {e}\n"
                     f"{e.with_traceback(e.__traceback__)}")
        raise e
