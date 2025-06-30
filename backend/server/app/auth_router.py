from fastapi import APIRouter, Depends, HTTPException, Request, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .schemas import UserCreate, UserLogin
from .models import User, Session
from .database import get_db
from .auth_utils import SESSION_EXPIRE_HOURS, create_session_token, get_session_expiration

router = APIRouter()

@router.post("/login")
async def login(
    response: Response,
    user_data: UserLogin,  # Используем схему для авторизации
    db: Session = Depends(get_db)
):
    # Добавляем CORS заголовки
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:8080"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    
    user = db.query(User).filter(User.Email == user_data.Email).first()
    
    if not user or not user.check_password(user_data.Password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )
    
    # Создаем новую сессию
    session_token = create_session_token()
    expires_at = get_session_expiration()
    
    new_session = Session(
        SessionToken=session_token,
        UserId=user.IdUser,
        ExpiresAt=expires_at
    )
    
    db.add(new_session)
    db.commit()
    
    # Устанавливаем cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=SESSION_EXPIRE_HOURS * 3600,
        secure=False,  # Изменено на False для HTTP
        samesite="Lax"
    )
    
    # Возвращаем данные пользователя
    return {
        "message": "Успешная авторизация",
        "user": {
            "IdUser": user.IdUser,
            "FirstName": user.FirstName,
            "LastName": user.LastName,
            "SecondName": user.SecondName,
            "Email": user.Email,
            "UserName": user.UserName,
            "Rating": user.Rating,
            "CreatedAt": user.CreatedAt,
            "Enabled": user.Enabled,
            "IsStaff": user.IsStaff
        }
    }

@router.options("/login")
async def login_options(response: Response):
    # Обработка preflight запросов
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:8080"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return {"message": "OK"}

@router.post("/logout")
async def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    session_token = request.cookies.get("session_token")
    if session_token:
        # Удаляем сессию из БД
        db.query(Session).filter(Session.SessionToken == session_token).delete()
        db.commit()
    
    # Очищаем cookie
    response.delete_cookie("session_token")
    return {"message": "Вы вышли из системы"}

@router.post("/refresh")
async def refresh_session(response: Response, request: Request, db: Session = Depends(get_db)):
    old_token = request.cookies.get("session_token")
    if not old_token:
        raise HTTPException(status_code=401, detail="Сессия не найдена")
    
    # Создаем новую сессию
    new_token = create_session_token()
    expires_at = get_session_expiration()
    
    # Находим старую сессию
    session = db.query(Session).filter(Session.SessionToken == old_token).first()
    if not session:
        raise HTTPException(status_code=401, detail="Недействительная сессия")
    
    # Создаем новую сессию для того же пользователя
    new_session = Session(
        SessionToken=new_token,
        UserId=session.UserId,
        ExpiresAt=expires_at
    )
    
    db.add(new_session)
    db.delete(session)  # Удаляем старую сессию
    db.commit()
    
    # Устанавливаем новую cookie
    response.set_cookie(
        key="session_token",
        value=new_token,
        httponly=True,
        max_age=SESSION_EXPIRE_HOURS * 3600,
        secure=False,
        samesite="Lax"
    )
    
    return {"message": "Сессия обновлена"}