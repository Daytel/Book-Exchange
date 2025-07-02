import { Component, OnInit } from '@angular/core';
import { BookService } from '../../services/book.service';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-my-exchange',
  templateUrl: './my-exchange.component.html',
  styleUrls: ['./my-exchange.component.css']
})
export class MyExchangeComponent implements OnInit {
  userName = 'Смелый заяц';
  userAvatar = 'assets/avatar.jpg';
  userRating = 2;

  fullMatches: any[] = [];
  partialMatches: any[] = [];
  otherMatches: any[] = [];
  loading = true;
  errorMsg = '';

  lastUpdateTime: Date | null = null;
  canRefresh = true;
  refreshTimeout: any = null;
  refreshCountdown: number | null = null;
  refreshInterval: any = null;

  isLoggedIn = false;
  avatar: string | null = null;

  constructor(private bookService: BookService, private authService: AuthService, private router: Router) {}

  ngOnInit() {
    this.authService.getCurrentUser().subscribe({
      next: (user: any) => {
        this.isLoggedIn = true;
        this.userName = user.UserName || user.userName || user.Email || '';
        this.avatar = user.Avatar ? 'data:image/jpeg;base64,' + user.Avatar : null;
        const userId = user.IdUser || user.id || user.userId;
        if (!userId) {
          this.errorMsg = 'Пользователь не авторизован';
          this.loading = false;
          return;
        }
        // Восстанавливаем время последнего обновления из localStorage
        const last = localStorage.getItem('myexchange_last_update');
        if (last) {
          this.lastUpdateTime = new Date(last);
          const diff = Date.now() - this.lastUpdateTime.getTime();
          if (diff < 30000) {
            this.canRefresh = false;
            this.setRefreshTimer(30000 - diff);
          }
        }
        this.loadMatches(userId);
      },
      error: () => {
        this.isLoggedIn = false;
        this.userName = '';
        this.avatar = null;
        this.errorMsg = 'Пользователь не авторизован';
        this.loading = false;
      }
    });
  }

  loadMatches(userId: number) {
    this.loading = true;
    this.bookService.getExchangeMatches(userId).subscribe({
      next: (res: any) => {
        this.fullMatches = res.fullMatches || [];
        this.partialMatches = res.partialMatches || [];
        this.otherMatches = res.otherMatches || [];
        this.loading = false;
        this.lastUpdateTime = new Date();
        localStorage.setItem('myexchange_last_update', this.lastUpdateTime.toISOString());
        this.canRefresh = false;
        this.setRefreshTimer(30000);
      },
      error: (err: any) => {
        this.errorMsg = 'Ошибка загрузки предложений обмена';
        this.loading = false;
      }
    });
  }

  refreshMatches() {
    if (!this.canRefresh) return;
    const userId = this.authService.getUserId();
    if (!userId) return;
    this.loadMatches(userId);
  }

  setRefreshTimer(ms: number) {
    if (this.refreshTimeout) clearTimeout(this.refreshTimeout);
    if (this.refreshInterval) clearInterval(this.refreshInterval);
    this.refreshCountdown = Math.ceil(ms / 1000);
    this.refreshInterval = setInterval(() => {
      if (this.refreshCountdown !== null) {
        this.refreshCountdown--;
        if (this.refreshCountdown <= 0) {
          this.refreshCountdown = null;
          clearInterval(this.refreshInterval);
        }
      }
    }, 1000);
    this.refreshTimeout = setTimeout(() => {
      this.canRefresh = true;
      this.refreshCountdown = null;
      if (this.refreshInterval) clearInterval(this.refreshInterval);
    }, ms);
  }

  showAuthAlert(event: Event) {
    event.preventDefault();
    alert('Для доступа к разделу "Мои обмены" необходимо авторизоваться!');
  }

  goToProfile() {
    // Переход на страницу профиля
    // Например:
    window.location.href = '/my-exchange/personal';
  }

  logout() {
    this.authService.logout().subscribe({
      next: () => {
        this.router.navigate(['/auth/login']);
      },
      error: () => {
        this.router.navigate(['/auth/login']);
      }
    });
  }

  offerExchange(offer: any) {
    // TODO: реализовать отправку предложения обмена
    console.log('Предложить обмен:', offer);
  }
}
