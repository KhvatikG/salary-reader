from sqlalchemy.orm import Session

from app.models import Employee, Department
from iiko_api import client


def update_employees_from_api(department_id: str, session: Session):
    try:
        employees_from_api = client.employees.get_employees_by_department(department_id)
    except Exception as e:
        raise Exception(f"Ошибка получения работников для отдела {department_id}: {e}")

    existing_employees = session.query(Employee).all()
    existing_employees_dict = {emp.id: emp for emp in existing_employees}
    departments_dict = {dept.code: dept for dept in session.query(Department).all()}
    roles_dict = {}

    for employee_data in employees_from_api:
        employee_id = employee_data['id']
        role_id = employee_data['mainRoleId']

        if role_id not in roles_dict:
            try:
                role_name = client.roles.get_role_by_id(role_id)['name']
                roles_dict[role_id] = role_name
            except Exception as e:
                raise Exception(f"Ошибка получения роли по id {role_id}: {e}")
        else:
            role_name = roles_dict[role_id]

        if employee_id in existing_employees_dict:
            existing_employee = existing_employees_dict[employee_id]
            existing_employee.name = employee_data['name']
            existing_employee.code = employee_data['code']
            existing_employee.position = role_name
        else:
            new_employee = Employee(
                id=employee_id,
                name=employee_data['name'],
                code=employee_data['code'],
                position=role_name
            )
            session.add(new_employee)
            existing_employee = new_employee

        existing_employee.departments.clear()
        department_codes = employee_data.get('departmentCodes', [])
        for department_code in department_codes:
            if department_code in departments_dict.keys():
                existing_employee.departments.append(departments_dict[department_code])
            else:
                raise ValueError(f"Отдел с кодом {department_code} не найден в базе данных.")

    # Удаляем сотрудников, которых больше нет в API
    api_employee_ids = {emp_data['id'] for emp_data in employees_from_api}
    for emp_id in existing_employees_dict.keys():
        if emp_id not in api_employee_ids:
            session.delete(existing_employees_dict[emp_id])
