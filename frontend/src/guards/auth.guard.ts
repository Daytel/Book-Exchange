import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({ providedIn: 'root' })
export class AuthGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(): boolean {
    const userId = this.authService.getUserId();
    if (userId) {
      return true;
    }
    alert('Для доступа к разделу необходимо авторизоваться!');
    this.router.navigate(['/auth/login']);
    return false;
  }
}
