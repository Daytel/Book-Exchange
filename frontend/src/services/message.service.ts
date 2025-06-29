import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface UserMsg {
  IdUserMsg: number;
  IdUser: number;
  CreateAt: string;
  Text: string;
  Notes?: string;
  IdStatus: number;
  Type: boolean;
}

export interface Status {
  IdStatus: number;
  Name: string;
}

@Injectable({ providedIn: 'root' })
export class MessageService {
  private apiUrl = 'http://localhost:8000/api/messages';

  constructor(private http: HttpClient) {}

  // Получить все сообщения пользователя
  getReceivedMessages(userId: number): Observable<UserMsg[]> {
    return this.http.get<UserMsg[]>(`${this.apiUrl}/received`, {
      params: { user_id: userId },
      withCredentials: true
    });
  }

  // Отправить сообщение
  sendMessage(msg: any) {
    return this.http.post(this.apiUrl + '/', msg, { withCredentials: true });
  }

  // Получить список статусов
  getStatuses() {
    return this.http.get<Status[]>(`${this.apiUrl.replace('/messages', '')}/statuses/`, { withCredentials: true });
  }
}
