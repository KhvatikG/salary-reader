from dotenv import dotenv_values
from iiko_api import IikoApi

config = dotenv_values(".env")

iiko_api = IikoApi(
    base_url=config.get("BASE_URL"),
    login=config.get("IIKO_LOGIN"),
    hash_password=config.get("IIKO_PASS")
)

__all__ = ['iiko_api']
