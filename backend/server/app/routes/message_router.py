from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import UserMsg, User, Status
from ..schemas import UserMsgCreate, UserMsgResponse, StatusResponse
import aiosmtplib
from email.message import EmailMessage

router = APIRouter()

SMTP_HOST = "smtp.yandex.ru"  # или smtp.gmail.com
SMTP_PORT = 587
SMTP_USER = "your_email@yandex.ru"
SMTP_PASS = "your_password"

async def send_email(to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASS,
        start_tls=True,
    )

@router.post("/messages/", response_model=UserMsgResponse)
async def create_message(msg: UserMsgCreate, db: Session = Depends(get_db)):
    db_msg = UserMsg(
        IdUser=msg.IdUser,
        CreateAt=datetime.utcnow(),
        Text=msg.Text,
        Notes=msg.Notes,
        IdStatus=msg.IdStatus,
        Type=msg.Type
    )
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)

    user = db.query(User).filter(User.IdUser == msg.IdUser).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # await send_email(
    #     to_email=user.Email,
    #     subject="Новое сообщение",
    #     body=msg.Text
    # )

    # Добавить StatusName вручную
    status_name = db_msg.status.Name if db_msg.status else ""
    return {
        **db_msg.__dict__,
        "StatusName": status_name
    }

@router.get("/messages/received", response_model=list[UserMsgResponse])
async def get_received_messages(user_id: int, db: Session = Depends(get_db)):
    messages = db.query(UserMsg).filter(UserMsg.IdUser == user_id).order_by(UserMsg.CreateAt.desc()).all()
    result = []
    for msg in messages:
        status_name = msg.status.Name if msg.status else ""
        result.append({
            **msg.__dict__,
            "StatusName": status_name
        })
    return result

@router.get("/statuses/", response_model=list[StatusResponse])
async def get_statuses(db: Session = Depends(get_db)):
    statuses = db.query(Status).all()
    return statuses

@router.delete("/messages/{msg_id}", status_code=204)
async def delete_message(msg_id: int, db: Session = Depends(get_db)):
    msg = db.query(UserMsg).filter(UserMsg.IdUserMsg == msg_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(msg)
    db.commit()
    return 