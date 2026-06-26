from __future__ import annotations

import contextlib
import sys
from pathlib import Path

from dotenv import dotenv_values
from requests.exceptions import HTTPError

from salary_reader.core.logging_config import get_logger

logger = get_logger(__name__, level="DEBUG")


def _env_file_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / ".env"
    return Path(__file__).resolve().parents[3] / ".env"


try:
    from iiko_api import IikoApi

    config = dotenv_values(_env_file_path())

    base_url = config.get("BASE_URL")
    login = config.get("IIKO_LOGIN")
    password = config.get("IIKO_PASS")

    if not all([base_url, login, password]):
        print(
            "Warning: Missing iiko API configuration. "
            "Please create a .env file with BASE_URL, IIKO_LOGIN, and IIKO_PASS"
        )
        iiko_api = None
    else:
        iiko_api = IikoApi(
            base_url=base_url,
            login=login,
            hash_password=password,
        )
except Exception as e:
    print(f"Warning: Failed to initialize iiko_api: {e}")
    iiko_api = None


@contextlib.contextmanager
def safe_iiko_auth():
    """
    Контекстный менеджер аутентификации iiko.
    Игнорирует 401 на logout — сессия уже могла истечь на стороне сервера.
    """
    if iiko_api is None:
        raise RuntimeError("iiko_api не инициализирован")

    iiko_api.client.login()
    try:
        yield iiko_api
    finally:
        try:
            iiko_api.client.logout()
        except HTTPError as e:
            logger.warning(f"logout iiko завершился с ошибкой (игнорируем): {e}")


__all__ = ["iiko_api", "safe_iiko_auth"]
