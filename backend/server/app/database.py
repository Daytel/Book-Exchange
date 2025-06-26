from sqlalchemy import create_engine, text
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

# 🚀 ЗАПОЛНЕНИЕ БАЗЫ ПРИ ЗАПУСКЕ
def populate_database():
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    test_data_path = os.path.join(BASE_DIR, "db", "test_data.sql")

    if not os.path.exists(test_data_path):
        print(f"Файл не найден: {test_data_path}")
        return

    print("📥 Заполнение базы данных из test_data.sql...")
    with open(test_data_path, encoding="utf-8") as f:
        sql_commands = f.read()

    with engine.connect() as conn:
        for command in sql_commands.split(';'):
            command = command.strip()
            if command:
                try:
                    conn.execute(text(command))
                except Exception as e:
                    print(f"⚠️ Ошибка при выполнении SQL:\n{command[:100]}...\n{e}")
        conn.commit()
    print("✅ База данных успешно заполнена.")

def clear_database():
    print("⚠️ Очистка базы данных...")
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            for table in reversed(Base.metadata.sorted_tables):
                conn.execute(text(f"TRUNCATE TABLE `{table.name}`"))
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            trans.commit()
            print("✅ Все таблицы успешно очищены.")
        except Exception as e:
            trans.rollback()
            print(f"❌ Ошибка при очистке: {e}")

if __name__ == "__main__":
    import sys

    if "clear" in sys.argv:
        clear_database()
    elif "populate" in sys.argv:
        populate_database()
    else:
        print("ℹ️ Используй: python database.py [clear | populate]")