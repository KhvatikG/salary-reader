"""
Модуль для проверки и скачивания обновлений приложения
"""
import datetime
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Dict, Any
from packaging import version

from .version import get_version_info


class Updater:
    """Класс для управления обновлениями приложения"""
    
    def __init__(self, repo_owner: str = "KhvatikG", repo_name: str = "salary-reader"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        self.current_version = get_version_info()["version"]
        
    def check_for_updates(self) -> Optional[Dict[str, Any]]:
        """
        Проверяет наличие обновлений
        
        Returns:
            Dict с информацией о последнем релизе или None если обновлений нет
        """
        try:
            with urllib.request.urlopen(self.api_url) as response:
                data = json.loads(response.read().decode())
                
            latest_version = data["tag_name"].lstrip("v")  # Убираем префикс 'v'
            
            # Сравниваем версии
            if version.parse(latest_version) > version.parse(self.current_version):
                return {
                    "version": latest_version,
                    "tag_name": data["tag_name"],
                    "download_url": self._get_download_url(data),
                    "release_notes": data.get("body", ""),
                    "published_at": data.get("published_at", "")
                }
                
        except (urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
            print(f"Ошибка при проверке обновлений: {e}")
            
        return None
    
    def _get_download_url(self, release_data: Dict[str, Any]) -> Optional[str]:
        """Получает URL для скачивания exe файла"""
        for asset in release_data.get("assets", []):
            if asset["name"].endswith(".exe"):
                return asset["browser_download_url"]
        return None
    
    def download_update(self, download_url: str, progress_callback=None) -> bool:
        """
        Скачивает обновление
        
        Args:
            download_url: URL для скачивания
            progress_callback: Функция для отображения прогресса
            
        Returns:
            True если скачивание успешно, False иначе
        """
        try:
            # Определяем путь для временного файла
            temp_path = Path(sys.executable).parent / "SalaryReader_new.exe"
            
            def show_progress(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(100, (downloaded / total_size) * 100)
                    progress_callback(int(percent))
            
            # Скачиваем файл
            urllib.request.urlretrieve(download_url, temp_path, show_progress)
            
            # Проверяем, что файл скачался
            if temp_path.exists() and temp_path.stat().st_size > 0:
                return True
            else:
                temp_path.unlink(missing_ok=True)
                return False
                
        except Exception as e:
            print(f"Ошибка при скачивании обновления: {e}")
            return False
    
    def install_update(self) -> bool:
        """
        Устанавливает скачанное обновление
        
        Returns:
            True если установка успешна, False иначе
        """
        try:
            current_exe = Path(sys.executable)
            date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            new_exe = current_exe.parent / f"SalaryReader_new_{date_str}.exe"
            backup_exe = current_exe.parent / "SalaryReader_backup.exe"
            
            if not new_exe.exists():
                return False
            
            # Создаем резервную копию текущего exe
            if current_exe.exists():
                current_exe.rename(backup_exe)
            
            # Переименовываем новый exe
            new_exe.rename(current_exe)
            
            return True
            
        except Exception as e:
            print(f"Ошибка при установке обновления: {e}")
            # Пытаемся восстановить из резервной копии
            try:
                backup_exe = current_exe.parent / "SalaryReader_backup.exe"
                if backup_exe.exists():
                    backup_exe.rename(current_exe)
            except:
                pass
            return False
    
    def cleanup(self):
        """Очищает временные файлы"""
        try:
            temp_files = [
                Path(sys.executable).parent / "SalaryReader_new.exe",
                Path(sys.executable).parent / "SalaryReader_backup.exe"
            ]
            
            for file_path in temp_files:
                if file_path.exists():
                    file_path.unlink()
                    
        except Exception as e:
            print(f"Ошибка при очистке временных файлов: {e}")


def check_updates_available() -> bool:
    """
    Простая функция для проверки наличия обновлений
    
    Returns:
        True если есть обновления, False иначе
    """
    updater = Updater()
    return updater.check_for_updates() is not None
