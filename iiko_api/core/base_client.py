# TODO: Флаг ис авторайз, отображает стэйт авторизации, если он тру то отправляем запрос
# TODO: Если фолс то предварительно авторизуемся. Такжн хэндлер ответов в случае анаотарайзд меняет флаг на folse
# TODO: При этом необходимо избежать зацыкленного повтореня попыток авторизации


import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from iiko_api.core.config.logging_config import get_logger

logger = get_logger(name=__name__)


class BaseClient:
    def __init__(self, base_url, login, hash_password):
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
            return None

        return wrapper

    @_handle_request_errors
    def _get(self, endpoint, params=None):
        return self.session.get(self.base_url + endpoint, params=params)

    @_handle_request_errors
    def _post(self, endpoint, data=None):
        return self.session.post(self.base_url + endpoint, data=data)

    def login(self):
        endpoint = "/resto/api/auth"
        params = {"login": self.username, "pass": self.secret}
        response = self._get(endpoint=endpoint, params=params).text
        if response:
            logger.info("Авторизация прошла успешно")
        else:
            logger.error("Ошибка авторизации")

    def logout(self):
        endpoint = "/resto/api/logout"
        response = self._get(endpoint=endpoint)
        if response:
            logger.info("Токен авторизации отменен")
        else:
            logger.error("Ошибка отмены авторизации")
