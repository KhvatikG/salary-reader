from __future__ import annotations  # Импортируем типы loguru для анотаций

import sys

import loguru
from loguru import logger

from .paths import get_log_path

logfile_path = get_log_path("app.log")

def get_logger(name: str, level: str = "DEBUG", filepath: str = logfile_path, **kwargs) -> loguru.Logger:
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
    
    # Добавляем консольный вывод
    new_logger.add(sink=sys.stderr, level=level, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level>")
    
    # Добавляем файловый вывод
    new_logger.add(sink=filepath, level=level, rotation="1 day", retention="10 days", **kwargs)
    return new_logger
