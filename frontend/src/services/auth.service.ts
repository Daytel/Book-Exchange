import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}


  login(email: string, password: string) {
    return this.http.post(`${this.apiUrl}/auth/login`, { Email: email, Password: password }, { 
      withCredentials: true
    });
  }

  logout() {
    return this.http.post(`${this.apiUrl}/auth/logout`, {}, { 
      withCredentials: true 
    });
  }

  refreshSession() {
    return this.http.post(`${this.apiUrl}/auth/refresh`, {}, { 
      withCredentials: true 
    });
  }

  getProtectedData() {
    return this.http.get(`${this.apiUrl}/protected-data`, { 
      withCredentials: true 
    });
  }
}