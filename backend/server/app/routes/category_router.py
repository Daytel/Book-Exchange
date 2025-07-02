from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Category, ValueCategory, OfferList, BookLiterary, Autor, UserList, UserValueCategory, WishList
from ..schemas import CategoryResponse, ValueCategoryResponse
from typing import List, Dict, Any
from datetime import datetime

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
        IdUser=1,  # TODO: получить из сессии
        CreateAt=datetime.utcnow(),
        UpdateAt=datetime.utcnow(),
        IdStatus=1  # TODO: статус по умолчанию
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
            db.add(UserValueCategory(IdUserList=user_list.IdUserList, IdCategory=cat['IdCategory']))
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
                db.add(UserValueCategory(IdUserList=user_list.IdUserList, IdCategory=cat['IdCategory']))
        db.commit()
    return {"IdOfferList": id, "status": "updated"}

@router.post("/wish-list")
def create_wish_list(data: dict = Body(...), db: Session = Depends(get_db)):
    # TODO: получить IdUser и IdUserAddress из сессии/формы
    wish = WishList(
        IdUser=1,
        CreatedAt=datetime.utcnow(),
        UpdateAt=datetime.utcnow(),
        IdStatus=1,
        IdUserAddress=1
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
            db.add(UserValueCategory(IdUserList=user_list.IdUserList, IdCategory=cat['IdCategory']))
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
                db.add(UserValueCategory(IdUserList=user_list.IdUserList, IdCategory=cat['IdCategory']))
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