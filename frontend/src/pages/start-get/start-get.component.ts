import { Component, OnInit } from '@angular/core';
import { BookService } from '../../services/book.service';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';
import { __assign } from 'tslib';

@Component({
  selector: 'app-start-get',
  templateUrl: './start-get.component.html',
  styleUrls: ['./start-get.component.css']
})
export class StartGetComponent implements OnInit {
  categories: any[] = [];
  errorMsg: string = '';
  isLoggedIn = false;
  userName: string | null = null;
  avatar: string | null = null;
  isEditMode = false;

  constructor(
    private bookService: BookService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    // Логика авторизации (аналогично StartExchangeComponent)
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
      // --- сначала пробуем локальный wishListData ---
      const localWish = this.bookService.getWishListData();
      if (localWish && localWish.categories) {
        localWish.categories.forEach((cat: any) => {
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
      // --- если нет локального, пробуем по idWishList ---
      const idWishList = this.bookService.getIdWishList();
      if (idWishList) {
        this.bookService.getWishListById(idWishList).subscribe((wish: any) => {
          if (wish && wish.categories && Array.isArray(wish.categories)) {
            wish.categories.forEach((cat: any) => {
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

    const wishListData = {
      categories: selectedCategories,
      IdUser: this.authService.getUserId()
    };
    if (this.isEditMode) {
      this.bookService.saveWishList(wishListData).subscribe({
        next: () => {
          this.router.navigate(['start-exchange/address']);
        },
        error: () => {
          this.errorMsg = 'Ошибка при сохранении WishList. Попробуйте ещё раз.';
        }
      });
    } else {
      this.bookService.setWishListData(wishListData);
      this.router.navigate(['start-exchange/address']);
    }
  }

  goToGive() {
    this.router.navigate(['/start-exchange/give']);
  }

  goToAddress() {
    this.router.navigate(['start-exchange/address']);
  }

  goToProfile() {
    this.router.navigate(['/my-exchange/personal']);
  }

  showAuthAlert(event: Event) {
    event.preventDefault();
    alert('Для доступа к разделу "Мои обмены" необходимо авторизоваться!');
  }
}
