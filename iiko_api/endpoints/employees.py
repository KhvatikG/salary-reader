from datetime import datetime, date

from iiko_api.core import BaseClient
import xmltodict


class EmployeesEndpoints:
    """
    Класс, предоставляющий методы для работы с сотрудниками
    """

    def __init__(self, client: BaseClient):
        self.client = client

    def get_employees(self) -> list[dict]:
        """
        Получение списка всех сотрудников
        :return: список словарей, где каждый словарь представляет сотрудника
        """
        # Авторизация
        self.client.login()

        # Выполнение GET-запроса к API, возвращающего данные о сотрудниках
        xml_data = self.client.get('/resto/api/employees/')

        # Отпускаем авторизацию
        self.client.logout()

        # Преобразование XML-данных в словарь
        dict_data = xmltodict.parse(xml_data.text)

        return dict_data['employees']['employee']

    def get_employee_by_id(self, employee_id: int) -> dict:
        """
        Получение данных о сотруднике по его ID
        :return: словарь, где каждый ключ представляет поле сотрудника, а значение - его значение
        """
        # Авторизация
        self.client.login()

        # Выполнение GET-запроса к API, возвращающего данные о сотруднике
        xml_data = self.client.get(f'/resto/api/employees/byId/{employee_id}')

        # Отпускаем авторизацию
        self.client.logout()

        # Преобразование XML-данных в словарь
        dict_data = xmltodict.parse(xml_data.text)

        dict_data = dict_data['employee']

        if dict_data.get('departmentCodes') and not isinstance(dict_data.get('departmentCodes'), list):
            dict_data['departmentCodes'] = [dict_data.get('departmentCodes')]
        else:
            dict_data['departmentCodes'] = []

        return dict_data

    def get_employees_by_department(self, department_code: str) -> list[dict]:
        """
        Получение списка сотрудников по коду отдела
        :return: список словарей, где каждый словарь представляет сотрудника привязанного к отделу
        """

        # Выполнение GET-запроса к API, возвращающего данные о сотрудниках
        xml_data = self.client.get(f'/resto/api/employees/byDepartment/{department_code}')

        # Преобразование XML-данных в словарь
        dict_data = xmltodict.parse(xml_data.text)

        employees = []

        for employee in dict_data['employees']['employee']:
            if employee.get('departmentCodes') and not isinstance(employee.get('departmentCodes'), list):
                employee['departmentCodes'] = [employee.get('departmentCodes')]
            else:
                employee['departmentCodes'] = []

            employees.append(employee)

        return employees

    def get_attendances_for_department(self, department_code: str, date_from: datetime, date_to: datetime) -> list[
        dict]:
        """
        Получение явок сотрудников по отделу за период.
        :param department_code: Код отдела
        :param date_from: Начало периода
        :param date_to: Конец периода, включительно
        :return: Список словарей, где каждый словарь представляет явку
        """
        date_from = datetime.strftime(date_from, '%Y-%m-%d')
        date_to = datetime.strftime(date_to, '%Y-%m-%d')
        print(date_from, date_to)
        # Авторизация
        self.client.login()

        endpoint = f'/resto/api/employees/attendance/byDepartment/{department_code}'

        params = {
            'from': date_from,
            'to': date_to
        }

        # Выполняем запрос к API
        xml_data = self.client.get(endpoint=endpoint, params=params)

        # Отпускаем авторизацию
        self.client.logout()

        dict_data = xmltodict.parse(xml_data.text)

        return dict_data['attendances']['attendance']


class RolesEndpoints:
    """
    Класс, предоставляющий методы для работы с ролями сотрудников по API
    """

    def __init__(self, client: BaseClient):
        self.client = client

    def get_roles(self) -> list[dict]:
        """
        Получение списка всех ролей
        :return: Список словарей, где каждый словарь представляет роль
        """
        # Выполнение GET-запроса к API, возвращающего данные о ролях
        xml_data = self.client.get('/resto/api/employees/roles/')

        # Преобразование XML-данных в словарь
        dict_data = xmltodict.parse(xml_data.text)

        return dict_data['employeeRoles']['role']

    def get_role_by_id(self, role_id: str) -> dict:
        """
        Получение роли по ID
        :param role_id: ID роли
        :return: Словарь, где каждый словарь представляет роль
        """
        # Авторизуемся
        self.client.login()

        # Выполнение GET-запроса к API, возвращающего данные о роли по ID
        xml_data = self.client.get(f'/resto/api/employees/roles/byId/{role_id}')

        # Отпускаем авторизацию
        self.client.logout()

        # Преобразование XML-данных в словарь
        dict_data = xmltodict.parse(xml_data.text)

        return dict_data['role']


class ReportsEndpoints:
    """
    Класс, предоставляющий методы для работы с отчетами по API
    """

    def __init__(self, client: BaseClient):
        self.client = client

    def get_sales_report(
            self, date_from: datetime, date_to: datetime, department_id: str, date_aggregation: bool = True
    ) -> dict[date, float] | list[dict]:
        """
        Получение отчета по продажам за период.
        Возвращает словарь, где ключ это дата, а значение это выручка, если date_aggregation=True
        Если date_aggregation=False, то отчет будет списком словарей с ключами date и value.
        :param department_id: ID отдела
        :param date_from: Начало периода
        :param date_to: Конец периода включается в отчет
        :param date_aggregation: Если True, то отчет будет агрегирован по дням, иначе будет соответствовать выводу iiko.
        :return: Словарь, где ключ это дата, а значение это выручка.
        """
        format_ = '%d.%m.%Y'
        date_from = datetime.strftime(date_from, format_)
        date_to = datetime.strftime(date_to, format_)

        endpoint = '/resto/api/reports/sales'

        params = {
            'department': department_id,
            'dateFrom': date_from,
            'dateTo': date_to,
            'allRevenue': 'false'
        }

        # Авторизуемся
        self.client.login()

        # Выполнение GET-запроса к API
        xml_data = self.client.get(endpoint=endpoint, params=params)

        # Отпускаем авторизацию
        self.client.logout()

        # Преобразование XML-данных в словарь
        dict_data = xmltodict.parse(xml_data.text)
        print(f"[get_sales_report]{dict_data=}")
        if date_aggregation:
            agg_dict_data: dict[date, float] = {}
            dict_data = dict_data['dayDishValues']['dayDishValue']
            print(f"[get_sales_report]{dict_data=}")
            if type(dict_data) != list:
                dict_data = [dict_data]
                print("--------NOT LIST TO LIST--------")
                print(f"[get_sales_report]{dict_data=}")
                print("--------NOT LIST TO LIST--------")

            for day in dict_data:
                print("----------------------")
                print(f"[get_sales_report]{day=}")
                print("----------------------")
                format_ = '%d.%m.%Y'
                day_date = datetime.strptime(day['date'], format_).date()
                print(f"[get_sales_report]{day_date=}")
                agg_dict_data[day_date] = day['value']
                print(f"[get_sales_report]{agg_dict_data=}")

            return agg_dict_data
        return dict_data['dayDishValues']['dayDishValue']
