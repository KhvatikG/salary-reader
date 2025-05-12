import os
import sys
from pathlib import Path

def is_frozen():
    """Проверяем, запущено ли приложение как exe (PyInstaller)"""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def get_application_path():
    """Получаем путь до директории приложения"""
    if is_frozen():
        # Для exe-файла
        return Path(sys._MEIPASS)
    else:
        # Для разработки
        return Path(__file__).parent.parent.parent  # -> src директория

def get_db_path():
    """Получаем путь до файла БД"""
    if is_frozen():
        # Для exe-файла - сохраняем БД рядом с exe
        app_dir = Path(sys.executable).parent
        return app_dir / 'salary_reader.db'
    else:
        # Для разработки - сохраняем в пользовательской директории
        app_data = Path.home() / 'AppData' / 'Local' / 'SalaryReader'
        return app_data / 'salary_reader.db'

def get_resource_path(relative_path):
    """Получаем путь до ресурса (иконок, UI файлов и т.д.)"""
    if is_frozen():
        # Для exe-файла
        return Path(sys._MEIPASS) / relative_path
    else:
        # Для разработки
        return Path(__file__).parent.parent / relative_path
