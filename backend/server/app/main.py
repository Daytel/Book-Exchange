from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse, RedirectResponse
from typing import Optional
import secrets
from pydantic import BaseModel

from app import models
from .database import engine, Base, populate_database
# Добавить написанные routes
# from .routes import students, tasks, classes, journal, gamefields, solutions
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import get_db
import os

Base.metadata.create_all(bind=engine)

# Запуск: uvicorn app.main:app --reload
# Чистка: python app/database.py clear

app = FastAPI()

populate_database()

@app.get("/")
def read_root():
    return {"message": "Welcome to Book Exchange API"}


# Добавить routes

@app.get('/')
def read_root():
    return {'message': 'Обмен книгами API'}

