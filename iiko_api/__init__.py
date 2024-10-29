from .core import BaseClient
from .endpoints import EmployeesEndpoints

client = BaseClient(
    base_url="BASE_URL",
    login="PRO",
    hash_password="IIKO_PASS"
)

client.employees = EmployeesEndpoints(client)

__all__ = ['BaseClient', 'client']