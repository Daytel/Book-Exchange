import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class BookService {
  private bookData: any = null;
  private offerListData: any = null;
  private idOfferList: number | null = null;
  private idWishList: number | null = null;
  private wishListData: any = null;
  private apiUrl = 'http://localhost:8000';

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

  getCategories(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/categories/full`);
  }

  getOfferListById(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/offer-list/${id}`);
  }

  saveOfferList(data: any): Observable<any> {
    // Если idOfferList есть, делаем PUT, иначе POST
    if (this.idOfferList) {
      return this.http.put(`${this.apiUrl}/offer-list/${this.idOfferList}`, data).pipe(
        // После успешного запроса сбрасываем idOfferList
        tap(() => this.clearIdOfferList())
      );
    } else {
      return this.http.post(`${this.apiUrl}/offer-list`, data).pipe(
        tap((res: any) => {
          if (res && res.IdOfferList) this.clearIdOfferList();
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
        tap(() => this.clearIdWishList())
      );
    } else {
      return this.http.post(`${this.apiUrl}/wish-list`, data).pipe(
        tap((res: any) => {
          if (res && res.IdWishList) this.clearIdWishList();
        })
      );
    }
  }
} 