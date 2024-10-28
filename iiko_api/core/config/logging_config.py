from __future__ import annotations  # Импортируем типы loguru для анотаций

import sys

import loguru
from loguru import logger


def get_logger(name: str, level: str = "INFO", filepath: str = None, **kwargs) -> loguru.Logger:
    """
    Возвращает объект логгера

    :param name: Имя логгера
    :param level: Уровень логирования, по умолчанию INFO
    :param filepath: Путь для сохранения логов
    :param kwargs: Дополнительные параметры логирования
    :return: Объект логгера
    """

    new_logger = logger.bind(name=name)
    new_logger.remove() # Удаляем дефолтный логгер

    new_logger.add(sink=filepath if filepath else sys.stdout, level=level, **kwargs)
    return new_logger



