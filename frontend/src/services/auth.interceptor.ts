import { Injectable } from '@angular/core';

import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';

import { catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from './auth.service';
import { Observable } from 'rxjs';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {

    private isRefreshing = false;

    constructor(private authService: AuthService) {}

    intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        const token = this.authService.getToken();
        if (token) {
            request = request.clone({
                setHeaders: {
                    Authorization: `Bearer ${token}`
                }
            });
        }
        return next.handle(request).pipe(
            catchError((error: HttpErrorResponse) => {
                if (error.status === 401 && !request.url.includes('/auth/')) {
                    return this.handle401Error(request, next);
                }
                return throwError(error);
            })
        );
    }

    private handle401Error(request: HttpRequest<any>, next: HttpHandler) {
        if (!this.isRefreshing) {
            this.isRefreshing = true;
            
            return this.authService.refreshSession().pipe(
                switchMap(() => {
                    this.isRefreshing = false;
                    return this.authService.getCurrentUser().pipe(
                        switchMap((user: any) => {
                            this.authService.setUserData(user.IdUser, user.IsStaff ? 'admin' : 'user');
                            return next.handle(request);
                        })
                    );
                }),
                catchError((err) => {
                    this.isRefreshing = false;
                    this.authService.logout().subscribe();
                    this.authService.clearUserData();
                    return throwError(err);
                })
            );
        }
        return next.handle(request);
    }

}