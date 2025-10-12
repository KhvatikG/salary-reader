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
from loguru import logger
from packaging import version

from .version import get_version_info


class Updater:
    """Класс для управления обновлениями приложения"""
    
    def __init__(self, repo_owner: str = "KhvatikG", repo_name: str = "salary-reader"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        self.current_version = get_version_info()["version"]
        
        logger.debug("Инициализация Updater...")
        logger.debug(f"Текущая версия: {self.current_version}")
        logger.debug(f"API URL: {self.api_url}")
        logger.debug(f"Репозиторий: {self.repo_owner}/{self.repo_name}")
        
    def check_for_updates(self) -> Optional[Dict[str, Any]]:
        """
        Проверяет наличие обновлений
        
        Returns:
            Dict с информацией о последнем релизе или None если обновлений нет
        """
        try:
            logger.debug("Проверяем наличие обновлений...")
            with urllib.request.urlopen(self.api_url) as response:
                data = json.loads(response.read().decode())
            logger.debug(f"Данные о релизе: {data}")
            latest_version = data["tag_name"].lstrip("v")  # Убираем префикс 'v'

            # Сравниваем версии
            if version.parse(latest_version) > version.parse(self.current_version):
                logger.debug("Обновления найдены")
                return {
                    "version": latest_version,
                    "tag_name": data["tag_name"],
                    "download_url": self._get_download_url(data),
                    "release_notes": data.get("body", ""),
                    "published_at": data.get("published_at", "")
                }
                
        except (urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
            logger.debug(f"Ошибка при проверке обновлений: {e}")
            
        return None
    
    def _get_download_url(self, release_data: Dict[str, Any]) -> Optional[str]:
        """Получает URL для скачивания exe файла"""
        logger.debug("Получаем URL для скачивания exe файла...")
        for asset in release_data.get("assets", []):
            if asset["name"].endswith(".exe"):
                url = asset["browser_download_url"]
                logger.debug(f"Найден exe файл: {asset['name']}")
                logger.debug(f"URL: {url}")
                # Проверяем, что URL начинается с https
                if url.startswith("https://"):
                    return url
                else:
                    logger.debug(f"URL не использует HTTPS: {url}")
        logger.debug("URL для скачивания exe файла не найден")
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
            logger.debug(f"Скачиваем обновление с URL: {download_url}")
            # Определяем путь для временного файла
            temp_path = Path(sys.executable).parent / "SalaryReader_new.exe"
            
            # Удаляем старый файл если есть
            if temp_path.exists():
                temp_path.unlink()
                logger.debug("Старый временный файл удален")
            
            # Создаем запрос с правильными заголовками
            request = urllib.request.Request(download_url)
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            request.add_header('Accept', 'application/octet-stream')
            request.add_header('Accept-Encoding', 'identity')  # Отключаем сжатие
            
            logger.debug("Отправляем запрос...")
            
            # Скачиваем файл
            with urllib.request.urlopen(request) as response:
                # Проверяем статус ответа
                if response.status != 200:
                    logger.debug(f"HTTP ошибка: {response.status}")
                    return False
                
                # Проверяем Content-Type
                content_type = response.headers.get('Content-Type', '')
                logger.debug(f"Content-Type: {content_type}")
                
                # Проверяем размер файла
                content_length = response.headers.get('Content-Length')
                if content_length:
                    expected_size = int(content_length)
                    logger.debug(f"Ожидаемый размер файла: {expected_size} байт")
                else:
                    expected_size = None
                
                # Скачиваем файл по частям
                downloaded = 0
                with open(temp_path, 'wb') as f:
                    while True:
                        chunk = response.read(8192)  # Читаем по 8KB
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Обновляем прогресс
                        if expected_size and progress_callback:
                            percent = min(100, (downloaded / expected_size) * 100)
                            progress_callback(round(percent, 4))
            
            # Проверяем, что файл скачался
            if temp_path.exists():
                file_size = temp_path.stat().st_size
                logger.debug(f"Скачано {file_size} байт")
                
                # Проверяем минимальный размер (exe файл должен быть больше 1MB)
                if file_size < 1024 * 1024:  # 1MB
                    logger.debug(f"Файл слишком мал: {file_size} байт")
                    temp_path.unlink()
                    return False
                
                # Проверяем, что это действительно exe файл
                with open(temp_path, 'rb') as f:
                    header = f.read(2)
                    if header != b'MZ':  # PE файл начинается с MZ
                        logger.debug(f"Файл не является исполняемым: {header}")
                        temp_path.unlink()
                        return False
                
                logger.debug("Файл успешно скачан и проверен")
                return True
            else:
                logger.debug("Файл не был создан")
                return False
                
        except urllib.error.HTTPError as e:
            logger.debug(f"HTTP ошибка при скачивании: {e.code} - {e.reason}")
            return False
        except urllib.error.URLError as e:
            logger.debug(f"URL ошибка при скачивании: {e.reason}")
            return False
        except Exception as e:
            logger.debug(f"Ошибка при скачивании обновления: {e}")
            # Удаляем поврежденный файл
            if temp_path.exists():
                temp_path.unlink()
            return False
    
    def install_update(self) -> bool:
        """
        Устанавливает скачанное обновление
        
        Returns:
            True если установка успешна, False иначе
        """
        logger.debug("Установка обновления...")
        logger.debug(f"Текущая версия: {self.current_version}")
        
        try:
            current_exe = Path(sys.executable)
            new_exe = current_exe.parent / f"SalaryReader_new.exe"
            backup_exe = current_exe.parent / "SalaryReader_backup.exe"
            
            logger.debug(f"Текущий exe: {current_exe}")
            logger.debug(f"Новый exe: {new_exe}")
            logger.debug(f"Резервная копия: {backup_exe}")


            if not new_exe.exists():
                logger.debug("Новый exe не найден")
                return False
            
            logger.debug("Новый exe найден")
            logger.debug("Создаем резервную копию текущего exe...")

            # Создаем резервную копию текущего exe
            if current_exe.exists():
                logger.debug("Создаем резервную копию текущего exe...")
                current_exe.rename(backup_exe)
                logger.debug("Резервная копия создана")
            
            logger.debug("Переименовываем новый exe...")
            # Переименовываем новый exe
            new_exe.rename(current_exe)
            logger.debug("Новый exe переименован")
            
            logger.debug("Установка обновления завершена")
            return True
            
        except Exception as e:
            logger.debug(f"Ошибка при установке обновления: {e}")
            # Пытаемся восстановить из резервной копии
            try:
                logger.debug("Пытаемся восстановить из резервной копии...")
                backup_exe = current_exe.parent / "SalaryReader_backup.exe"
                if backup_exe.exists():
                    backup_exe.rename(current_exe)
                    logger.debug("Восстановление из резервной копии завершено")
            except:
                logger.debug("Восстановление из резервной копии не удалось")
                pass
            return False
    
    def cleanup(self):
        """Очищает временные файлы"""
        try:
            logger.debug("Очищаем временные файлы...")
            temp_files = [
                Path(sys.executable).parent / "SalaryReader_new.exe",
                Path(sys.executable).parent / "SalaryReader_backup.exe"
            ]
            logger.debug(f"Временные файлы: {temp_files}")
            for file_path in temp_files:
                if file_path.exists():
                    file_path.unlink()
                    logger.debug(f"Временный файл {file_path} удален")
        except Exception as e:
            logger.debug(f"Ошибка при очистке временных файлов: {e}")


def check_updates_available() -> bool:
    """
    Простая функция для проверки наличия обновлений
    
    Returns:
        True если есть обновления, False иначе
    """
    logger.debug("Проверяем наличие обновлений...")
    updater = Updater()
    logger.debug("Проверка обновлений завершена")
    return updater.check_for_updates() is not None
