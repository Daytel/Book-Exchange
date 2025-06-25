from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Получение параметров подключения с fallback-значениями
DB_USER = os.getenv("DB_USER", "root")  # Fallback к 'root' если переменная не задана
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")  # Добавлен порт
DB_NAME = os.getenv("DB_NAME", "mydb")

# Формирование строки подключения
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?charset=utf8mb4"  # Добавляем кодировку
)

# Настройка движка SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=3600,   # Пересоздавать соединения каждые 3600 секунд (1 час)
    pool_size=10,        # Размер пула соединений
    max_overflow=20,     # Максимальное количество соединений сверх pool_size
    echo=False           # Логирование SQL (True для отладки)
)

# Фабрика сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Базовый класс для моделей
Base = declarative_base()

# Генератор сессий для Dependency Injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()