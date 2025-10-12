# salary_reader/core/database.py
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from .paths import get_db_path  # Импорт нового модуля

# Проверяем доступность sqlite3
try:
    import sqlite3
except ImportError as e:
    print(f"Ошибка импорта sqlite3: {e}")
    print("Попытка исправления...")
    
    # Если это PyInstaller bundle, пытаемся исправить пути
    if getattr(sys, 'frozen', False):
        import os
        # Добавляем возможные пути к sqlite3
        possible_paths = [
            os.path.join(os.path.dirname(sys.executable), 'sqlite3.dll'),
            os.path.join(os.path.dirname(sys.executable), '_internal', 'sqlite3.dll'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Найден sqlite3.dll в {path}")
                break
        else:
            print("sqlite3.dll не найден в стандартных местах")
    
    raise e

# Создаём директорию для БД при необходимости
db_path = get_db_path()
os.makedirs(db_path.parent, exist_ok=True)

engine = create_engine(f'sqlite:///{db_path}')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def get_session():
    return Session()
