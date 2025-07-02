import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { BookService } from '../../services/book.service';

@Component({
  selector: 'app-start-address',
  templateUrl: './start-address.component.html',
  styleUrls: ['./start-address.component.css']
})
export class StartAddressComponent implements OnInit {
  addressForm: FormGroup;
  isLoggedIn = false;
  userName: string | null = null;
  avatar: string | null = null;
  errorMsg = '';
  successMsg = '';
  isEditMode = false;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private authService: AuthService,
    private bookService: BookService
  ) {
    this.addressForm = this.fb.group({
      city: ['', Validators.required],
      street: ['', Validators.required],
      building: [''],
      house: ['', Validators.required],
      flat: [''],
      index: ['', [Validators.required, Validators.pattern(/^\d{6}$/)]],
      surname: ['', Validators.required],
      name: ['', Validators.required],
      patronymic: [''],
    });
  }

  ngOnInit() {
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
    // --- автозаполнение формы ---
    const localAddress = this.bookService.getAddressData();
    if (localAddress) {
      this.addressForm.patchValue(localAddress);
      this.isEditMode = false;
      return;
    }
    const idAddress = this.bookService.getIdAddress();
    if (idAddress) {
      this.bookService.getAddressById(idAddress).subscribe({
        next: (data: any) => {
          this.addressForm.patchValue(data);
          this.isEditMode = true;
        },
        error: () => {
          this.errorMsg = 'Ошибка при получении адреса из базы данных.';
        }
      });
    }
  }

  onSubmit() {
    this.errorMsg = '';
    this.successMsg = '';
    if (this.addressForm.invalid) {
      this.errorMsg = 'Пожалуйста, заполните все обязательные поля.';
      return;
    }
    if (this.isEditMode) {
      // В режиме редактирования не используем onSubmit
      return;
    }
    // Сохраняем локально
    this.bookService.setAddressData(this.addressForm.value);
    if (!this.isLoggedIn) {
      this.errorMsg = 'Вы не авторизованы. Пожалуйста, авторизуйтесь для завершения обмена.';
      return;
    }
    // Формируем данные для backend
    const formValue = this.addressForm.value;
    const addressData: any = {
      IdUser: this.authService.getUserId(),
      AddrIndex: formValue.index,
      AddrCity: formValue.city,
      AddrStreet: formValue.street,
      AddrHouse: formValue.house
    };

    if (formValue.building) {
      addressData.AddrStructure = formValue.building;
    }
    if (formValue.flat) {
      addressData.AddrApart = formValue.flat;
    }

    this.bookService.saveAddress(addressData).subscribe({
      next: (res: any) => {
        if (res && res.idUserAddress) {
          // Отправляем все данные (адрес, offerList, wishList)
          this.bookService.sendFullExchange().subscribe({
            next: () => {
              this.successMsg = 'Заявка создана!';
              this.router.navigate(['/my-exchange/offers']);
            },
            error: () => {
              this.errorMsg = 'Ошибка при отправке данных обмена.';
            }
          });
        } else {
          this.errorMsg = 'Ошибка при сохранении адреса.';
        }
      },
      error: () => {
        this.errorMsg = 'Ошибка при сохранении адреса.';
      }
    });
  }

  onSave() {
    this.errorMsg = '';
    this.successMsg = '';
    if (!this.isLoggedIn) {
      this.errorMsg = 'Вы не авторизованы.';
      return;
    }
    if (this.addressForm.invalid) {
      this.errorMsg = 'Пожалуйста, заполните все обязательные поля.';
      return;
    }
    const idAddress = this.bookService.getIdAddress();
    if (!idAddress) {
      this.errorMsg = 'Не найден id адреса для обновления.';
      return;
    }
    // Формируем данные для backend
    const formValue = this.addressForm.value;
    const addressData: any = {
      IdUser: this.authService.getUserId(),
      AddrIndex: formValue.index,
      AddrCity: formValue.city,
      AddrStreet: formValue.street,
      AddrHouse: formValue.house
    };

    if (formValue.building) {
      addressData.AddrStructure = formValue.building;
    }
    if (formValue.flat) {
      addressData.AddrApart = formValue.flat;
    }

    this.bookService.updateAddressById(idAddress, addressData).subscribe({
      next: () => {
        this.successMsg = 'Адрес успешно обновлён!';
      },
      error: () => {
        this.errorMsg = 'Ошибка при обновлении адреса.';
      }
    });
  }

  goToGive() {
    this.router.navigate(['start-exchange/give']);
  }

  goToGet() {
    this.router.navigate(['start-exchange/get']);
  }

  goToProfile() {
    this.router.navigate(['/my-exchange/personal']);
  }

  showAuthAlert(event: Event) {
    event.preventDefault();
    alert('Для доступа к разделу "Мои обмены" необходимо авторизоваться!');
  }
}
