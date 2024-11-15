# TODO: Заменить удалить все client.login() в проекте
"""
Модуль для работы с API iiko
Содержит Базовый класс для работы с API iiko.
Включающий методы: get, post
Методы для авторизации и отправки запросов.
А так-же контекстный менеджер логирования запросов и декоратор для авторизации запросов в функциях.
Логирует запросы и ошибки.
"""
import contextlib
from typing import Callable, Any

import requests
from requests import Response
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

from iiko_api.core.config.logging_config import get_logger

logger = get_logger(name=__name__, level="DEBUG")

LOGIN_ENDPOINT = "/resto/api/auth"
LOGOUT_ENDPOINT = "/resto/api/logout"


class BaseClient:
    """
    Базовый класс для работы с API iiko
    """
    def __init__(self, base_url: str, login: str, hash_password: str):
        """
        Инициализация клиента API iiko
        :param base_url: базовый URL-адрес API
        :param login: имя пользователя
        :param hash_password: хэш пароля
        """
        self.base_url = base_url
        self.secret = hash_password
        self.username = login
        self.session = requests.Session()

    @staticmethod
    def _handle_request_errors(func: Callable) -> Callable:
        """
        Декоратор для обработки ошибок HTTP запросов
        :param func: Функция для обработки ошибок
        :return:
        """

        def wrapper(*args, **kwargs):
            try:
                response: Response = func(*args, **kwargs)
                response.raise_for_status()
                logger.debug(f":\n  Request URL: {response.request.url}\n"
                            f"  Request Method: {response.request.method}\n"
                            f"  Request Body: {response.request.body}\n"
                            f"  Response Body: {response.text}\n"
                             )
                return response
            except HTTPError as http_error:
                logger.error(f"HTTP error: {http_error} - Status code: {http_error.response.status_code}")
                logger.debug(f"\n  Request URL: {http_error.response.url}\n"
                            f"  Request Method: {http_error.response.request.method}\n"
                            f"  Request Headers: {http_error.response.request.headers}\n"
                            f"  Request Body: {http_error.response.request.body}\n"
                            f"  Response Headers: {http_error.response.headers}\n"
                            f"  Response Body: {http_error.response.text}\n"
                            )
            except ConnectionError as connection_error:
                logger.error(f"Connection error: {connection_error}")
            except Timeout as timeout_error:
                logger.error(f"Timeout error: {timeout_error}")
            except RequestException as request_error:
                logger.error(f"Request error: {request_error}")
            raise # Повторное возбуждение исключения для логики обработки

        return wrapper

    @_handle_request_errors
    def get(self, endpoint: str, params: dict[str, Any] = None) -> Response:
        """
        Метод для выполнения GET запроса
        :param endpoint: конечная точка API
        :param params: параметры запроса
        :return: ответ сервера
        """
        return self.session.get(self.base_url + endpoint, params=params)

    @_handle_request_errors
    def post(self, endpoint: str, data: dict[str, Any] = None) -> Response:
        """
        Метод для выполнения POST запроса
        :param endpoint: конечная точка API
        :param data: данные запроса
        :return: ответ сервера
        """
        return self.session.post(self.base_url + endpoint, data=data)

    def login(self) -> None:
        """
        Метод для авторизации, токен сохраняется в сессии
        :return:
        """
        params = {"login": self.username, "pass": self.secret}
        response = self.get(endpoint=LOGIN_ENDPOINT, params=params)
        if response.ok:
            logger.info("Авторизация прошла успешно")
        else:
            logger.error("Ошибка авторизации")
            logger.debug(f"Ответ: {response.text}")

    def logout(self) -> None:
        """
        Метод для отмены авторизации
        :return:
        """
        response = self.get(endpoint=LOGOUT_ENDPOINT)
        if response.ok:
            logger.info("Токен авторизации отменен")
        else:
            logger.error("Ошибка отмены авторизации")
            logger.debug(f"Ответ: {response.text}")

    @contextlib.contextmanager
    def auth(self) -> None:
        """
        Контекстный менеджер для авторизации запросов
        """
        self.login()
        try:
            yield
        finally:
            self.logout()

    def with_auth(self, func: Callable) -> Callable:
        """
        Декоратор для выполнения функции с авторизацией
        """
        def wrapper(*args, **kwargs) -> Any:
            with self.auth():
                return func(*args, **kwargs)
        return wrapper
