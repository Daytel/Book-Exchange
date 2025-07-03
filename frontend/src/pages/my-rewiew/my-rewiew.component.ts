import { Component, OnInit } from '@angular/core';
import { AuthService } from 'src/services/auth.service';
import { BookService } from 'src/services/book.service';

interface Author {
  id: number;
  name: string;
}

interface Book {
  id: number;
  title: string;
}

interface Review {
  author: string;
  date: string;
  preview: string;
  full: string;
  expanded: boolean;
}

@Component({
  selector: 'app-my-rewiew',
  templateUrl: './my-rewiew.component.html',
  styleUrls: ['./my-rewiew.component.css']
})
export class MyRewiewComponent implements OnInit {
  authors: any[] = [];
  books: any[] = [];
  selectedAuthorId: number | null = null;
  selectedBookId: number | null = null;

  activeTab: 'leave' | 'view' = 'leave';

  reviewText: string = '';

  reviews: Review[] = [
    {
      author: 'Книголюб',
      date: '15.06.2024',
      preview: 'Эта книга произвела на меня огромное впечатление. Автор мастерски раскрывает сложные темы, делая их доступными для понимания. Персонажи прописаны очень детально, сюжет захватывает с первых страниц...',
      full: 'Эта книга произвела на меня огромное впечатление. Автор мастерски раскрывает сложные темы, делая их доступными для понимания. Персонажи прописаны очень детально, сюжет захватывает с первых страниц. Особенно хочется отметить глубокую проработку мира, в котором разворачиваются события. Несмотря на объем, книга читается на одном дыхании. Рекомендую всем, кто интересуется современной литературой в этом жанре. Однозначно одна из лучших книг, которые я читал за последнее время.',
      expanded: false
    },
    {
      author: 'Литератор',
      date: '10.06.2024',
      preview: 'Интересный взгляд на привычные вещи. Книга заставляет задуматься о многих аспектах нашей жизни. Стиль автора легкий и приятный, хотя иногда чувствуется некоторая поверхностность в раскрытии...',
      full: 'Интересный взгляд на привычные вещи. Книга заставляет задуматься о многих аспектах нашей жизни. Стиль автора легкий и приятный, хотя иногда чувствуется некоторая поверхностность в раскрытии второстепенных персонажей. Основная сюжетная линия выстроена грамотно, с неожиданными поворотами. Особенно порадовала концовка - она оказалась не такой предсказуемой, как можно было предположить в начале. В целом, хорошая книга для неторопливого чтения, но не без недостатков. Подойдет для любителей этого жанра.',
      expanded: false
    }
  ];

  user: any = {};

  constructor(
    private bookService: BookService,
    private authService: AuthService
  ) {}

  ngOnInit() {
    this.authService.getCurrentUser().subscribe(
      (user: any) => {
        this.user = user;
      },
      () => {
        this.user = { UserName: 'Гость', Avatar: 'assets/default-avatar.jpg', Rating: 0 };
      }
    );
    this.bookService.getAuthors().subscribe(authors => {
      this.authors = authors;
    });
  }

  onAuthorChange() {
    this.selectedBookId = null;
    if (this.selectedAuthorId) {
      this.bookService.getBooksByAuthor(this.selectedAuthorId).subscribe(books => {
        this.books = books;
      });
    } else {
      this.books = [];
    }
  }

  switchTab(tab: 'leave' | 'view') {
    this.activeTab = tab;
  }

  toggleReview(review: Review) {
    review.expanded = !review.expanded;
  }

  submitReview() {
    if (this.reviewText.trim()) {
      alert('Ваш отзыв отправлен: ' + this.reviewText);
      this.reviewText = '';
    }
  }
}
