from .core import BaseClient
from .endpoints import EmployeesEndpoints, RolesEndpoints
from dotenv import dotenv_values

config = dotenv_values(".env")

client = BaseClient(
    base_url=config.get("BASE_URL"),
    login=config.get("IIKO_LOGIN"),
    hash_password=config.get("IIKO_PASS")
)

client.employees: EmployeesEndpoints = EmployeesEndpoints(client)
client.roles: RolesEndpoints = RolesEndpoints(client)

__all__ = ['BaseClient', 'client']