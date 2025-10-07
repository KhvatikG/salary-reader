import sys
from pathlib import Path


def resource_path(relative_path: str) -> str:
    """Возвращает абсолютный путь к ресурсам для работы и в собранном приложении"""
    try:
        # PyInstaller создает временную папку в _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        base_path = Path(__file__).parent.parent  # Родительская папка относительно helpers/

    return str(base_path / relative_path)
