import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { forkJoin } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class BookService {
  private bookData: any = null;
  private offerListData: any = null;
  private idOfferList: number | null = null;
  private idWishList: number | null = null;
  private wishListData: any = null;
  private addressData: any = null;
  private idAddress: number | null = null
  private apiUrl = 'http://localhost:8000/categories';

  constructor(private http: HttpClient) {}

  setBookData(data: any) {
    this.bookData = data;
  }

  getBookData() {
    return this.bookData;
  }

  setOfferListData(data: any) {
    this.offerListData = data;
  }

  getOfferListData() {
    return this.offerListData;
  }

  clearOfferListData() {
    this.offerListData = null;
  }

  setIdOfferList(id: number) {
    this.idOfferList = id;
  }

  getIdOfferList(): number | null {
    return this.idOfferList;
  }

  clearIdOfferList() {
    this.idOfferList = null;
  }

  setIdWishList(id: number) {
    this.idWishList = id;
  }

  getIdWishList(): number | null {
    return this.idWishList;
  }

  clearIdWishList() {
    this.idWishList = null;
  }

  setWishListData(data: any) {
    this.wishListData = data;
  }

  getWishListData() {
    return this.wishListData;
  }

  clearWishListData() {
    this.wishListData = null;
  }

  setAddressData(data: any) {
    this.addressData = data;
  }

  getAddressData() {
    return this.addressData;
  }

  clearAddressData() {
    this.addressData = null;
  }

  setIdAddress(id: number) {
    this.idAddress = id;
  }

  getIdAddress(): number | null {
    return this.idAddress;
  }

  clearIdAddress() {
    this.idAddress = null;
  }

  getCategories(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/full`);
  }

  getOfferListById(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/offer-list/${id}`);
  }

  saveOfferList(data: any): Observable<any> {
    // Если idOfferList есть, делаем PUT, иначе POST
    if (this.idOfferList) {
      return this.http.put(`${this.apiUrl}/offer-list/${this.idOfferList}`, data).pipe(
        tap(() => {
          this.clearOfferListData();
          this.clearIdOfferList();
        })
      );
    } else {
      return this.http.post(`${this.apiUrl}/offer-list`, data).pipe(
        tap((res: any) => {
          if (res && res.IdOfferList) {
            this.clearOfferListData();
            this.clearIdOfferList();
          }
        })
      );
    }
  }

  getWishListById(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/wish-list/${id}`);
  }

  saveWishList(data: any): Observable<any> {
    if (this.idWishList) {
      return this.http.put(`${this.apiUrl}/wish-list/${this.idWishList}`, data).pipe(
        tap(() => {
          this.clearWishListData();
          this.clearIdWishList();
        })
      );
    } else {
      return this.http.post(`${this.apiUrl}/wish-list`, data).pipe(
        tap((res: any) => {
          if (res && res.IdWishList) {
            this.clearWishListData();
            this.clearIdWishList();
          }
        })
      );
    }
  }

  getAddressById(id: number) {
    return this.http.get<any>(`${this.apiUrl}/address/${id}`);
  }

  updateAddressById(id: number, data: any) {
    return this.http.put(`${this.apiUrl}/address/${id}`, data).pipe(
      tap(() => {
        this.clearAddressData();
        this.clearIdAddress();
      })
    );
  }

  saveAddress(data: any) {
    return this.http.post(`${this.apiUrl}/address`, data).pipe(
      tap((res: any) => {
        this.clearAddressData();
        this.clearIdAddress();
      })
    );
  }

  sendFullExchange(): Observable<any> {
    // Сначала адрес, затем offerList и wishList
    return forkJoin({
      offerList: this.saveOfferList(this.offerListData),
      wishList: this.saveWishList(this.wishListData)
    });
  }

  getExchangeMatches(userId: number) {
    return this.http.get<any>(`${this.apiUrl}/exchange-matches?IdUser=${userId}`);
  }

  getActiveExchanges(userId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/active-exchanges?IdUser=${userId}`);
  }

  /** Подтвердить обмен */
  confirmExchange(exchangeId: number): Observable<any> {
    return this.http.patch(
      `${this.apiUrl}/active-exchanges/${exchangeId}/confirm`,
      {},
      { withCredentials: true }
    );
  }

  /** Отменить обмен */
  cancelExchange(exchangeId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/active-exchanges/${exchangeId}/cancel`);
  }

  /** Отправить трек-номер */
  submitTracking(exchangeId: number, offerListId: number, trackNumber: string): Observable<any> {
    return this.http.patch(`${this.apiUrl}/active-exchanges/${exchangeId}/track`, null, {
      params: {
        offerlist_id: offerListId,
        track_number: trackNumber
      }
    });
  }

  /** Подтвердить получение книги */
  confirmReceipt(exchangeId: number, offerListId: number): Observable<any> {
    return this.http.patch(`${this.apiUrl}/active-exchanges/${exchangeId}/receive`, null, {
      params: {
        offerlist_id: offerListId
      }
    });
  }

  /** Предложить обмен */
  proposeExchange(myOfferListId: number, myWishListId: number, theirOfferListId: number, theirWishListId: number) {
    console.log('POST proposeExchange', myOfferListId, myWishListId, theirOfferListId, theirWishListId);
    return this.http.post(`${this.apiUrl}/exchange/propose`, null, {
      params: {
        my_offerlist_id: myOfferListId,
        my_wishlist_id: myWishListId,
        their_offerlist_id: theirOfferListId,
        their_wishlist_id: theirWishListId
      }
    });
  }

  getAuthors(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/authors`);
  }

  getBooksByAuthor(authorId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/authors/${authorId}/books`);
  }

  /** Получить все OfferList пользователя */
  getOfferListByUser(userId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/offer-list/user/${userId}`);
  }

  /** Удалить OfferList по id */
  deleteOfferListById(offerListId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/offer-list/${offerListId}`);
  }

  /** Получить все WishList пользователя */
  getWishListByUser(userId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/wish-list/user/${userId}`);
  }

  /** Удалить WishList по id */
  deleteWishListById(wishListId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/wish-list/${wishListId}`);
  }

  /** Получить завершённые обмены пользователя */
  getArchiveExchanges(userId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/archive-exchanges?IdUser=${userId}`);
  }
} 