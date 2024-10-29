from iiko_api import BaseClient
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
        # Выполнение GET-запроса к API, возвращающего данные о сотрудниках
        xml_data = self.client.get('/resto/api/employees/')

        # Преобразование XML-данных в словарь
        dict_data = xmltodict.parse(xml_data.text)

        # Извлечение списка сотрудников из словаря
        employees = dict_data['employees']['employee']

        return employees


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

        # Извлечение списка ролей из словаря
        roles = dict_data['employeeRoles']['role']

        return roles

