import { Injectable } from '@angular/core';
import { HttpClient} from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap, switchMap } from 'rxjs/operators';



@Injectable({ providedIn: 'root' })
export class AuthService {
    private apiUrl = 'http://localhost:8000';

    constructor(private http: HttpClient) {}

    login(email: string, password: string): Observable<any> {
        return this.http.post(`${this.apiUrl}/auth/login`, { Email: email, Password: password }, {
            withCredentials: true
        }).pipe(
            tap((response: any) => {
                // Предполагается, что токен приходит в response.access_token
                localStorage.setItem('access_token', response.access_token);
            })
        );
    }

    // Временно закомментировано, так как эндпоинта нет
    register(data: { firstName: string, lastName: string, secondName: string, email: string, userName: string, password: string }): Observable<any> {
        return this.http.post(`${this.apiUrl}/auth/register`, {
            FirstName: data.firstName,
            LastName: data.lastName,
            SecondName: data.secondName || '',
            Email: data.email,
            UserName: data.userName,
            Password: data.password
        }, {
            withCredentials: true
        }).pipe(
            switchMap(() => this.login(data.email, data.password))
        );
    }

    logout(): Observable<any> {
        return this.http.post(`${this.apiUrl}/auth/logout`, {}, {
            withCredentials: true
        });
    }

    refreshSession(): Observable<any> {
        return this.http.post(`${this.apiUrl}/auth/refresh`, {}, {
            withCredentials: true
        });
    }

    getCurrentUser(): Observable<any> {
        return this.http.get(`${this.apiUrl}/auth/me`, {
            withCredentials: true
        });
    }

    setUserData(id: number, role: string): void {
        localStorage.setItem('userId', id.toString());
        localStorage.setItem('userRole', role);
    }

    getUserId(): number | null {
        const id = localStorage.getItem('userId');
        return id ? parseInt(id, 10) : null;
    }

    getUserRole(): string | null {
        return localStorage.getItem('userRole');
    }

    clearUserData(): void {
        localStorage.removeItem('userId');
        localStorage.removeItem('userRole');
    }

    getUserById(id: number): Observable<any> {
        return this.http.get(`${this.apiUrl}/auth/user/${id}`, {
            withCredentials: true
        });
    }

    getToken(): string | null {
        return localStorage.getItem('access_token');
    }

}