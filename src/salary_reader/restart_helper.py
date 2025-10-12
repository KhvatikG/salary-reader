"""
Вспомогательный модуль для перезапуска приложения после обновления
"""
import os
import sys
import subprocess
import time
from pathlib import Path


def restart_application():
    """
    Перезапускает приложение после обновления
    """
    try:
        # Получаем путь к исполняемому файлу
        exe_path = sys.executable
        
        # Если это PyInstaller bundle, используем полный путь
        if getattr(sys, 'frozen', False):
            exe_path = os.path.abspath(sys.executable)
        
        # Получаем рабочую директорию
        working_dir = os.path.dirname(exe_path)
        
        # Создаем bat файл для перезапуска
        bat_path = os.path.join(working_dir, "restart_app.bat")
        
        with open(bat_path, 'w', encoding='utf-8') as f:
            f.write(f'@echo off\n')
            f.write(f'cd /d "{working_dir}"\n')
            f.write(f'"{exe_path}"\n')
            f.write(f'del "%~f0"\n')  # Удаляем bat файл после запуска
        
        # Запускаем bat файл
        subprocess.Popen([bat_path], shell=True)
        
        return True
        
    except Exception as e:
        print(f"Ошибка при создании скрипта перезапуска: {e}")
        
        # Fallback - попробуем обычный перезапуск
        try:
            subprocess.Popen([exe_path], cwd=working_dir)
            return True
        except Exception as e2:
            print(f"Ошибка при fallback перезапуске: {e2}")
            return False


if __name__ == "__main__":
    restart_application()
