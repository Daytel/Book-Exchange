from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse, RedirectResponse
from typing import Optional
import secrets
from pydantic import BaseModel

from app import models

from .routes.auth_router import router as auth_router
from .routes.message_router import router as message_router

from .database import engine, Base, get_current_user, populate_database
# Добавить написанные routes
# from .routes import students, tasks, classes, journal, gamefields, solutions
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import get_db
import os

# Запуск: uvicorn app.main:app --reload
# Чистка: python app/database.py clear

app = FastAPI()

# Создаем таблицы и заполняем базу данных
print("🚀 Инициализация базы данных...")
populate_database()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:8080",
        "http://localhost:4200",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:4200",
    ],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутер аутентификации
app.include_router(auth_router, prefix="/auth", tags=["auth"])


# Подключаем роутер сообщений
app.include_router(message_router, prefix="/api", tags=["messages"])

# Пример защищенного роута
@app.get("/protected-data")
async def get_protected_data(current_user: models.User = Depends(get_current_user)):
    return {"data": "Секретные данные", "user": current_user.Email}

