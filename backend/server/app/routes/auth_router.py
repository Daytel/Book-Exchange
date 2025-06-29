from fastapi import APIRouter, Depends, HTTPException, Request, status, Response
from sqlalchemy.orm import Session
from ..schemas import LoginRequest, LoginResponse, UserAuthResponse
from ..models import User, Session
from ..database import get_db
from ..auth_utils import SESSION_EXPIRE_HOURS, create_session_token, get_session_expiration

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(
    response: Response,
    user_data: LoginRequest,  # Используем схему для входа
    db: Session = Depends(get_db)
):
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
        secure=True,
        samesite="Lax"
    )
    
    # Создаем объект пользователя для ответа (без пароля)
    user_response = UserAuthResponse(
        IdUser=user.IdUser,
        FirstName=user.FirstName,
        LastName=user.LastName,
        SecondName=user.SecondName,
        Email=user.Email,
        UserName=user.UserName,
        Rating=user.Rating,
        CreatedAt=user.CreatedAt,
        Enabled=user.Enabled,
        Avatar=user.Avatar,
        IsStaff=user.IsStaff
    )
    
    return LoginResponse(
        message="Успешная авторизация",
        user=user_response
    )

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
        secure=True,
        samesite="Lax"
    )
    
    return {"message": "Сессия обновлена"}

@router.get("/me", response_model=UserAuthResponse)
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="Сессия не найдена")
    
    # Находим сессию
    session = db.query(Session).filter(Session.SessionToken == session_token).first()
    if not session:
        raise HTTPException(status_code=401, detail="Недействительная сессия")
    
    # Получаем пользователя
    user = db.query(User).filter(User.IdUser == session.UserId).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return UserAuthResponse(
        IdUser=user.IdUser,
        FirstName=user.FirstName,
        LastName=user.LastName,
        SecondName=user.SecondName,
        Email=user.Email,
        UserName=user.UserName,
        Rating=user.Rating,
        CreatedAt=user.CreatedAt,
        Enabled=user.Enabled,
        Avatar=user.Avatar,
        IsStaff=user.IsStaff
    ) 