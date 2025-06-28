import { Component, OnInit } from '@angular/core';

interface Category {
  id: number;
  name: string;
  description: string;
}

interface Status {
  id: number;
  name: string;
  description: string;
}

interface Author {
  id: number;
  name: string;
}

interface Book {
  id: number;
  title: string;
  author: string;
  year: number;
}

interface User {
  id: number;
  nickname: string;
  email: string;
  rating: number;
  status: string;
}

@Component({
  selector: 'app-admin-panel',
  templateUrl: './admin-panel.component.html',
  styleUrls: ['./admin-panel.component.css']
})
export class AdminPanelComponent implements OnInit {
  categories: Category[] = [
    { id: 1, name: 'Программирование', description: 'Книги по программированию и IT' },
    { id: 2, name: 'Фантастика', description: 'Научная фантастика и фэнтези' }
  ];

  statuses: Status[] = [
    { id: 1, name: 'Ожидание подтверждения', description: 'Ожидает подтверждения от второго участника' },
    { id: 2, name: 'Подтвержден', description: 'Обмен подтвержден обеими сторонами' },
    { id: 3, name: 'Отправлен', description: 'Книга отправлена по почте' }
  ];

  authors: Author[] = [
    { id: 1, name: 'Иванов А.П.' },
    { id: 2, name: 'Петров С.И.' },
    { id: 3, name: 'Сидоров В.К.' }
  ];

  books: Book[] = [
    { id: 1, title: 'Основы программирования', author: 'Иванов А.П.', year: 2020 },
    { id: 2, title: 'Продвинутые алгоритмы', author: 'Петров С.И.', year: 2022 },
    { id: 3, title: 'История древнего мира', author: 'Сидоров В.К.', year: 2019 }
  ];

  users: User[] = [
    { id: 1, nickname: 'Смелый заяц', email: 'hare@example.com', rating: 4.8, status: 'Активен' },
    { id: 2, nickname: 'Золотая рыбка', email: 'fish@example.com', rating: 3.5, status: 'Активен' },
    { id: 3, nickname: 'Веселый перец', email: 'pepper@example.com', rating: 5.0, status: 'Активен' },
    { id: 4, nickname: 'Заблокированный', email: 'blocked@example.com', rating: 1.2, status: 'Заблокирован' }
  ];

  selectedUser: string = 'admin (я)';

  constructor() { }

  ngOnInit(): void { }

  logout(): void {
    console.log('Logout triggered');
  }

  editCategory(id: number): void {
    console.log(`Edit category with ID: ${id}`);
  }

  deleteCategory(id: number): void {
    this.categories = this.categories.filter(category => category.id !== id);
  }

  addCategory(): void {
    console.log('Add new category');
  }

  editStatus(id: number): void {
    console.log(`Edit status with ID: ${id}`);
  }

  deleteStatus(id: number): void {
    this.statuses = this.statuses.filter(status => status.id !== id);
  }

  addStatus(): void {
    console.log('Add new status');
  }

  editAuthor(id: number): void {
    console.log(`Edit author with ID: ${id}`);
  }

  deleteAuthor(id: number): void {
    this.authors = this.authors.filter(author => author.id !== id);
  }

  addAuthor(): void {
    console.log('Add new author');
  }

  editBook(id: number): void {
    console.log(`Edit book with ID: ${id}`);
  }

  deleteBook(id: number): void {
    this.books = this.books.filter(book => book.id !== id);
  }

  addBook(): void {
    console.log('Add new book');
  }

  blockUser(id: number): void {
    const user = this.users.find(u => u.id === id);
    if (user) user.status = 'Заблокирован';
  }

  unblockUser(id: number): void {
    const user = this.users.find(u => u.id === id);
    if (user) user.status = 'Активен';
  }

  searchUsers(): void {
    console.log('Search users');
  }
}
