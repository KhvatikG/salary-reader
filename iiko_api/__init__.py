from .core import BaseClient
from .endpoints import EmployeesEndpoints, RolesEndpoints

client = BaseClient(
    base_url="BASE_URL",
    login="PRO",
    hash_password="IIKO_PASS"
)

client.employees: EmployeesEndpoints = EmployeesEndpoints(client)
client.roles: RolesEndpoints = RolesEndpoints(client)

__all__ = ['BaseClient', 'client']