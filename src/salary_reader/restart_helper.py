"""
Вспомогательный модуль для перезапуска приложения после обновления
"""
import os
import sys
import subprocess
import time
from pathlib import Path
from loguru import logger


def restart_application():
    """
    Перезапускает приложение после обновления
    """
    try:
        logger.debug("Перезапускаем приложение...")
        # Получаем путь к исполняемому файлу
        exe_path = sys.executable
        logger.debug(f"Путь к исполняемому файлу: {exe_path}")
        
        # Если это PyInstaller bundle, используем полный путь
        if getattr(sys, 'frozen', False):
            exe_path = os.path.abspath(sys.executable)
            logger.debug("Это PyInstaller bundle")
            logger.debug(f"Путь к исполняемому файлу: {exe_path}")
        
        # Получаем рабочую директорию
        working_dir = os.path.dirname(exe_path)
        logger.debug(f"Рабочая директория: {working_dir}")
        
        # Проверяем, что новый exe файл существует и не поврежден
        new_exe_path = os.path.join(working_dir, "SalaryReader.exe")
        if os.path.exists(new_exe_path):
            logger.debug("Проверяем новый exe файл...")
            try:
                # Пробуем прочитать заголовок файла
                with open(new_exe_path, 'rb') as f:
                    header = f.read(2)
                    if header != b'MZ':
                        logger.error("Новый exe файл поврежден - не является PE файлом")
                        return False
                logger.debug("Новый exe файл проверен успешно")
            except Exception as e:
                logger.error(f"Ошибка при проверке нового exe файла: {e}")
                return False
        
        # Создаем PowerShell скрипт для более надежного перезапуска
        ps_script_path = os.path.join(working_dir, "restart_app.ps1")
        logger.debug(f"Создаем PowerShell скрипт: {ps_script_path}")
        
        with open(ps_script_path, 'w', encoding='utf-8-sig') as f:  # BOM для правильной кодировки
            f.write('#!/usr/bin/env pwsh\n')
            f.write('# PowerShell скрипт для перезапуска приложения\n')
            f.write('$ErrorActionPreference = "SilentlyContinue"\n')  # Подавляем ошибки
            f.write(f'Set-Location -Path "{working_dir}"\n')
            f.write(f'Start-Process -FilePath "{exe_path}" -ArgumentList "--restart-after-update" -WorkingDirectory "{working_dir}"\n')
            f.write('# Удаляем скрипт после запуска\n')
            f.write('Start-Sleep -Seconds 2\n')
            f.write(f'Remove-Item -Path "{ps_script_path}" -Force -ErrorAction SilentlyContinue\n')
        
        # Создаем bat файл как fallback
        bat_path = os.path.join(working_dir, "restart_app.bat")
        logger.debug(f"Создаем bat файл: {bat_path}")
        
        with open(bat_path, 'w', encoding='utf-8-sig') as f:  # BOM для правильной кодировки
            f.write('@echo off\n')
            f.write('chcp 65001 >nul\n')  # Устанавливаем UTF-8 кодировку
            f.write('REM Bat файл для перезапуска приложения\n')
            f.write(f'cd /d "{working_dir}"\n')
            f.write(f'"{exe_path}" --restart-after-update\n')
            f.write('REM Удаляем bat файл после запуска\n')
            f.write('del "%~f0" 2>nul\n')  # Подавляем ошибки
        
        # Сначала пробуем bat файл (лучше работает с кириллицей)
        try:
            logger.debug("Пробуем запустить через bat файл...")
            subprocess.Popen([bat_path], shell=True)
            logger.debug("Bat файл запущен")
            return True
        except Exception as e:
            logger.debug(f"Ошибка при запуске bat файла: {e}")
            
            # Fallback - пробуем PowerShell
            try:
                logger.debug("Пробуем запустить через PowerShell...")
                subprocess.Popen([
                    'powershell.exe', 
                    '-ExecutionPolicy', 'Bypass', 
                    '-File', ps_script_path
                ], shell=False)
                logger.debug("PowerShell скрипт запущен")
                return True
            except Exception as e2:
                logger.debug(f"Ошибка при запуске PowerShell: {e2}")
                
                # Последний fallback - прямой запуск
                try:
                    logger.debug("Пробуем прямой запуск...")
                    subprocess.Popen([exe_path, "--restart-after-update"], cwd=working_dir, shell=False)
                    logger.debug("Прямой запуск выполнен")
                    return True
                except Exception as e3:
                    logger.debug(f"Ошибка при прямом запуске: {e3}")
                    return False
        
    except Exception as e:
        logger.debug(f"Критическая ошибка при перезапуске: {e}")
        return False


if __name__ == "__main__":
    restart_application()
