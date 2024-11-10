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

    def get_employees_by_department(self, department_code: str) -> list[dict]:
        """
        Получение списка сотрудников по коду отдела
        :return: список словарей, где каждый словарь представляет сотрудника привязанного к отделу
        """
        # Авторизация
        self.client.login()

        # Выполнение GET-запроса к API, возвращающего данные о сотрудниках
        xml_data = self.client.get(f'/resto/api/employees/byDepartment/{department_code}')

        # Отпускаем авторизацию
        self.client.logout()

        # Преобразование XML-данных в словарь
        dict_data = xmltodict.parse(xml_data.text)

        return dict_data['employees']['employee']


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
        # Авторизуемся
        self.client.login()

        # Выполнение GET-запроса к API, возвращающего данные о ролях
        xml_data = self.client.get('/resto/api/employees/roles/')

        # Отпускаем авторизацию
        self.client.logout()

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
