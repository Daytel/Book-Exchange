import { Component, OnInit } from '@angular/core';
import { BookService } from 'src/services/book.service';
import { AuthService } from 'src/services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-my-active',
  templateUrl: './my-active.component.html',
  styleUrls: ['./my-active.component.css']
})
export class MyActiveComponent implements OnInit {
  userName = '';
  userAvatar = '';
  userRating = 0;
  activeExchanges: any[] = [];
  lastUpdate = new Date();
  loading = true;
  errorMsg = '';
  isLoggedIn = false;
  avatar: string | null = null;
  userId: number | null = null;

  constructor(private bookService: BookService, private authService: AuthService, private router: Router) {}

  ngOnInit() {
    this.authService.getCurrentUser().subscribe({
      next: (user: any) => {
        this.userName = user.UserName || user.userName || user.Email || '';
        this.userAvatar = user.Avatar ? 'data:image/jpeg;base64,' + user.Avatar : 'assets/avatar.jpg';
        this.userRating = user.Rating || 0;
        this.avatar = this.userAvatar;
        this.isLoggedIn = true;
        this.userId = user.IdUser || user.id || user.userId;
        if (this.userId !== null && this.userId !== undefined) {
          this.loadActiveExchanges(this.userId);
        }
      },
      error: () => {
        this.errorMsg = 'Ошибка авторизации';
        this.loading = false;
        this.isLoggedIn = false;
      }
    });
  }

  loadActiveExchanges(userId: number) {
    this.loading = true;
    this.bookService.getActiveExchanges(userId).subscribe({
      next: (res: any) => {
        this.activeExchanges = (res.exchanges || []).map((ex: any) => {
          // Гарантируем наличие массива категорий для обеих книг
          ex.myBook = ex.myBook || {};
          ex.theirBook = ex.theirBook || {};
          ex.myBook.categories = ex.myBook.categories || [];
          ex.theirBook.categories = ex.theirBook.categories || [];
          return ex;
        });
        this.lastUpdate = new Date();
        this.loading = false;
      },
      error: () => {
        this.errorMsg = 'Ошибка загрузки активных обменов';
        this.loading = false;
      }
    });
  }

  toggleDetails(exchange: any) {
    exchange.expanded = !exchange.expanded;
    this.activeExchanges.forEach(e => {
      if (e !== exchange) e.expanded = false;
    });
  }

  confirmExchange(exchange: any) {
    this.bookService.confirmExchange(exchange.id).subscribe({
      next: () => {
        if (this.userId !== null && this.userId !== undefined) {
          this.loadActiveExchanges(this.userId);
        }
      },
      error: () => alert('Ошибка подтверждения обмена')
    });
  }

  cancelExchange(exchange: any) {
    if (confirm('Вы уверены, что хотите отменить обмен?')) {
      this.bookService.cancelExchange(exchange.id).subscribe({
        next: () => {
          if (this.userId !== null && this.userId !== undefined) {
            this.loadActiveExchanges(this.userId);
          }
        },
        error: () => alert('Ошибка отмены обмена')
      });
    }
  }

  submitTracking(exchange: any, trackNumber: string) {
    if (!trackNumber) {
      alert('Введите трек-номер!');
      return;
    }
    this.bookService.submitTracking(exchange.id, exchange.myOfferListId, trackNumber).subscribe({
      next: () => {
        alert('Трек-номер отправлен!');
        this.loadActiveExchanges(this.userId!);
      },
      error: () => alert('Ошибка отправки трек-номера')
    });
  }

  confirmReceipt(exchange: any) {
    this.bookService.confirmReceipt(exchange.id, exchange.myOfferListId).subscribe({
      next: () => {
        if (this.userId !== null && this.userId !== undefined) {
          this.loadActiveExchanges(this.userId);
        }
      },
      error: () => alert('Ошибка подтверждения получения')
    });
  }

  showAuthAlert(event: Event) {
    event.preventDefault();
    alert('Для доступа к обменам необходимо авторизоваться!');
  }

  goToProfile() {
    this.router.navigate(['/my-exchange/personal']);
  }

  logout() {
    this.authService.logout();
    window.location.href = '/auth/login';
  }

  offerExchange(offer: any) {
    const myOfferListId = this.bookService.getIdOfferList();
    const myWishListId = this.bookService.getIdWishList();
    const theirOfferListId = offer.offerListId;
    const theirWishListId = offer.wishListId;

    if (!myOfferListId || !myWishListId || !theirOfferListId || !theirWishListId) {
      alert('Не удалось получить все необходимые данные для обмена');
      return;
    }

    this.bookService.proposeExchange(
      myOfferListId,
      myWishListId,
      theirOfferListId,
      theirWishListId
    ).subscribe({
      next: () => {
        alert('Обмен предложен!');
        // обновить список обменов, если нужно
      },
      error: () => alert('Ошибка при предложении обмена')
    });
  }

  isMyExchange(exchange: any): boolean {
    return exchange.myUserId === this.userId;
  }

  canConfirmExchange(exchange: any): boolean {
    return exchange.canConfirm && exchange.myStatusCode === 11 && exchange.partnerStatusCode === 12 && exchange.myUserId === this.userId;
  }

  canReceiveBook(exchange: any): boolean {
    // Кнопка активна, если партнер отправил книгу (статус 14) и это мой обмен
    return exchange.partnerStatusCode === 14 && exchange.myUserId === this.userId && exchange.tracking; // tracking — если вы хотите скрывать после ввода трека
  }
}
