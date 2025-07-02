from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import Category, ValueCategory, OfferList, BookLiterary, Autor, UserList, UserValueCategory, WishList, UserAddress, User
from ..schemas import CategoryResponse, ValueCategoryResponse, UserAddressResponse, UserAddressBase
from typing import List, Dict, Any
from datetime import datetime
from ..database import recalculate_user_rating

router = APIRouter()

@router.get("/full", response_model=List[Dict[str, Any]])
def get_categories_with_values(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    result = []
    for cat in categories:
        values = db.query(ValueCategory).filter(ValueCategory.IdCategory == cat.IdCategory).all()
        result.append({
            "IdCategory": cat.IdCategory,
            "Value": cat.Value,
            "MultySelect": cat.MultySelect,
            "values": [
                {"IdValueCategory": v.IdValueCategory, "Value": v.Value} for v in values
            ]
        })
    return result

@router.get("/offer-list/{id}")
def get_offer_list_by_id(id: int, db: Session = Depends(get_db)):
    offer = db.query(OfferList).filter(OfferList.IdOfferList == id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="OfferList not found")
    book = db.query(BookLiterary).filter(BookLiterary.IdBookLiterary == offer.IdBookLiterary).first()
    autor = db.query(Autor).filter(Autor.IdAutor == book.IdAutor).first() if book else None
    # Получаем UserList по IdOfferList
    user_list = db.query(UserList).filter(UserList.IdOfferList == id).first()
    selected_categories = []
    if user_list:
        user_value_cats = db.query(UserValueCategory).filter(UserValueCategory.IdUserList == user_list.IdUserList).all()
        for uvc in user_value_cats:
            selected_categories.append({
                "IdCategory": uvc.IdCategory,
                # Получаем IdValueCategory для этой категории
                "IdValueCategory": db.query(ValueCategory.IdValueCategory).filter(
                    ValueCategory.IdCategory == uvc.IdCategory
                ).all()  # Можно доработать, если нужно только выбранные значения
            })
        # Альтернативно, если UserValueCategory хранит IdValueCategory:
        # selected_categories.append({"IdCategory": uvc.category.IdCategory, "IdValueCategory": uvc.IdValueCategory})
    return {
        "IdOfferList": offer.IdOfferList,
        "book": {
            "authorLastName": autor.LastName if autor else None,
            "authorFirstName": autor.FirstName if autor else None,
            "bookTitle": book.BookName if book else None,
            "isbn": book.ISBN if book else None,
            "year": book.YearPublishing.year if book and book.YearPublishing else None
        },
        "categories": selected_categories
    }

@router.post("/offer-list")
def create_offer_list(data: dict = Body(...), db: Session = Depends(get_db)):
    # Создаём автора, если нужно
    autor = Autor(FirstName=data['book']['authorFirstName'], LastName=data['book']['authorLastName'])
    db.add(autor)
    db.commit()
    db.refresh(autor)
    # Создаём книгу
    book = BookLiterary(
        IdAutor=autor.IdAutor,
        BookName=data['book']['bookTitle'],
        ISBN=data['book']['isbn'],
        YearPublishing=datetime(int(data['book']['year']), 1, 1)
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    # Создаём OfferList
    offer = OfferList(
        IdBookLiterary=book.IdBookLiterary,
        IdUser=data.get('IdUser', 1),  # TODO: получить из сессии
        CreateAt=datetime.utcnow(),
        UpdateAt=datetime.utcnow(),
        IdStatus=11  # TODO: статус по умолчанию
    )
    db.add(offer)
    db.commit()
    db.refresh(offer)
    # Создаём UserList
    user_list = UserList(IdOfferList=offer.IdOfferList)
    db.add(user_list)
    db.commit()
    db.refresh(user_list)
    # Сохраняем выбранные категории
    for cat in data['categories']:
        for val_id in cat['selected']:
            # Если вдруг вложенный массив, разворачиваем все значения
            if isinstance(val_id, list):
                for sub_id in val_id:
                    db.add(UserValueCategory(IdUserList=user_list.IdUserList, IdValueCategory=sub_id))
            else:
                db.add(UserValueCategory(IdUserList=user_list.IdUserList, IdValueCategory=val_id))
    db.commit()
    return {"IdOfferList": offer.IdOfferList}

@router.put("/offer-list/{id}")
def update_offer_list(id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    offer = db.query(OfferList).filter(OfferList.IdOfferList == id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="OfferList not found")
    # Обновляем книгу
    book = db.query(BookLiterary).filter(BookLiterary.IdBookLiterary == offer.IdBookLiterary).first()
    autor = db.query(Autor).filter(Autor.IdAutor == book.IdAutor).first() if book else None
    if autor and book:
        autor.FirstName = data['book']['authorFirstName']
        autor.LastName = data['book']['authorLastName']
        book.BookName = data['book']['bookTitle']
        book.ISBN = data['book']['isbn']
        book.YearPublishing = datetime(int(data['book']['year']), 1, 1)
        db.commit()
    # Обновляем категории
    user_list = db.query(UserList).filter(UserList.IdOfferList == id).first()
    if user_list:
        db.query(UserValueCategory).filter(UserValueCategory.IdUserList == user_list.IdUserList).delete()
        for cat in data['categories']:
            for val_id in cat['selected']:
                db.add(UserValueCategory(IdUserList=user_list.IdUserList, IdValueCategory=val_id))
        db.commit()
    # После обновления статуса — пересчитать рейтинг пользователя
    recalculate_user_rating(offer.IdUser, db)
    return {"IdOfferList": id, "status": "updated"}

@router.post("/wish-list")
def create_wish_list(data: dict = Body(...), db: Session = Depends(get_db)):
    # TODO: получить IdUser и IdUserAddress из сессии/формы
    wish = WishList(
        IdUser=data.get('IdUser', 1),
        CreatedAt=datetime.utcnow(),
        UpdateAt=datetime.utcnow(),
        IdStatus=11,
        IdUserAddress=data.get('IdUserAddress', 1)
    )
    db.add(wish)
    db.commit()
    db.refresh(wish)
    # Создаём UserList
    user_list = UserList(IdWishList=wish.IdWishList)
    db.add(user_list)
    db.commit()
    db.refresh(user_list)
    # Сохраняем выбранные категории
    for cat in data['categories']:
        for val_id in cat['selected']:
            db.add(UserValueCategory(IdUserList=user_list.IdUserList, IdValueCategory=val_id))
    db.commit()
    return {"IdWishList": wish.IdWishList}

@router.put("/wish-list/{id}")
def update_wish_list(id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    wish = db.query(WishList).filter(WishList.IdWishList == id).first()
    if not wish:
        raise HTTPException(status_code=404, detail="WishList not found")
    wish.UpdateAt = datetime.utcnow()
    db.commit()
    # Обновляем категории
    user_list = db.query(UserList).filter(UserList.IdWishList == id).first()
    if user_list:
        db.query(UserValueCategory).filter(UserValueCategory.IdUserList == user_list.IdUserList).delete()
        for cat in data['categories']:
            for val_id in cat['selected']:
                db.add(UserValueCategory(IdUserList=user_list.IdUserList, IdValueCategory=val_id))
        db.commit()
    return {"IdWishList": id, "status": "updated"}

@router.get("/wish-list/{id}")
def get_wish_list_by_id(id: int, db: Session = Depends(get_db)):
    wish = db.query(WishList).filter(WishList.IdWishList == id).first()
    if not wish:
        raise HTTPException(status_code=404, detail="WishList not found")
    user_list = db.query(UserList).filter(UserList.IdWishList == id).first()
    selected_categories = []
    if user_list:
        user_value_cats = db.query(UserValueCategory).filter(UserValueCategory.IdUserList == user_list.IdUserList).all()
        for uvc in user_value_cats:
            selected_categories.append({
                "IdCategory": uvc.IdCategory,
                # Получаем IdValueCategory для этой категории
                "IdValueCategory": db.query(ValueCategory.IdValueCategory).filter(
                    ValueCategory.IdCategory == uvc.IdCategory
                ).all()
            })
    return {
        "IdWishList": wish.IdWishList,
        "categories": selected_categories
    }

@router.get("/address/{id}", response_model=UserAddressResponse)
def get_address_by_id(id: int, db: Session = Depends(get_db)):
    address = db.query(UserAddress).filter(UserAddress.idUserAddress == id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return UserAddressResponse(
        idUserAddress=address.idUserAddress,
        IdUser=address.IdUser,
        AddrIndex=address.AddrIndex,
        AddrCity=address.AddrCity,
        AddrStreet=address.AddrStreet,
        AddrHouse=address.AddrHouse,
        AddrStructure=address.AddrStructure,
        AddrApart=address.AddrApart
    )

@router.put("/address/{id}")
def update_address_by_id(id: int, data: UserAddressBase, db: Session = Depends(get_db)):
    address = db.query(UserAddress).filter(UserAddress.idUserAddress == id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    address.IdUser = data.IdUser
    address.AddrIndex = data.AddrIndex
    address.AddrCity = data.AddrCity
    address.AddrStreet = data.AddrStreet
    address.AddrHouse = data.AddrHouse
    address.AddrStructure = data.AddrStructure
    address.AddrApart = data.AddrApart
    db.commit()
    return {"status": "updated"}

@router.post("/address")
def create_address(data: UserAddressBase, db: Session = Depends(get_db)):
    address = UserAddress(
        IdUser=data.IdUser,
        AddrIndex=data.AddrIndex,
        AddrCity=data.AddrCity,
        AddrStreet=data.AddrStreet,
        AddrHouse=data.AddrHouse,
        AddrStructure=data.AddrStructure,
        AddrApart=data.AddrApart
    )
    db.add(address)
    db.commit()
    db.refresh(address)
    return {"idUserAddress": address.idUserAddress}

@router.get("/exchange-matches")
def get_exchange_matches(IdUser: int = Query(...), db: Session = Depends(get_db)):
    # Пересчитываем рейтинг для всех пользователей, участвующих в обменах (включая себя)
    user_ids = [u.IdUser for u in db.query(User).all()]
    for uid in user_ids:
        recalculate_user_rating(uid, db)
    # Получаем все WishList и OfferList других пользователей
    wishlists = db.query(WishList).filter(WishList.IdUser != IdUser).all()
    offerlists = db.query(OfferList).filter(OfferList.IdUser != IdUser).all()
    # Получаем свои WishList и OfferList
    my_wishlists = db.query(WishList).filter(WishList.IdUser == IdUser).all()
    my_offerlists = db.query(OfferList).filter(OfferList.IdUser == IdUser).all()
    # Собираем категории для своих списков
    def get_categories(userlist):
        user_list = None
        if hasattr(userlist, 'IdWishList') and getattr(userlist, 'IdWishList', None):
            user_list = db.query(UserList).filter(UserList.IdWishList == userlist.IdWishList).first()
        elif hasattr(userlist, 'IdOfferList') and getattr(userlist, 'IdOfferList', None):
            user_list = db.query(UserList).filter(UserList.IdOfferList == userlist.IdOfferList).first()
        if not user_list:
            return set()
        uvc = db.query(UserValueCategory).filter(UserValueCategory.IdUserList == user_list.IdUserList).all()
        return set([v.IdValueCategory for v in uvc])
    def offer_info(offer):
        user = offer.user
        # Если у пользователя несколько адресов, берём первый или основной
        address = user.addresses[0] if hasattr(user, 'addresses') and user.addresses else None
        return {
            "offerId": offer.IdOfferList,
            "userId": user.IdUser,
            "userName": user.UserName,
            "avatar": getattr(user, 'Avatar', None),
            "city": address.AddrCity if address else "",
            "rating": getattr(user, 'Rating', 0),
        }
    fullMatches = []
    partialMatches = []
    otherMatches = []
    # Для каждого чужого пользователя ищем совпадения в обе стороны
    for other_user in db.query(User).filter(User.IdUser != IdUser).all():
        other_wishlists = [w for w in wishlists if w.IdUser == other_user.IdUser]
        other_offerlists = [o for o in offerlists if o.IdUser == other_user.IdUser]
        i_want_his = False
        he_wants_mine = False
        # Я хочу то, что у него есть (вложенность)
        for my_wish in my_wishlists:
            my_wish_cats = get_categories(my_wish)
            for his_offer in other_offerlists:
                his_offer_cats = get_categories(his_offer)
                print(f"[DEBUG] User {IdUser} wish {getattr(my_wish, 'IdWishList', None)} cats: {my_wish_cats} vs User {other_user.IdUser} offer {getattr(his_offer, 'IdOfferList', None)} cats: {his_offer_cats}", flush=True)
                if my_wish_cats and his_offer_cats and my_wish_cats.issubset(his_offer_cats):
                    i_want_his = True
        # Он хочет то, что есть у меня (вложенность)
        for his_wish in other_wishlists:
            his_wish_cats = get_categories(his_wish)
            for my_offer in my_offerlists:
                my_offer_cats = get_categories(my_offer)
                print(f"[DEBUG] User {other_user.IdUser} wish {getattr(his_wish, 'IdWishList', None)} cats: {his_wish_cats} vs User {IdUser} offer {getattr(my_offer, 'IdOfferList', None)} cats: {my_offer_cats}", flush=True)
                if his_wish_cats and my_offer_cats and his_wish_cats.issubset(my_offer_cats):
                    he_wants_mine = True
        print(f"[DEBUG] User {IdUser} <-> User {other_user.IdUser}: i_want_his={i_want_his}, he_wants_mine={he_wants_mine}", flush=True)
        if i_want_his and he_wants_mine:
            for offer in other_offerlists:
                fullMatches.append(offer_info(offer))
        elif i_want_his or he_wants_mine:
            for offer in other_offerlists:
                partialMatches.append(offer_info(offer))
        else:
            for offer in other_offerlists:
                otherMatches.append(offer_info(offer))
    # Исключаем дубли
    def unique_by_user(lst):
        seen = set()
        res = []
        for x in lst:
            uid = x['userId']
            if uid not in seen:
                seen.add(uid)
                res.append(x)
        return res

    return {
        "fullMatches": unique_by_user(fullMatches),
        "partialMatches": unique_by_user(partialMatches),
        "otherMatches": unique_by_user(otherMatches)
    } 