# TODO: Флаг ис авторайз, отображает стэйт авторизации, если он тру то отправляем запрос
#  Если фолс то предварительно авторизуемся. Также хэндлер ответов в случае анаотарайзд меняет флаг на folse
#  При этом необходимо избежать зацикленного повторения попыток авторизации
"""
Модуль для работы с API iiko

"""

import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

from iiko_api.core.config.logging_config import get_logger

logger = get_logger(name=__name__)

LOGIN_ENDPOINT = "/resto/api/auth"
LOGOUT_ENDPOINT = "/resto/api/logout"


class BaseClient:
    """
    Базовый класс для работы с API iiko
    """
    def __init__(self, base_url, login, hash_password):
        """
        Инициализация клиента API iiko
        :param base_url: базовая URL-адрес API
        :param login: имя пользователя
        :param hash_password: хэш пароля
        """
        self.base_url = base_url
        self.secret = hash_password
        self.username = login
        self.session = requests.Session()

    @staticmethod
    def _handle_request_errors(func: callable):
        """
        Декоратор для обработки ошибок HTTP запросов
        :param func: Функция для обработки ошибок
        :return:
        """

        def wrapper(*args, **kwargs):
            try:
                response = func(*args, **kwargs)
                response.raise_for_status()
                return response
            except HTTPError as http_error:
                logger.error(f"HTTP error: {http_error} - Status code: {http_error.response.status_code}")
                logger.debug(f"Request URL: {http_error.response.url}")
                logger.debug(f"Request Method: {http_error.response.request.method}")
                logger.debug(f"Request Headers: {http_error.response.request.headers}")
                logger.debug(f"Request Body: {http_error.response.request.body}")
                logger.debug(f"Response Headers: {http_error.response.headers}")
                logger.debug(f"Response Body: {http_error.response.text}")
            except ConnectionError as connection_error:
                logger.error(f"Connection error: {connection_error}")
            except Timeout as timeout_error:
                logger.error(f"Timeout error: {timeout_error}")
            except RequestException as request_error:
                logger.error(f"Request error: {request_error}")
            raise

        return wrapper

    @_handle_request_errors
    def get(self, endpoint, params=None):
        """
        Метод для выполнения GET запроса
        :param endpoint: конечная точка API
        :param params: параметры запроса
        :return: ответ сервера
        """
        return self.session.get(self.base_url + endpoint, params=params)

    @_handle_request_errors
    def _post(self, endpoint, data=None):
        """
        Метод для выполнения POST запроса
        :param endpoint: конечная точка API
        :param data: данные запроса
        :return: ответ сервера
        """
        return self.session.post(self.base_url + endpoint, data=data)

    def login(self):
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

    def logout(self):
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
