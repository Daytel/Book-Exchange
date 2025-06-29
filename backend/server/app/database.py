from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status, Request
from .models import Session as SessionModel, User
from passlib.context import CryptContext

# Загрузка переменных окружения
load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    echo=False,          # Логирование SQL (True для отладки)
    connect_args={"init_command": "SET sql_mode='STRICT_TRANS_TABLES'"}
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
    init_db_path = os.path.join(BASE_DIR, "db", "init-db.sql")
    test_data_path = os.path.join(BASE_DIR, "db", "test_data.sql")

    # Сначала очищаем базу данных
    print("🧹 Очистка базы данных...")
    clear_database()

    # Сначала создаем таблицы из init-db.sql
    if os.path.exists(init_db_path):
        print("🔧 Создание таблиц из init-db.sql...")
        with open(init_db_path, encoding="utf-8") as f:
            init_sql = f.read()

        with engine.connect() as conn:
            try:
                # Заменяем проблемные команды на правильные
                init_sql = init_sql.replace('SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;', 'SET UNIQUE_CHECKS=0;')
                init_sql = init_sql.replace('SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;', 'SET FOREIGN_KEY_CHECKS=0;')
                init_sql = init_sql.replace('SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE=', 'SET SQL_MODE=')
                init_sql = init_sql.replace('SET SQL_MODE=@OLD_SQL_MODE;', "SET SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';")
                init_sql = init_sql.replace('SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;', 'SET FOREIGN_KEY_CHECKS=1;')
                init_sql = init_sql.replace('SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;', 'SET UNIQUE_CHECKS=1;')
                
                # Разбиваем на отдельные команды, учитывая многострочные CREATE TABLE
                statements = []
                current_statement = ""
                in_create_table = False
                paren_count = 0
                
                for line in init_sql.split('\n'):
                    line = line.strip()
                    if not line or line.startswith('--') or line.startswith('/*'):
                        continue
                    
                    current_statement += line + " "
                    
                    # Отслеживаем скобки для CREATE TABLE
                    if 'CREATE TABLE' in line.upper():
                        in_create_table = True
                    
                    if in_create_table:
                        paren_count += line.count('(') - line.count(')')
                        if paren_count == 0 and line.endswith(';'):
                            in_create_table = False
                            statements.append(current_statement.strip())
                            current_statement = ""
                    elif line.endswith(';'):
                        statements.append(current_statement.strip())
                        current_statement = ""
                
                # Выполняем каждую команду отдельно
                for statement in statements:
                    if statement.strip():
                        try:
                            conn.execute(text(statement))
                            print(f"✅ Выполнена команда: {statement[:50]}...")
                        except Exception as e:
                            print(f"⚠️ Ошибка при выполнении: {statement[:50]}...\n{e}")
                
                conn.commit()
                print("✅ Таблицы созданы")
            except Exception as e:
                print(f"⚠️ Ошибка при создании таблиц: {e}")
                conn.rollback()
                raise

    if not os.path.exists(test_data_path):
        print(f"Файл не найден: {test_data_path}")
        return

    print("📥 Заполнение базы данных из test_data.sql...")
    
    with open(test_data_path, encoding="utf-8") as f:
        sql_commands = f.read()

    # Исправляем названия колонок в SQL
    # Заменяем только в таблице Category, но не в Status
    sql_commands = sql_commands.replace('`Category`.`Name`', '`Category`.`Value`')
    sql_commands = sql_commands.replace('`Category_IdCategory`', '`IdValueCategory`')  # UserValueCategory

    with engine.connect() as conn:
        # Сначала выполняем все НЕ-пользовательские команды
        for command in sql_commands.split(';'):
            command = command.strip()
            if command and "UNHASHED_PASSWORD" not in command and not command.startswith('/*'):
                try:
                    conn.execute(text(command))
                except Exception as e:
                    print(f"⚠️ Ошибка при выполнении SQL:\n{command[:100]}...\n{e}")
        
        # Затем отдельно обрабатываем пользователей с хешированием
        for command in sql_commands.split(';'):
            command = command.strip()
            if command and "UNHASHED_PASSWORD" in command:
                try:
                    # Извлекаем незахешированный пароль
                    unhashed_start = command.find("'UNHASHED_PASSWORD:") + 19
                    unhashed_end = command.find("'", unhashed_start)
                    raw_password = command[unhashed_start:unhashed_end]
                    
                    # Хешируем пароль
                    hashed_password = pwd_context.hash(raw_password)
                    
                    # Модифицируем SQL
                    safe_command = command.replace(f"'UNHASHED_PASSWORD:{raw_password}'", f"'{hashed_password}'")
                    
                    conn.execute(text(safe_command))
                except Exception as e:
                    print(f"⚠️ Ошибка при обработке пользователя:\n{command[:100]}...\n{e}")
        
        conn.commit()
    
    print("✅ База данных успешно заполнена с хешированными паролями.")

# Если нужно перехешировать существующих пользователей
def hash_existing_passwords():
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.Password.like("UNHASHED_PASSWORD:%")).all()
        for user in users:
            raw_password = user.Password.split(":")[1]
            user.set_password(raw_password)
        db.commit()
    finally:
        db.close()

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

def get_current_user(request: Request, db: Session = Depends(get_db)):
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Сессия не найдена"
        )
    
    session = db.query(SessionModel).filter(
        SessionModel.SessionToken == session_token
    ).first()
    
    if not session or session.ExpiresAt < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительная сессия"
        )
    
    return session.user