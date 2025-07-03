from fastapi import APIRouter, Depends, HTTPException, Body, Query, status
from sqlalchemy.orm import Session, joinedload
from ..database import get_db, get_current_user
from ..models import Category, ValueCategory, OfferList, BookLiterary, Autor, UserList, UserValueCategory, WishList, UserAddress, User, ExchangeList, UserExchangeList, Status, UserMsg
from ..schemas import CategoryResponse, ValueCategoryResponse, UserAddressResponse, UserAddressBase
from typing import List, Dict, Any
from datetime import datetime, timedelta
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
    def offer_info(offer, my_offer=None, my_wish=None, their_offer=None, their_wish=None, db=None):
        user = offer.user
        their_user = None
        if their_offer and hasattr(their_offer, 'IdUser'):
            their_user = db.query(User).filter(User.IdUser == their_offer.IdUser).first()
        address = user.addresses[0] if hasattr(user, 'addresses') and user.addresses else None
        user_list = db.query(UserList).filter(UserList.IdOfferList == offer.IdOfferList).first()
        categories = []
        if user_list:
            uvc_list = db.query(UserValueCategory).filter(UserValueCategory.IdUserList == user_list.IdUserList).all()
            for uvc in uvc_list:
                value_cat = db.query(ValueCategory).filter(ValueCategory.IdValueCategory == uvc.IdValueCategory).first()
                cat = db.query(Category).filter(Category.IdCategory == value_cat.IdCategory).first() if value_cat else None
                categories.append({
                    "IdCategory": value_cat.IdCategory if value_cat else None,
                    "categoryName": cat.Value if cat else None,
                    "IdValueCategory": value_cat.IdValueCategory if value_cat else None,
                    "valueName": value_cat.Value if value_cat else None
                })
        return {
            "offerId": offer.IdOfferList,
            "userId": user.IdUser,
            "userName": user.UserName,
            "avatar": getattr(user, 'Avatar', None),
            "city": address.AddrCity if address else "",
            "rating": getattr(user, 'Rating', 0),
            "categories": categories,
            # Новые поля для фронта:
            "myOfferListId": my_offer.IdOfferList if my_offer else None,
            "myWishListId": my_wish.IdWishList if my_wish else None,
            "theirOfferListId": their_offer.IdOfferList if their_offer else offer.IdOfferList,
            "theirWishListId": their_wish.IdWishList if their_wish else None,
            "myUserId": IdUser,
            "theirUserId": their_user.IdUser if their_user else None
        }
    fullMatches = []
    partialMatches = []
    otherMatches = []
    for other_user in db.query(User).filter(User.IdUser != IdUser).all():
        other_wishlists = [w for w in wishlists if w.IdUser == other_user.IdUser]
        other_offerlists = [o for o in offerlists if o.IdUser == other_user.IdUser]
        i_want_his = False
        he_wants_mine = False
        max_match_offer = None
        max_match_count = 0
        my_best_offer = None
        my_best_wish = None
        their_best_offer = None
        their_best_wish = None
        # Я хочу то, что у него есть (вложенность)
        for my_wish in my_wishlists:
            my_wish_cats = get_categories(my_wish)
            for his_offer in other_offerlists:
                his_offer_cats = get_categories(his_offer)
                if my_wish_cats and his_offer_cats:
                    match_count = len(my_wish_cats & his_offer_cats)
                    if match_count > max_match_count:
                        max_match_count = match_count
                        max_match_offer = his_offer
                        my_best_wish = my_wish
                        their_best_offer = his_offer
                if my_wish_cats and his_offer_cats and my_wish_cats.issubset(his_offer_cats):
                    i_want_his = True
                    my_best_wish = my_wish
                    their_best_offer = his_offer
        # Он хочет то, что есть у меня (вложенность)
        for his_wish in other_wishlists:
            his_wish_cats = get_categories(his_wish)
            for my_offer in my_offerlists:
                my_offer_cats = get_categories(my_offer)
                if his_wish_cats and my_offer_cats and his_wish_cats.issubset(my_offer_cats):
                    he_wants_mine = True
                    my_best_offer = my_offer
                    their_best_wish = his_wish
        if i_want_his and he_wants_mine:
            for offer in other_offerlists:
                fullMatches.append(offer_info(offer, my_best_offer, my_best_wish, their_best_offer, their_best_wish, db))
        elif i_want_his or he_wants_mine:
            if max_match_offer:
                partialMatches.append(offer_info(max_match_offer, my_best_offer, my_best_wish, their_best_offer, their_best_wish, db))
        else:
            if other_offerlists:
                max_other_offer = None
                max_other_count = -1
                for his_offer in other_offerlists:
                    match_count = 0
                    for my_wish in my_wishlists:
                        my_wish_cats = get_categories(my_wish)
                        his_offer_cats = get_categories(his_offer)
                        if my_wish_cats and his_offer_cats:
                            match_count = max(match_count, len(my_wish_cats & his_offer_cats))
                    if match_count > max_other_count:
                        max_other_count = match_count
                        max_other_offer = his_offer
                        my_best_wish = my_wish
                        their_best_offer = his_offer
                if max_other_offer:
                    otherMatches.append(offer_info(max_other_offer, my_best_offer, my_best_wish, their_best_offer, their_best_wish, db))
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

