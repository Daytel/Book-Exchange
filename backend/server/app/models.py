from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, Date, LargeBinary, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import re
from .auth_utils import get_password_hash, verify_password

Base = declarative_base()

class User(Base):
    __tablename__ = 'User'
    
    IdUser = Column(Integer, primary_key=True, autoincrement=True)
    FirstName = Column(String(25), nullable=False)
    LastName = Column(String(50), nullable=False)
    SecondName = Column(String(25))
    Email = Column(String(50), nullable=False)
    UserName = Column(String(20), nullable=False)
    Password = Column(String(255), nullable=False) # Изменил на 255 для хеша
    Rating = Column(Float, default=0.0)
    CreatedAt = Column(DateTime, nullable=False)
    Enabled = Column(Boolean, default=True)
    Avatar = Column(LargeBinary)
    IsStaff = Column(Boolean, default=False)

    # Методы для работы с паролем
    def set_password(self, password: str):
        """Хеширует и устанавливает пароль"""
        self.Password = get_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Проверяет пароль против хеша или простого текста"""
        try:
            # Сначала пробуем проверить как хеш
            return verify_password(password, self.Password)
        except Exception:
            # Если не получилось, сравниваем как простой текст
            return password == self.Password

    
    __table_args__ = (
        CheckConstraint('LENGTH(Password) >= 8', name='password_length'),
        CheckConstraint('Password REGEXP "^.*[A-ZА-Я].*$"', name='password_uppercase'),
        CheckConstraint('Password REGEXP "^.*[0-9].*$"', name='password_digit'),
        CheckConstraint('Email LIKE "%@%"', name='valid_email'),
    )
    

class Autor(Base):
    __tablename__ = 'Autor'
    
    IdAutor = Column(Integer, primary_key=True, autoincrement=True)
    FirstName = Column(String(20))
    LastName = Column(String(50), nullable=False)

class BookLiterary(Base):
    __tablename__ = 'BookLiterary'
    
    IdBookLiterary = Column(Integer, primary_key=True, autoincrement=True)
    IdAutor = Column(Integer, ForeignKey('Autor.IdAutor'), nullable=False)
    BookName = Column(String(50), nullable=False)
    Note = Column(String(50))
    ISBN = Column(String(13))
    YearPublishing = Column(Date, nullable=False)
    
    autor = relationship("Autor")

class Status(Base):
    __tablename__ = 'Status'
    
    IdStatus = Column(Integer, primary_key=True)
    Name = Column(String(10), default='свободен')

class OfferList(Base):
    __tablename__ = 'OfferList'
    
    IdOfferList = Column(Integer, primary_key=True, autoincrement=True)
    IdBookLiterary = Column(Integer, ForeignKey('BookLiterary.IdBookLiterary'), nullable=False)
    IdUser = Column(Integer, ForeignKey('User.IdUser'), nullable=False)
    CreateAt = Column(DateTime, nullable=False)
    UpdateAt = Column(DateTime, nullable=False)
    IdStatus = Column(Integer, ForeignKey('Status.IdStatus'), nullable=False)
    
    book = relationship("BookLiterary")
    user = relationship("User")
    status = relationship("Status")

class UserAddress(Base):
    __tablename__ = 'UserAddress'
    
    idUserAddress = Column(Integer, primary_key=True, autoincrement=True)
    IdUser = Column(Integer, ForeignKey('User.IdUser'), nullable=False)
    AddrIndex = Column(String(6), nullable=False)
    AddrCity = Column(String(15), nullable=False)
    AddrStreet = Column(String(25), nullable=False)
    AddrHouse = Column(String(5), nullable=False)
    AddrStructure = Column(String(10))
    AddrApart = Column(String(3))
    
    __table_args__ = (
        CheckConstraint('AddrIndex REGEXP "^[0-9]{6}$"', name='valid_index'),
    )

class WishList(Base):
    __tablename__ = 'WishList'
    
    IdWishList = Column(Integer, primary_key=True, autoincrement=True)
    IdUser = Column(Integer, ForeignKey('User.IdUser'), nullable=False)
    CreatedAt = Column(DateTime, nullable=False)
    UpdateAt = Column(DateTime, nullable=False)
    IdStatus = Column(Integer, ForeignKey('Status.IdStatus'), nullable=False)
    IdUserAddress = Column(Integer, ForeignKey('UserAddress.idUserAddress'), nullable=False)
    
    user = relationship("User")
    status = relationship("Status")
    address = relationship("UserAddress")

class UserMsg(Base):
    __tablename__ = 'UserMsg'
    
    IdUserMsg = Column(Integer, primary_key=True, autoincrement=True)
    IdUser = Column(Integer, ForeignKey('User.IdUser'), nullable=False)
    CreateAt = Column(DateTime, nullable=False)
    Text = Column(String(250), nullable=False)
    Notes = Column(String(150))
    IdStatus = Column(Integer, ForeignKey('Status.IdStatus'), nullable=False)
    Type = Column(Boolean, nullable=False)
    
    user = relationship("User")
    status = relationship("Status")

class ExchangeList(Base):
    __tablename__ = 'ExchangeList'
    
    IdExchangeList = Column(Integer, primary_key=True, autoincrement=True)
    IdOfferList1 = Column(Integer, ForeignKey('OfferList.IdOfferList'), nullable=False)
    IdWishList1 = Column(Integer, ForeignKey('WishList.IdWishList'), nullable=False)
    IdOfferList2 = Column(Integer, ForeignKey('OfferList.IdOfferList'), nullable=False)
    IdWishList2 = Column(Integer, ForeignKey('WishList.IdWishList'), nullable=False)
    CreateAt = Column(DateTime, nullable=False)
    IsBoth = Column(Boolean, default=False)
    
    offer1 = relationship("OfferList", foreign_keys=[IdOfferList1])
    wish1 = relationship("WishList", foreign_keys=[IdWishList1])
    offer2 = relationship("OfferList", foreign_keys=[IdOfferList2])
    wish2 = relationship("WishList", foreign_keys=[IdWishList2])

class UserExchangeList(Base):
    __tablename__ = 'UserExchangeList'
    
    IdUserExchangeList = Column(Integer, primary_key=True, autoincrement=True)
    IdOfferList = Column(Integer, ForeignKey('OfferList.IdOfferList'), nullable=False)
    TrackNumber = Column(String(14))
    Receiving = Column(Boolean, nullable=False)
    
    offer = relationship("OfferList")

class Category(Base):
    __tablename__ = 'Category'
    
    IdCategory = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String(25), nullable=False)
    IdParent = Column(Integer, ForeignKey('Category.IdCategory'), default=0)
    MultySelect = Column(Boolean, default=False)
    
    parent = relationship("Category", remote_side=[IdCategory])

class BookResponse(Base):
    __tablename__ = 'BookResponse'
    
    IdBookLiterary = Column(Integer, ForeignKey('BookLiterary.IdBookLiterary'), primary_key=True)
    IdUser = Column(Integer, ForeignKey('User.IdUser'), primary_key=True)
    CreateAt = Column(DateTime, nullable=False)
    Response = Column(String(500), nullable=False)
    Note = Column(String(50))
    
    book = relationship("BookLiterary")
    user = relationship("User")

class UserList(Base):
    __tablename__ = 'UserList'
    
    IdUserList = Column(Integer, primary_key=True, autoincrement=True)
    IdOfferList = Column(Integer, ForeignKey('OfferList.IdOfferList'))
    IdWishList = Column(Integer, ForeignKey('WishList.IdWishList'))
    
    offer = relationship("OfferList")
    wish = relationship("WishList")

class UserValueCategory(Base):
    __tablename__ = 'UserValueCategory'
    
    IdUserList = Column(Integer, ForeignKey('UserList.IdUserList'), primary_key=True)
    IdCategory = Column(Integer, ForeignKey('Category.IdCategory'), primary_key=True)
    
    user_list = relationship("UserList")
    category = relationship("Category")

class Session(Base):
    __tablename__ = 'Session'
    
    IdSession = Column(Integer, primary_key=True, autoincrement=True)
    SessionToken = Column(String(36), unique=True, nullable=False)
    UserId = Column(Integer, ForeignKey('User.IdUser'), nullable=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    ExpiresAt = Column(DateTime, nullable=False)
    
    # Связь с пользователем
    user = relationship("User")