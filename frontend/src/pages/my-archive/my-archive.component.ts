import { Component, OnInit } from '@angular/core';
import { BookService } from 'src/services/book.service';

@Component({
  selector: 'app-my-archive',
  templateUrl: './my-archive.component.html',
  styleUrls: ['./my-archive.component.css']
})
export class MyArchiveComponent implements OnInit {
  user = {
    name: 'Смелый заяц',
    avatar: 'assets/default-avatar.jpg',
    rating: 2
  };
  isLoggedIn = true; // TODO: заменить на реальную проверку авторизации
  avatar = this.user.avatar;
  userName = this.user.name;
  userRating = this.user.rating;
  userAvatar = this.user.avatar;
  archiveExchanges: any[] = [];
  lastUpdate = new Date();
  expandedIndex: number | null = null;

  constructor(private bookService: BookService) {}

  ngOnInit() {
    const userId = 1; // TODO: получить реальный userId из auth
    this.bookService.getArchiveExchanges(userId).subscribe(res => {
      this.archiveExchanges = (res.exchanges || []).map((ex: any) => ({ ...ex, expanded: false }));
      this.lastUpdate = new Date();
    });
  }

  toggleDetails(idx: number) {
    this.archiveExchanges[idx].expanded = !this.archiveExchanges[idx].expanded;
    this.archiveExchanges.forEach((e, i) => {
      if (i !== idx) e.expanded = false;
    });
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