@router.get("/active-exchanges")
def get_active_exchanges(IdUser: int = Query(...), db: Session = Depends(get_db)):
    now = datetime.utcnow()
    user_offer_ids = [o.IdOfferList for o in db.query(OfferList).filter(OfferList.IdUser == IdUser).all()]
    exchanges = db.query(ExchangeList).filter(
        (ExchangeList.IdOfferList1.in_(user_offer_ids)) | (ExchangeList.IdOfferList2.in_(user_offer_ids)),
        ExchangeList.CreateAt >= now - timedelta(days=2)
    ).all()
    def get_categories_for_offer(offer_id):
        user_list = db.query(UserList).filter(UserList.IdOfferList == offer_id).first()
        categories = []
        if user_list:
            uvc_list = db.query(UserValueCategory).filter(UserValueCategory.IdUserList == user_list.IdUserList).all()
            for uvc in uvc_list:
                value_cat = db.query(ValueCategory).filter(ValueCategory.IdValueCategory == uvc.IdValueCategory).first()
                cat = db.query(Category).filter(Category.IdCategory == value_cat.IdCategory).first() if value_cat else None
                categories.append({
                    "IdCategory": value_cat.IdCategory if value_cat else None,
                    "categoryName": cat.Value if cat else None,
                    "IdValueCategory": value_cat.IdValueCategory if value_cat else None,
                    "valueName": value_cat.Value if value_cat else None
                })
        return categories
    result = []
    for exch in exchanges:
        # Определяем, с какой стороны пользователь
        if exch.IdOfferList1 in user_offer_ids:
            my_offer_id = exch.IdOfferList1
            their_offer_id = exch.IdOfferList2
            my_wishlist_id = exch.IdWishList1
            their_wishlist_id = exch.IdWishList2
        else:
            my_offer_id = exch.IdOfferList2
            their_offer_id = exch.IdOfferList1
            my_wishlist_id = exch.IdWishList2
            their_wishlist_id = exch.IdWishList1
        my_offer = db.query(OfferList).filter(OfferList.IdOfferList == my_offer_id).first()
        their_offer = db.query(OfferList).filter(OfferList.IdOfferList == their_offer_id).first()
        # Новая логика: обмен не показываем только если оба статуса 11 или оба 15
        if (my_offer.IdStatus == 11 and their_offer.IdStatus == 11) or (my_offer.IdStatus == 15 and their_offer.IdStatus == 15):
            continue
        my_user = db.query(User).filter(User.IdUser == my_offer.IdUser).first() if my_offer else None
        their_user = db.query(User).filter(User.IdUser == their_offer.IdUser).first() if their_offer else None
        # Книга
        my_book = db.query(BookLiterary).filter(BookLiterary.IdBookLiterary == my_offer.IdBookLiterary).first() if my_offer else None
        their_book = db.query(BookLiterary).filter(BookLiterary.IdBookLiterary == their_offer.IdBookLiterary).first() if their_offer else None
        # Категории для обеих книг
        my_categories = get_categories_for_offer(my_offer_id)
        their_categories = get_categories_for_offer(their_offer_id)
        my_uel = db.query(UserExchangeList).filter(UserExchangeList.IdOfferList == my_offer_id).first()
        their_uel = db.query(UserExchangeList).filter(UserExchangeList.IdOfferList == their_offer_id).first()
        # Получаем статусы из БД
        my_status_obj = db.query(Status).filter(Status.IdStatus == my_offer.IdStatus).first() if my_offer else None
        their_status_obj = db.query(Status).filter(Status.IdStatus == their_offer.IdStatus).first() if their_offer else None
        my_status_code = my_offer.IdStatus if my_offer else None
        their_status_code = their_offer.IdStatus if their_offer else None
        my_status_text = my_status_obj.Name if my_status_obj else None
        their_status_text = their_status_obj.Name if their_status_obj else None
        # Получаем адреса для отправки книг
        my_wishlist = db.query(WishList).filter(WishList.IdWishList == my_wishlist_id).first()
        their_wishlist = db.query(WishList).filter(WishList.IdWishList == their_wishlist_id).first()
        my_address = db.query(UserAddress).filter(UserAddress.idUserAddress == my_wishlist.IdUserAddress).first() if my_wishlist and my_wishlist.IdUserAddress else None
        their_address = db.query(UserAddress).filter(UserAddress.idUserAddress == their_wishlist.IdUserAddress).first() if their_wishlist and their_wishlist.IdUserAddress else None
        # Формируем статус для UI (оставляем для совместимости)
        if not exch.IsBoth:
            my_status = my_status_text or "Ожидает подтверждения"
            partner_status = their_status_text or "Ожидает подтверждения"
            can_confirm = True
            can_send = False
            can_receive = False
        else:
            my_status = my_status_text or "Подтвержден"
            partner_status = their_status_text or "Подтвержден"
            can_confirm = False
            can_send = True if not (my_uel and my_uel.TrackNumber) else False
            can_receive = True if (my_uel and my_uel.TrackNumber and not my_uel.Receiving) else False
            if my_uel and my_uel.Receiving:
                my_status = "Книга получена"
                can_receive = False
        # Аналогично для партнера
        if their_uel and their_uel.Receiving:
            partner_status = "Книга получена"
        # Собираем результат
        result.append({
            "id": exch.IdExchangeList,
            "myBook": {
                "author": my_book.autor.LastName if my_book and my_book.autor else None,
                "title": my_book.BookName if my_book else None,
                "categories": my_categories,
                "year": my_book.YearPublishing.year if my_book and my_book.YearPublishing else None
            },
            "theirBook": {
                "author": their_book.autor.LastName if their_book and their_book.autor else None,
                "title": their_book.BookName if their_book else None,
                "categories": their_categories,
                "year": their_book.YearPublishing.year if their_book and their_book.YearPublishing else None
            },
            "myStatus": my_status,
            "partnerStatus": partner_status,
            "myStatusCode": my_status_code,
            "partnerStatusCode": their_status_code,
            "myStatusText": my_status_text,
            "partnerStatusText": their_status_text,
            "tracking": my_uel.TrackNumber if my_uel else None,
            "partnerTracking": their_uel.TrackNumber if their_uel else None,
            "canConfirm": can_confirm,
            "canSend": can_send,
            "canReceive": can_receive,
            "city": their_user.addresses[0].AddrCity if their_user and hasattr(their_user, 'addresses') and their_user.addresses else None,
            "rating": getattr(their_user, 'Rating', 0) if their_user else 0,
            "userName": their_user.UserName if their_user else None,
            "avatar": their_user.Avatar if their_user else None,
            "myOfferListId": my_offer_id,
            "myWishListId": my_wishlist_id,
            "theirOfferListId": their_offer_id,
            "theirWishListId": their_wishlist_id,
            "myAddress": {
                "city": my_address.AddrCity if my_address else None,
                "street": my_address.AddrStreet if my_address else None,
                "house": my_address.AddrHouse if my_address else None,
                "structure": my_address.AddrStructure if my_address else None,
                "flat": my_address.AddrApart if my_address else None,
                "postcode": my_address.AddrIndex if my_address else None,
            } if my_address else None,
            "theirAddress": {
                "city": their_address.AddrCity if their_address else None,
                "street": their_address.AddrStreet if their_address else None,
                "house": their_address.AddrHouse if their_address else None,
                "structure": their_address.AddrStructure if their_address else None,
                "flat": their_address.AddrApart if their_address else None,
                "postcode": their_address.AddrIndex if their_address else None,
            } if their_address else None,
            "myUserId": IdUser,
            "theirUserId": their_user.IdUser if their_user else None
        })
    return {"exchanges": result}

