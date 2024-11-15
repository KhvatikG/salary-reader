from .core.base_client import BaseClient
from .endpoints.employees import EmployeesEndpoints, RolesEndpoints, ReportsEndpoints


class IikoApi:
    def __init__(self, base_url: str, login: str, hash_password: str):
        # Инициализируем базовый клиент
        self.client = BaseClient(base_url, login, hash_password)

        # Инициализируем эндпоинты, передавая клиент в конструктор каждого из них
        self.employees = EmployeesEndpoints(self.client)
        self.roles = RolesEndpoints(self.client)
        self.reports = ReportsEndpoints(self.client)
