"""
Модуль для получения версии приложения 
"""
import tomllib
from pathlib import Path
from typing import Optional


def get_version() -> str:
    """
    Получает версию приложения из pyproject.toml
    
    Returns:
        str: Версия приложения в формате "x.y.z"
    """
    try:
        # Сначала пытаемся найти pyproject.toml в корне проекта (режим разработки)
        pyproject_path = Path(__file__).parent.parent.parent.parent / "pyproject.toml"
        
        # Если не найден, пытаемся найти в директории с exe (собранное приложение)
        if not pyproject_path.exists():
            import sys
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller bundle
                pyproject_path = Path(sys._MEIPASS) / "pyproject.toml"
            else:
                # Обычный запуск
                pyproject_path = Path(sys.executable).parent / "pyproject.toml"
        
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                
            return data["tool"]["poetry"]["version"]
        else:
            # Fallback версия если файл не найден
            return "0.0.0"
            
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError) as e:
        # Fallback версия если не удалось прочитать pyproject.toml
        return "0.0.0"


def get_version_info() -> dict[str, str]:
    """
    Получает расширенную информацию о версии
    
    Returns:
        dict: Словарь с информацией о версии
    """
    version = get_version()
    
    return {
        "version": version,
        "app_name": "SalaryReader",
        "full_version": f"SalaryReader v{version}"
    }