@router.patch("/active-exchanges/{exchange_id}/confirm")
def confirm_exchange(exchange_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    exch = db.query(ExchangeList).filter(ExchangeList.IdExchangeList == exchange_id).first()
    if not exch:
        raise HTTPException(status_code=404, detail="Exchange not found")
    # Проверяем, что текущий пользователь — владелец одного из OfferList
    if exch.offer1.IdUser != current_user.IdUser and exch.offer2.IdUser != current_user.IdUser:
        raise HTTPException(status_code=403, detail="Not allowed")
    # Меняем IsBoth на True
    exch.IsBoth = True
    exch.CreateAt = datetime.utcnow()
    # Меняем статусы OfferList на 12
    offer1 = db.query(OfferList).filter(OfferList.IdOfferList == exch.IdOfferList1).first()
    offer2 = db.query(OfferList).filter(OfferList.IdOfferList == exch.IdOfferList2).first()
    wish1 = db.query(WishList).filter(WishList.IdWishList == exch.IdWishList1).first()
    wish2 = db.query(WishList).filter(WishList.IdWishList == exch.IdWishList2).first()
    if offer1:
        offer1.IdStatus = 12
    if offer2:
        offer2.IdStatus = 12
    # Добавляем UserExchangeList для каждого OfferList, если ещё нет
    for offer in [offer1, offer2]:
        if offer and not db.query(UserExchangeList).filter(UserExchangeList.IdOfferList == offer.IdOfferList).first():
            db.add(UserExchangeList(IdOfferList=offer.IdOfferList, TrackNumber=None, Receiving=False))
    db.commit()

    # --- Сообщения для обоих участников ---
    # Для offer1 (ждёт user2 по адресу wish2.address)
    if offer1 and offer2 and wish2:
        book1 = offer1.book
        author1 = book1.autor.LastName if book1 and book1.autor else ''
        title1 = book1.BookName if book1 else ''
        user2 = offer2.user
        fio2 = f"{user2.LastName} {user2.FirstName} {user2.SecondName or ''}".strip() if user2 else ''
        addr2 = wish2.address
        addr2_str = f"{addr2.AddrCity}, {addr2.AddrStreet}, {addr2.AddrHouse}"
        if addr2.AddrStructure:
            addr2_str += f", стр. {addr2.AddrStructure}"
        if addr2.AddrApart:
            addr2_str += f", кв. {addr2.AddrApart}"
        msg1 = UserMsg(
            IdUser=offer1.IdUser,
            CreateAt=datetime.utcnow(),
            Text=f"Вашу книгу {author1}, {title1} ждёт {fio2} по адресу {addr2_str}",
            Notes=None,
            IdStatus=12,
            Type=True
        )
        db.add(msg1)
    # Для offer2 (ждёт user1 по адресу wish1.address)
    if offer1 and offer2 and wish1:
        book2 = offer2.book
        author2 = book2.autor.LastName if book2 and book2.autor else ''
        title2 = book2.BookName if book2 else ''
        user1 = offer1.user
        fio1 = f"{user1.LastName} {user1.FirstName} {user1.SecondName or ''}".strip() if user1 else ''
        addr1 = wish1.address
        addr1_str = f"{addr1.AddrCity}, {addr1.AddrStreet}, {addr1.AddrHouse}"
        if addr1.AddrStructure:
            addr1_str += f", стр. {addr1.AddrStructure}"
        if addr1.AddrApart:
            addr1_str += f", кв. {addr1.AddrApart}"
        msg2 = UserMsg(
            IdUser=offer2.IdUser,
            CreateAt=datetime.utcnow(),
            Text=f"Вашу книгу {author2}, {title2} ждёт {fio1} по адресу {addr1_str}",
            Notes=None,
            IdStatus=12,
            Type=True
        )
        db.add(msg2)
    db.commit()
    return {"status": "confirmed", "exchangeId": exchange_id, "IsBoth": True}

@router.delete("/active-exchanges/{exchange_id}/cancel")
def cancel_exchange(exchange_id: int, db: Session = Depends(get_db)):
    exch = db.query(ExchangeList).filter(ExchangeList.IdExchangeList == exchange_id).first()
    if not exch:
        raise HTTPException(status_code=404, detail="Exchange not found")
    # Получаем оба OfferList
    offer1 = db.query(OfferList).filter(OfferList.IdOfferList == exch.IdOfferList1).first()
    offer2 = db.query(OfferList).filter(OfferList.IdOfferList == exch.IdOfferList2).first()
    # Меняем статус OfferList1 с 12 на 11, если нужно
    if offer1 and offer1.IdStatus == 12:
        offer1.IdStatus = 11
        db.commit()
    # Получаем данные книги и авторов
    book1 = offer1.book if offer1 else None
    book2 = offer2.book if offer2 else None
    author1 = book1.autor.LastName if book1 and book1.autor else ''
    title1 = book1.BookName if book1 else ''
    author2 = book2.autor.LastName if book2 and book2.autor else ''
    title2 = book2.BookName if book2 else ''
    # Сообщение первому участнику (offer1.IdUser)
    if offer1:
        text1 = f"Второй участник не подтвердил обмен на вашу книгу {author1}, {title1}. Мы найдем Вам другой вариант."
        user_msg1 = UserMsg(
            IdUser=offer1.IdUser,
            CreateAt=datetime.utcnow(),
            Text=text1,
            Notes=None,
            IdStatus=15,
            Type=True
        )
        db.add(user_msg1)
    # Сообщение второму участнику (offer2.IdUser)
    if offer2:
        text2 = f"Вариант обмена на книгу {author1}, {title1} аннулирован."
        user_msg2 = UserMsg(
            IdUser=offer2.IdUser,
            CreateAt=datetime.utcnow(),
            Text=text2,
            Notes=None,
            IdStatus=15,
            Type=False
        )
        db.add(user_msg2)
    db.commit()
    db.delete(exch)
    db.commit()
    return {"status": "cancelled", "exchangeId": exchange_id}

@router.patch("/active-exchanges/{exchange_id}/track")
def submit_tracking(exchange_id: int, offerlist_id: int, track_number: str, db: Session = Depends(get_db)):
    exch = db.query(ExchangeList).filter(ExchangeList.IdExchangeList == exchange_id).first()
    if not exch:
        raise HTTPException(status_code=404, detail="Exchange not found")
    uel = db.query(UserExchangeList).filter(UserExchangeList.IdOfferList == offerlist_id).first()
    if not uel:
        raise HTTPException(status_code=404, detail="UserExchangeList not found")
    uel.TrackNumber = track_number
    # Обновляем статус OfferList на 13
    offer = db.query(OfferList).filter(OfferList.IdOfferList == offerlist_id).first()
    if offer:
        offer.IdStatus = 13
    # Проверяем, введён ли трек у второго участника
    other_offer_id = exch.IdOfferList1 if exch.IdOfferList2 == offerlist_id else exch.IdOfferList2
    other_uel = db.query(UserExchangeList).filter(UserExchangeList.IdOfferList == other_offer_id).first()
    other_offer = db.query(OfferList).filter(OfferList.IdOfferList == other_offer_id).first()
    if other_uel and other_uel.TrackNumber and offer and other_offer:
        offer.IdStatus = 14
        other_offer.IdStatus = 14
        exch.CreateAt = datetime.utcnow()
    db.commit()
    return {"status": "track updated", "exchangeId": exchange_id}

@router.patch("/active-exchanges/{exchange_id}/receive")
def confirm_receipt(exchange_id: int, offerlist_id: int, db: Session = Depends(get_db)):
    exch = db.query(ExchangeList).filter(ExchangeList.IdExchangeList == exchange_id).first()
    if not exch:
        raise HTTPException(status_code=404, detail="Exchange not found")
    uel = db.query(UserExchangeList).filter(UserExchangeList.IdOfferList == offerlist_id).first()
    if not uel:
        raise HTTPException(status_code=404, detail="UserExchangeList not found")
    uel.Receiving = True
    # Меняем статус OfferList другого участника на 15
    other_offer_id = exch.IdOfferList1 if exch.IdOfferList2 == offerlist_id else exch.IdOfferList2
    other_offer = db.query(OfferList).filter(OfferList.IdOfferList == other_offer_id).first()
    if other_offer:
        other_offer.IdStatus = 15
    db.commit()
    return {"status": "received", "exchangeId": exchange_id}

@router.post("/exchange/propose")
def propose_exchange(
    my_offerlist_id: int,
    my_wishlist_id: int,
    their_offerlist_id: int,
    their_wishlist_id: int,
    db: Session = Depends(get_db)
):
    # Меняем статус OfferList пользователя на 12
    my_offer = db.query(OfferList).filter(OfferList.IdOfferList == my_offerlist_id).first()
    if not my_offer:
        raise HTTPException(status_code=404, detail="My OfferList not found")
    my_offer.IdStatus = 12
    # Добавляем запись в ExchangeList
    exch = ExchangeList(
        IdOfferList1=my_offerlist_id,
        IdWishList1=my_wishlist_id,
        IdOfferList2=their_offerlist_id,
        IdWishList2=their_wishlist_id,
        CreateAt=datetime.utcnow(),
        IsBoth=False
    )
    db.add(exch)
    db.commit()
    db.refresh(exch)

    # --- Добавление сообщения второму пользователю ---
    their_offer = db.query(OfferList).filter(OfferList.IdOfferList == their_offerlist_id).first()
    if their_offer:
        book = their_offer.book
        author = book.autor.LastName if book and book.autor else ''
        title = book.BookName if book else ''
        text = f"На Вашу книгу {author}, {title} согласны обменяться."
        user_msg = UserMsg(
            IdUser=their_offer.IdUser,
            CreateAt=datetime.utcnow(),
            Text=text,
            Notes=None,
            IdStatus=11,
            Type=True
        )
        db.add(user_msg)
        db.commit()

    return {"status": "proposed", "exchangeId": exch.IdExchangeList}

@router.get("/authors")
def get_authors(db: Session = Depends(get_db)):
    authors = db.query(Autor).all()
    return [
        {"id": a.IdAutor, "firstName": a.FirstName, "lastName": a.LastName}
        for a in authors
    ]

@router.get("/authors/{author_id}/books")
def get_books_by_author(author_id: int, db: Session = Depends(get_db)):
    books = db.query(BookLiterary).filter(BookLiterary.IdAutor == author_id).all()
    return [
        {"id": b.IdBookLiterary, "title": b.BookName}
        for b in books
    ] 