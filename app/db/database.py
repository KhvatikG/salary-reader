import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..models import Base


# Определение полного пути к файлу базы данных
db_path = os.path.join(os.path.dirname(__file__), 'sqlite.db')
engine = create_engine(f'sqlite:///{db_path}')


Base.metadata.create_all(engine)  # Создание таблиц
Session = sessionmaker(bind=engine)

def get_session():
    return Session()