from typing import Type

from sqlalchemy.orm import Session

from ..core.models import Employee, Department
from salary_reader.helpers.iiko_helpers import normalize_department_codes
from salary_reader.iiko_init import iiko_api, safe_iiko_auth
from salary_reader.core.logging_config import get_logger

logger = get_logger(__name__, level="DEBUG")


def update_employees_from_api(session: Session):
    try:
        if iiko_api is None:
            logger.warning("iiko_api не инициализирован, пропускаем обновление сотрудников")
            return
            
        logger.info(f"Обновление сотрудников...")

        existing_employees: list[Type[Employee]] = (
            session.query(Employee)
            .all()
        )

        logger.debug(f"Существующие сотрудники: {existing_employees}")
        existing_employees_dict = {emp.id: emp for emp in existing_employees}

        with safe_iiko_auth():
            logger.debug("Получение ролей iiko")
            roles = iiko_api.roles.get_roles()
            roles_name_dict = {role["id"]: role["name"] for role in roles}
            logger.debug(f"Роили iiko получены {roles_name_dict}")

            logger.debug("Получение сотрудников из iiko...")
            api_employees_raw = iiko_api.employees.get_employees()
            if isinstance(api_employees_raw, dict):
                api_employees = [api_employees_raw]
            else:
                api_employees = api_employees_raw or []
            logger.debug(f"Сотрудники получены из iiko:\n  {api_employees}\n")

        for employee_data in api_employees:
            department_codes = normalize_department_codes(employee_data.get("departmentCodes"))
            if not department_codes:
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
