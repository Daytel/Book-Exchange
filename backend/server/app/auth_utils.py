import uuid
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os

# Настройки
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
SESSION_EXPIRE_HOURS = 1

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_session_token() -> str:
    return str(uuid.uuid4())

def get_session_expiration() -> datetime:
    return datetime.utcnow() + timedelta(hours=SESSION_EXPIRE_HOURS)