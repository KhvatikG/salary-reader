# salary_reader/core/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from .paths import get_db_path  # Импорт нового модуля

# Создаём директорию для БД при необходимости
db_path = get_db_path()
os.makedirs(db_path.parent, exist_ok=True)

engine = create_engine(f'sqlite:///{db_path}')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def get_session():
    return Session()
