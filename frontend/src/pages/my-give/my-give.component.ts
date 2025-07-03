import { Component, OnInit } from '@angular/core';
import { BookService } from 'src/services/book.service';

interface MyBook {
  id: number;
  author: string;
  title: string;
  genre: string;
  year: number;
  condition: string;
  science: string;
  cover: string;
  laureate: string;
  screened: string;
  language: string;
  IdStatus: number;
}

@Component({
  selector: 'app-my-give',
  templateUrl: './my-give.component.html',
  styleUrls: ['./my-give.component.css']
})
export class MyGiveComponent implements OnInit {
  user = {
    name: 'Смелый заяц',
    avatar: 'assets/default-avatar.jpg',
    rating: 2
  };
  books: MyBook[] = [];
  searchTime: Date = new Date();
  expandedIndex: number | null = null;

  // Для навигационной панели
  isLoggedIn = true; // TODO: заменить на реальную проверку авторизации
  avatar = this.user.avatar;
  userName = this.user.name;

  constructor(private bookService: BookService) {}

  ngOnInit() {
    const userId = 1; // TODO: получить реальный userId из auth
    this.bookService.getOfferListByUser(userId).subscribe((offers: any[]) => {
      this.books = offers
        .filter(offer => offer.IdStatus !== 15)
        .map(offer => ({
          id: offer.offerId || offer.IdOfferList || offer.id || 0,
          author: offer.book?.authorLastName + ' ' + offer.book?.authorFirstName || offer.author || '',
          title: offer.book?.bookTitle || offer.title || '',
          genre: offer.book?.genre || offer.genre || '',
          year: offer.book?.year || offer.year || 0,
          condition: offer.condition || '',
          science: offer.science || '',
          cover: offer.cover || '',
          laureate: offer.laureate || '',
          screened: offer.screened || '',
          language: offer.language || '',
          IdStatus: offer.IdStatus
        }));
      this.searchTime = new Date();
    });
  }

  toggleDetails(event: MouseEvent, idx: number) {
    if ((event.target as HTMLElement).classList.contains('delete-btn') || (event.target as HTMLElement).classList.contains('exchange-btn')) {
      return;
    }
    this.expandedIndex = this.expandedIndex === idx ? null : idx;
  }

  deleteBook(event: MouseEvent, idx: number) {
    event.stopPropagation();
    const book = this.books[idx];
    if (book.IdStatus !== 11) {
      alert('Удаление возможно только если статус = 11 (поиск)');
      return;
    }
    if (confirm(`Вы уверены, что хотите удалить книгу "${book.title}" из списка для обмена?`)) {
      this.bookService.deleteOfferListById(book.id).subscribe({
        next: () => {
          this.books.splice(idx, 1);
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
    // TODO: переход к профилю пользователя
    alert('Переход в профиль пользователя');
  }

  logout() {
    // TODO: реальная логика выхода
    alert('Вы вышли из аккаунта!');
    this.isLoggedIn = false;
  }
}
