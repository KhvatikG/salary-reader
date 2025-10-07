import os
import sys
import shutil
from pathlib import Path

# Добавляем src в путь импорта
sys.path.insert(0, os.path.abspath('src'))

def build_executable():
    # Устанавливаем переменные среды для PyInstaller
    os.environ['PYTHONOPTIMIZE'] = '1'

    # Путь для собранного приложения
    dist_dir = Path('dist')

    # Очищаем предыдущие сборки
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    # Определяем все файлы ресурсов
    icon_files = []
    ui_dir = Path('src/salary_reader/ui')
    for file in ui_dir.glob('*.png'):
        icon_files.append(f'--add-data={file};salary_reader/ui/')
    for file in ui_dir.glob('*.ico'):
        icon_files.append(f'--add-data={file};salary_reader/ui/')

    # Формируем команду для PyInstaller
    pyinstaller_args = [
        'pyinstaller',
        '--name=SalaryReader',
        '--onefile',  # Один файл
        '--windowed',  # Без консоли
        '--clean',
        '--noconfirm',
        # Добавляем точку входа
        'src/salary_reader/main.py',
    ]

    # Добавляем ресурсы
    pyinstaller_args.extend(icon_files)

    # Выполняем сборку
    import subprocess
    subprocess.run(' '.join(pyinstaller_args), shell=True)

    print(f"Сборка завершена. Исполняемый файл находится в {dist_dir / 'SalaryReader.exe'}")

if __name__ == '__main__':
    build_executable()