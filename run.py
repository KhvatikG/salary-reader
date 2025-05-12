import sys
import os

# Добавляем директорию src в путь Python
sys.path.insert(0, os.path.abspath('src'))

# Импортируем функцию запуска
from salary_reader.main import run

if __name__ == "__main__":
    run()