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

    if filepath:
        # Новый логгер с ротацией по дням
        new_logger.add(sink=filepath, level=level, rotation="1 day", retention="10 days", **kwargs)
    else:
        # В собранном exe файле sys.stdout может быть недоступен
        try:
            new_logger.add(sink=sys.stdout, level=level, **kwargs)
        except:
            # Если sys.stdout недоступен, используем stderr или файл
            try:
                new_logger.add(sink=sys.stderr, level=level, rotation="1 day", retention="10 days", **kwargs)
            except:
                # Последний резерв - файл в текущей директории
                new_logger.add(sink="app.log", level=level, rotation="1 day", retention="10 days", **kwargs)
    return new_logger



