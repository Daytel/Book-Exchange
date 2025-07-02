import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { BookService } from '../../services/book.service';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-start-exchange',
  templateUrl: './start-exchange.component.html',
  styleUrls: ['./start-exchange.component.css']
})
export class StartExchangeComponent implements OnInit {
  exchangeForm: FormGroup;
  categories: any[] = [];
  errorMsg: string = '';
  isLoggedIn = false;
  userName: string | null = null;
  avatar: string | null = null;
  isEditMode = false;

  constructor(
    private fb: FormBuilder,
    private bookService: BookService,
    private authService: AuthService,
    private router: Router
  ) {
    this.exchangeForm = this.fb.group({
      authorLastName: ['', Validators.required],
      authorFirstName: ['', Validators.required],
      bookTitle: ['', Validators.required],
      isbn: [''],
      year: ['', Validators.required]
    });
  }

  ngOnInit() {
    // --- логика авторизации ---
    const userId = this.authService.getUserId();
    if (userId) {
      this.isLoggedIn = true;
      this.authService.getUserById(userId).subscribe({
        next: (user: any) => {
          this.userName = user.UserName || user.userName || user.Email;
          if (user.Avatar) {
            this.avatar = 'data:image/jpeg;base64,' + user.Avatar;
          }
        },
        error: () => {
          this.isLoggedIn = false;
        }
      });
    }
    this.bookService.getCategories().subscribe((data: any[]) => {
      this.categories = data;
      this.categories.forEach((cat: any) => {
        if (cat.MultySelect) {
          cat.values.forEach((v: any) => v.selected = false);
        } else {
          cat.selected = null;
        }
        cat.open = false;
      });
      // --- сначала пробуем локальный offerListData ---
      const localOffer = this.bookService.getOfferListData();
      if (localOffer && localOffer.book && localOffer.categories) {
        this.exchangeForm.patchValue({
          authorLastName: localOffer.book.authorLastName || '',
          authorFirstName: localOffer.book.authorFirstName || '',
          bookTitle: localOffer.book.bookTitle || '',
          isbn: localOffer.book.isbn || '',
          year: localOffer.book.year || ''
        });
        localOffer.categories.forEach((cat: any) => {
          const localCat = this.categories.find((c: any) => c.IdCategory === cat.IdCategory);
          if (localCat) {
            if (localCat.MultySelect) {
              localCat.values.forEach((v: any) => {
                v.selected = Array.isArray(cat.selected)
                  ? cat.selected.some((id: any) => id === v.IdValueCategory)
                  : cat.selected === v.IdValueCategory;
              });
            } else {
              if (Array.isArray(cat.selected) && cat.selected.length > 0) {
                localCat.selected = cat.selected[0];
              } else if (cat.selected) {
                localCat.selected = cat.selected;
              }
            }
          }
        });
        this.isEditMode = false;
        return;
      }
      // --- если нет локального, пробуем по idOfferList ---
      const offerListId = this.bookService.getIdOfferList();
      if (offerListId) {
        this.bookService.getOfferListById(offerListId).subscribe((offer: any) => {
          if (offer && offer.book) {
            this.exchangeForm.patchValue({
              authorLastName: offer.book.authorLastName || '',
              authorFirstName: offer.book.authorFirstName || '',
              bookTitle: offer.book.bookTitle || '',
              isbn: offer.book.isbn || '',
              year: offer.book.year || ''
            });
          }
          if (offer && offer.categories && Array.isArray(offer.categories)) {
            offer.categories.forEach((cat: any) => {
              const localCat = this.categories.find((c: any) => c.IdCategory === cat.IdCategory);
              if (localCat) {
                if (localCat.MultySelect) {
                  localCat.values.forEach((v: any) => {
                    v.selected = Array.isArray(cat.IdValueCategory)
                      ? cat.IdValueCategory.some((id: any) => id === v.IdValueCategory)
                      : cat.IdValueCategory === v.IdValueCategory;
                  });
                } else {
                  if (Array.isArray(cat.IdValueCategory) && cat.IdValueCategory.length > 0) {
                    localCat.selected = cat.IdValueCategory[0];
                  } else if (cat.IdValueCategory) {
                    localCat.selected = cat.IdValueCategory;
                  }
                }
              }
            });
            this.isEditMode = true;
          }
        });
      } else {
        this.isEditMode = false;
      }
    });
  }

  goToProfile() {
    this.router.navigate(['/my-exchange/personal']);
  }

  toggleCategory(category: any) {
    category.open = !category.open;
  }

  clearAllFilters() {
    this.categories.forEach((cat: any) => {
      if (cat.MultySelect) {
        cat.values.forEach((v: any) => v.selected = false);
      } else {
        cat.selected = null;
      }
    });
  }

  onNext() {
    this.errorMsg = '';
    if (this.exchangeForm.invalid) {
      this.errorMsg = 'Пожалуйста, заполните все обязательные поля книги.';
      return;
    }
    // Проверка: выбрана хотя бы одна категория
    const selectedCategories = this.categories.map((cat: any) => {
      if (cat.MultySelect) {
        return {
          IdCategory: cat.IdCategory,
          selected: cat.values.filter((v: any) => v.selected).map((v: any) => v.IdValueCategory)
        };
      } else {
        return {
          IdCategory: cat.IdCategory,
          selected: cat.selected ? [cat.selected] : []
        };
      }
    });
    const anyCategorySelected = selectedCategories.some(cat => cat.selected.length > 0);
    if (!anyCategorySelected) {
      this.errorMsg = 'Пожалуйста, выберите хотя бы одну категорию.';
      return;
    }
    // Формируем структуру для OfferList (данные книги + выбранные категории)
    const offerListData = {
      book: this.exchangeForm.value,
      categories: selectedCategories
    };
    this.bookService.setOfferListData(offerListData);
    // Если не режим редактирования, переходим к start-get
    if (!this.isEditMode) {
      this.router.navigate(['/start-exchange/get']);
    }
    // В режиме редактирования можно добавить сохранение через saveOfferList
  }

  showAuthAlert(event: Event) {
    event.preventDefault();
    alert('Для доступа к разделу "Мои обмены" необходимо авторизоваться!');
  }

  goToAddress() {
    this.router.navigate(['start-exchange/address']);
  }

  goToGet() {
    this.router.navigate(['start-exchange/get']);
  }
} 