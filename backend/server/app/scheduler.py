from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import ExchangeList, User, OfferList, UserExchangeList, UserList, UserValueCategory, UserAddress, UserMsg
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
    # 1. Найти все ExchangeList, где прошло больше 8 дней, а трек-номер не отправлен
    expired_exchanges = db.query(ExchangeList).filter(
        ExchangeList.CreateAt < now - timedelta(days=8)
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
    admins = db.query(User).filter(User.IsStaff == True).all()
    for user_id in users_to_block:
        user = db.query(User).filter(User.IdUser == user_id).first()
        if user:
            # 2.1 Сообщение пользователю
            text_user = "Ваш доступ к приложению закрыт."
            exists_user = db.query(UserMsg).filter_by(IdUser=user_id, IdStatus=22, Type=True, Text=text_user).first()
            if not exists_user:
                user_msg = UserMsg(
                    IdUser=user_id,
                    CreateAt=datetime.utcnow(),
                    Text=text_user,
                    Notes=None,
                    IdStatus=22,
                    Type=True
                )
                db.add(user_msg)
            # 2.2 Сообщение администраторам
            fio = f"{user.LastName} {user.FirstName} {user.SecondName or ''}".strip()
            nickname = user.UserName
            text_admin = f"{fio} с никнеймом {nickname} был заблокирован"
            for admin in admins:
                exists_admin = db.query(UserMsg).filter_by(IdUser=admin.IdUser, IdStatus=22, Type=True, Text=text_admin).first()
                if not exists_admin:
                    admin_msg = UserMsg(
                        IdUser=admin.IdUser,
                        CreateAt=datetime.utcnow(),
                        Text=text_admin,
                        Notes=None,
                        IdStatus=22,
                        Type=True
                    )
                    db.add(admin_msg)
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

def remind_users_about_tracking():
    db: Session = SessionLocal()
    now = datetime.utcnow()
    # Найти все ExchangeList, подтверждённые более 6 дней назад
    exchanges = db.query(ExchangeList).filter(ExchangeList.CreateAt < now - timedelta(days=6), ExchangeList.IsBoth == True).all()
    for exch in exchanges:
        for offer_id in [exch.IdOfferList1, exch.IdOfferList2]:
            uel = db.query(UserExchangeList).filter(UserExchangeList.IdOfferList == offer_id).first()
            if uel and not uel.TrackNumber:
                offer = db.query(OfferList).filter(OfferList.IdOfferList == offer_id).first()
                if offer:
                    book = offer.book
                    author = book.autor.LastName if book and book.autor else ''
                    title = book.BookName if book else ''
                    text = f"Укажите трек-номер отправленной книги {author}, {title}."
                    # Проверяем, не отправляли ли уже такое сообщение (по IdStatus=12, Type=1, Text)
                    exists = db.query(UserMsg).filter_by(IdUser=offer.IdUser, IdStatus=12, Type=True, Text=text).first()
                    if not exists:
                        user_msg = UserMsg(
                            IdUser=offer.IdUser,
                            CreateAt=datetime.utcnow(),
                            Text=text,
                            Notes=None,
                            IdStatus=12,
                            Type=True
                        )
                        db.add(user_msg)
    db.commit()
    db.close()

def warn_users_and_admins_about_tracking():
    db: Session = SessionLocal()
    now = datetime.utcnow()
    # Найти все ExchangeList, подтверждённые более 7 дней назад
    exchanges = db.query(ExchangeList).filter(ExchangeList.CreateAt < now - timedelta(days=7), ExchangeList.IsBoth == True).all()
    admins = db.query(User).filter(User.IsStaff == True).all()
    for exch in exchanges:
        for offer_id in [exch.IdOfferList1, exch.IdOfferList2]:
            uel = db.query(UserExchangeList).filter(UserExchangeList.IdOfferList == offer_id).first()
            if uel and not uel.TrackNumber:
                offer = db.query(OfferList).filter(OfferList.IdOfferList == offer_id).first()
                if offer:
                    book = offer.book
                    author = book.autor.LastName if book and book.autor else ''
                    title = book.BookName if book else ''
                    user = offer.user
                    nickname = user.UserName if user else ''
                    # 1. Сообщение пользователю
                    deadline = (exch.CreateAt + timedelta(days=8)).strftime('%d.%m.%Y')
                    text_user = f"В случае отсутствия до {deadline} в карточке обмена трек-номера, у вас будет закрыт доступ к приложению."
                    exists_user = db.query(UserMsg).filter_by(IdUser=offer.IdUser, IdStatus=12, Type=True, Text=text_user).first()
                    if not exists_user:
                        user_msg = UserMsg(
                            IdUser=offer.IdUser,
                            CreateAt=datetime.utcnow(),
                            Text=text_user,
                            Notes=None,
                            IdStatus=12,
                            Type=True
                        )
                        db.add(user_msg)
                    # 2. Сообщение администраторам
                    text_admin = f"Пользователь {nickname} задерживает отправку книги {author}, {title}."
                    for admin in admins:
                        exists_admin = db.query(UserMsg).filter_by(IdUser=admin.IdUser, IdStatus=12, Type=True, Text=text_admin).first()
                        if not exists_admin:
                            admin_msg = UserMsg(
                                IdUser=admin.IdUser,
                                CreateAt=datetime.utcnow(),
                                Text=text_admin,
                                Notes=None,
                                IdStatus=12,
                                Type=True
                            )
                            db.add(admin_msg)
    db.commit()
    db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(remove_expired_exchanges, 'interval', hours=1)  # Проверка каждый час
    scheduler.add_job(block_and_cleanup_users_without_tracking, 'interval', hours=8)
    scheduler.add_job(remind_users_about_tracking, 'interval', hours=8)
    scheduler.add_job(warn_users_and_admins_about_tracking, 'interval', hours=8)
    scheduler.start()
