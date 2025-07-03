import { Component, OnInit } from '@angular/core';
import { BookService } from 'src/services/book.service';

interface MyWish {
  id: number;
  categories: Array<{ IdCategory: number; categoryName: string; IdValueCategory: number; valueName: string }>;
  condition: string;
  science: string;
  cover: string;
  laureate: string;
  screened: string;
  language: string;
  IdStatus: number;
}

@Component({
  selector: 'app-my-get',
  templateUrl: './my-get.component.html',
  styleUrls: ['./my-get.component.css']
})
export class MyGetComponent implements OnInit {
  user = {
    name: 'Смелый заяц',
    avatar: 'assets/default-avatar.jpg',
    rating: 2
  };
  wishes: MyWish[] = [];
  searchTime: Date = new Date();
  expandedIndex: number | null = null;

  // Для навигационной панели
  isLoggedIn = true; // TODO: заменить на реальную проверку авторизации
  avatar = this.user.avatar;
  userName = this.user.name;

  constructor(private bookService: BookService) {}

  ngOnInit() {
    const userId = 1; // TODO: получить реальный userId из auth
    this.bookService.getWishListByUser(userId).subscribe((wishes: any[]) => {
      this.wishes = wishes
        .filter(wish => wish.IdStatus !== 15)
        .map(wish => ({
          id: wish.wishId || wish.IdWishList || wish.id || 0,
          categories: wish.categories || [],
          condition: wish.condition || '',
          science: wish.science || '',
          cover: wish.cover || '',
          laureate: wish.laureate || '',
          screened: wish.screened || '',
          language: wish.language || '',
          IdStatus: wish.IdStatus
        }));
      this.searchTime = new Date();
    });
  }

  toggleDetails(event: MouseEvent, idx: number) {
    if ((event.target as HTMLElement).classList.contains('delete-btn')) {
      return;
    }
    this.expandedIndex = this.expandedIndex === idx ? null : idx;
  }

  deleteWish(event: MouseEvent, idx: number) {
    event.stopPropagation();
    const wish = this.wishes[idx];
    if (wish.IdStatus !== 11) {
      alert('Удаление возможно только если статус = 11 (поиск)');
      return;
    }
    if (confirm(`Вы уверены, что хотите удалить этот запрос на книгу?`)) {
      this.bookService.deleteWishListById(wish.id).subscribe({
        next: () => {
          this.wishes.splice(idx, 1);
          this.expandedIndex = null;
          this.searchTime = new Date();
        },
        error: (err) => {
          alert('Ошибка при удалении: ' + (err?.error?.detail || err.message));
        }
      });
    }
  }

  showAuthAlert(event: Event) {
    event.preventDefault();
    alert('Для доступа к обменам необходимо авторизоваться!');
  }

  goToProfile() {
    alert('Переход в профиль пользователя');
  }

  logout() {
    alert('Вы вышли из аккаунта!');
    this.isLoggedIn = false;
  }
}
