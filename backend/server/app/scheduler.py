from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import ExchangeList, User, OfferList, UserExchangeList, UserList, UserValueCategory, UserAddress
from datetime import datetime, timedelta

def remove_expired_exchanges():
    db: Session = SessionLocal()
    now = datetime.utcnow()
    expired = db.query(ExchangeList).filter(ExchangeList.CreateAt < now - timedelta(days=2)).all()
    for exch in expired:
        db.delete(exch)
    db.commit()
    db.close()

def block_and_cleanup_users_without_tracking():
    db: Session = SessionLocal()
    now = datetime.utcnow()
    # 1. Найти все ExchangeList, где прошло больше 7 дней, а трек-номер не отправлен
    expired_exchanges = db.query(ExchangeList).filter(
        ExchangeList.CreateAt < now - timedelta(days=7)
    ).all()
    users_to_block = set()
    for exch in expired_exchanges:
        for offer_id in [exch.IdOfferList1, exch.IdOfferList2]:
            uel = db.query(UserExchangeList).filter(UserExchangeList.IdOfferList == offer_id).first()
            if uel and not uel.TrackNumber:
                offer = db.query(OfferList).filter(OfferList.IdOfferList == offer_id).first()
                if offer:
                    users_to_block.add(offer.IdUser)
    # 2. Блокируем пользователей и удаляем их данные
    for user_id in users_to_block:
        user = db.query(User).filter(User.IdUser == user_id).first()
        if user:
            user.Enabled = False
            # Удаляем адреса
            db.query(UserAddress).filter(UserAddress.IdUser == user_id).delete()
            # Удаляем OfferList и связанные UserList/UserValueCategory
            offers = db.query(OfferList).filter(OfferList.IdUser == user_id).all()
            for offer in offers:
                user_lists = db.query(UserList).filter(UserList.IdOfferList == offer.IdOfferList).all()
                for ul in user_lists:
                    db.query(UserValueCategory).filter(UserValueCategory.IdUserList == ul.IdUserList).delete()
                    db.delete(ul)
                db.query(UserExchangeList).filter(UserExchangeList.IdOfferList == offer.IdOfferList).delete()
                db.delete(offer)
            # Удаляем все ExchangeList, где участвовал пользователь
            db.query(ExchangeList).filter(
                (ExchangeList.IdOfferList1.in_([o.IdOfferList for o in offers])) |
                (ExchangeList.IdOfferList2.in_([o.IdOfferList for o in offers]))
            ).delete(synchronize_session=False)
    db.commit()
    db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(remove_expired_exchanges, 'interval', hours=1)  # Проверка каждый час
    scheduler.add_job(block_and_cleanup_users_without_tracking, 'interval', hours=24)
    scheduler.start()
