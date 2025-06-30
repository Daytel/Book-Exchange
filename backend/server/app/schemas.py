from datetime import datetime, date
from typing import Optional, List, Union, Annotated
from pydantic import BaseModel, EmailStr, constr, field_validator, ConfigDict, Field
import re

# Специальный тип для пароля
PasswordStr = Annotated[
    str,
    Field(..., min_length=8, max_length=15)
]

# --------------- User Schemas ---------------
class UserBase(BaseModel):
    FirstName: str
    LastName: str
    SecondName: Optional[str] = None
    Email: EmailStr
    UserName: str
    Password: PasswordStr
    Rating: float = 0.0
    CreatedAt: datetime
    Enabled: bool = True
    Avatar: Optional[bytes] = None
    IsStaff: bool = False
    
    @field_validator('Password')
    def validate_password(cls, v):
        # Проверяем наличие заглавной буквы (латиница или кириллица)
        if not re.search(r'[A-ZА-Я]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        # Проверяем наличие цифры
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        # Проверяем, что пароль содержит только буквы и цифры (латиница и кириллица)
        if re.search(r'[^a-zA-Zа-яёЁ0-9]', v):
            raise ValueError('Password must contain only letters and digits')
        return v

# Схема для авторизации
class UserLogin(BaseModel):
    Email: EmailStr
    Password: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    IdUser: int
    model_config = ConfigDict(from_attributes=True)

# Схема для ответа авторизации (без пароля)
class UserAuthResponse(BaseModel):
    IdUser: int
    FirstName: str
    LastName: str
    SecondName: Optional[str] = None
    Email: str
    UserName: str
    Rating: float
    CreatedAt: datetime
    Enabled: bool
    Avatar: Optional[bytes] = None
    IsStaff: bool
    model_config = ConfigDict(from_attributes=True)

# Схема для ответа авторизации
class LoginResponse(BaseModel):
    message: str
    user: UserAuthResponse

# Схема для входа в систему
class LoginRequest(BaseModel):
    Email: EmailStr
    Password: str

# --------------- Autor Schemas ---------------
class AutorBase(BaseModel):
    LastName: str
    FirstName: Optional[str] = None

class AutorCreate(AutorBase):
    pass

class AutorResponse(AutorBase):
    IdAutor: int
    model_config = ConfigDict(from_attributes=True)

# --------------- BookLiterary Schemas ---------------
class BookLiteraryBase(BaseModel):
    IdAutor: int
    BookName: str
    Note: Optional[str] = None
    ISBN: Optional[str] = None
    YearPublishing: date

class BookLiteraryCreate(BookLiteraryBase):
    pass

class BookLiteraryResponse(BookLiteraryBase):
    IdBookLiterary: int
    model_config = ConfigDict(from_attributes=True)

# --------------- Status Schemas ---------------
class StatusBase(BaseModel):
    Name: str = 'свободен'

class StatusCreate(StatusBase):
    pass

class StatusResponse(StatusBase):
    IdStatus: int
    model_config = ConfigDict(from_attributes=True)

# --------------- OfferList Schemas ---------------
class OfferListBase(BaseModel):
    IdBookLiterary: int
    IdUser: int
    CreateAt: datetime
    UpdateAt: datetime
    IdStatus: int

class OfferListCreate(OfferListBase):
    pass

class OfferListResponse(OfferListBase):
    IdOfferList: int
    model_config = ConfigDict(from_attributes=True)

# --------------- UserAddress Schemas ---------------
class UserAddressBase(BaseModel):
    IdUser: int
    AddrIndex: str
    AddrCity: str
    AddrStreet: str
    AddrHouse: str
    AddrStructure: Optional[str] = None
    AddrApart: Optional[str] = None
    
    @field_validator('AddrIndex')
    def validate_index(cls, v):
        if not re.match(r'^\d{6}$', v):
            raise ValueError('Postal index must be 6 digits')
        return v

class UserAddressCreate(UserAddressBase):
    pass

class UserAddressResponse(UserAddressBase):
    idUserAddress: int
    model_config = ConfigDict(from_attributes=True)

# --------------- WishList Schemas ---------------
class WishListBase(BaseModel):
    IdUser: int
    CreatedAt: datetime
    UpdateAt: datetime
    IdStatus: int
    IdUserAddress: int

class WishListCreate(WishListBase):
    pass

class WishListResponse(WishListBase):
    IdWishList: int
    model_config = ConfigDict(from_attributes=True)

# --------------- UserMsg Schemas ---------------
class UserMsgBase(BaseModel):
    IdUser: int
    CreateAt: datetime
    Text: str
    Notes: Optional[str] = None
    IdStatus: int
    Type: bool

class UserMsgCreate(UserMsgBase):
    pass

class UserMsgResponse(UserMsgBase):
    IdUserMsg: int
    model_config = ConfigDict(from_attributes=True)

# --------------- ExchangeList Schemas ---------------
class ExchangeListBase(BaseModel):
    IdOfferList1: int
    IdWishList1: int
    IdOfferList2: int
    IdWishList2: int
    CreateAt: datetime
    IsBoth: bool = False

class ExchangeListCreate(ExchangeListBase):
    pass

class ExchangeListResponse(ExchangeListBase):
    IdExchangeList: int
    model_config = ConfigDict(from_attributes=True)

# --------------- UserExchangeList Schemas ---------------
class UserExchangeListBase(BaseModel):
    IdOfferList: int
    TrackNumber: Optional[str] = None
    Receiving: bool

class UserExchangeListCreate(UserExchangeListBase):
    pass

class UserExchangeListResponse(UserExchangeListBase):
    IdUserExchangeList: int
    model_config = ConfigDict(from_attributes=True)

# --------------- Category Schemas ---------------
class CategoryBase(BaseModel):
    Name: str
    IdParent: int = 0
    MultySelect: bool = False

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    IdCategory: int
    model_config = ConfigDict(from_attributes=True)

# --------------- BookResponse Schemas ---------------
class BookResponseBase(BaseModel):
    IdBookLiterary: int
    IdUser: int
    CreateAt: datetime
    Response: str
    Note: Optional[str] = None

class BookResponseCreate(BookResponseBase):
    pass

class BookResponseResponse(BookResponseBase):
    model_config = ConfigDict(from_attributes=True)

# --------------- UserList Schemas ---------------
class UserListBase(BaseModel):
    IdOfferList: Optional[int] = None
    IdWishList: Optional[int] = None

class UserListCreate(UserListBase):
    pass

class UserListResponse(UserListBase):
    IdUserList: int
    model_config = ConfigDict(from_attributes=True)

# --------------- UserValueCategory Schemas ---------------
class UserValueCategoryBase(BaseModel):
    IdUserList: int
    IdCategory: int

class UserValueCategoryCreate(UserValueCategoryBase):
    pass

class UserValueCategoryResponse(UserValueCategoryBase):
    model_config = ConfigDict(from_attributes=True)

# --------------- Sessions ---------------
class SessionCreate(BaseModel):
    UserId: int

class SessionResponse(BaseModel):
    IdSession: int
    SessionToken: str
    UserId: int
    CreatedAt: datetime
    ExpiresAt: datetime
    
    class Config:
        from_attributes = True