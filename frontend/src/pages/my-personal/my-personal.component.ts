import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth.service'; // Настройте путь
import { Observable } from 'rxjs';

@Component({
  selector: 'app-my-personal',
  templateUrl: './my-personal.component.html',
  styleUrls: ['./my-personal.component.css']
})
export class MyPersonalComponent implements OnInit {
  avatarPreview: string | null = null;
  userData: any; // Будет заполнен данными из сервера
  personalForm: FormGroup; // Инициализируем как FormGroup
  errorMessage: string | null = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService
  ) {
    // Инициализация формы с пустыми значениями
    this.personalForm = this.fb.group({
      lastName: ['', [Validators.required, Validators.pattern('[А-Яа-яЁё]{1,50}'), Validators.maxLength(50)]],
      firstName: ['', [Validators.required, Validators.pattern('[А-Яа-яЁё]{1,25}'), Validators.maxLength(25)]],
      middleName: ['', [Validators.pattern('[А-Яа-яЁё]{0,25}'), Validators.maxLength(25)]],
      email: ['', [Validators.required, Validators.email, Validators.maxLength(50)]],
      nickname: ['', [Validators.required, Validators.maxLength(20)]],
      password: ['', [Validators.required, Validators.minLength(8), Validators.maxLength(15)]],
      confirmPassword: ['', [Validators.required]],
      postalCode: ['', [Validators.required, Validators.pattern('\\d{6}'), Validators.maxLength(6)]],
      city: ['', [Validators.required, Validators.pattern('[А-Яа-яЁё\\s\\-]{1,15}'), Validators.maxLength(15)]],
      street: ['', [Validators.required, Validators.maxLength(25)]],
      building: ['', [Validators.pattern('[А-Яа-яЁё0-9]{0,10}'), Validators.maxLength(10)]],
      house: ['', [Validators.required, Validators.pattern('[А-Яа-яЁё0-9]{1,5}'), Validators.maxLength(5)]],
      apartment: ['', [Validators.pattern('\\d{0,3}'), Validators.maxLength(3)]]
    }, { validators: this.passwordMatchValidator });
  }

ngOnInit() {
    const userId = this.authService.getUserId();
    if (!userId) {
      this.errorMessage = 'Ошибка: ID пользователя не найден.';
      return;
    }


    // Получаем данные пользователя
    this.authService.getCurrentUser().subscribe({
      next: (userData: any) => {
        console.log('Полученные данные пользователя:', userData);
        this.userData = userData;

        // Получаем адрес пользователя
        this.authService.getUserAddress(userId).subscribe({
          next: (addressData: any) => {
            console.log('Полученные данные адреса:', addressData);
            this.personalForm.patchValue({
              lastName: userData.LastName || '',
              firstName: userData.FirstName || '',
              middleName: userData.SecondName || '',
              email: userData.Email || '',
              nickname: userData.UserName || '',
              confirmPassword: userData.Password || '', // Предполагаем, что confirmPassword = Password              
              password: userData.Password || '',
              postalCode: addressData.AddrIndex || '',
              city: addressData.AddrCity || '',
              street: addressData.AddrStreet || '',
              building: addressData.AddrStructure || '',
              house: addressData.AddrHouse || '',
              apartment: addressData.AddrApart || ''
            }, { emitEvent: false });
          },
          error: (err: any) => {
            console.error('Ошибка загрузки адреса:', err);
            this.errorMessage = 'Ошибка при загрузке адреса пользователя.';
            // Заполняем только данные пользователя, если адрес не загрузился
            this.personalForm.patchValue({
              lastName: userData.LastName || '',
              firstName: userData.FirstName || '',
              middleName: userData.SecondName || '',
              email: userData.Email || '',
              nickname: userData.UserName || '',
              confirmPassword: userData.Password || '',              
              password: userData.Password || ''

            }, { emitEvent: false });
          }
        });
      },
      error: (err: any) => {
        console.error('Ошибка загрузки данных пользователя:', err);
        this.errorMessage = 'Ошибка при загрузке данных пользователя.';
      }
    });
  }

  // Кастомный валидатор для совпадения паролей
  passwordMatchValidator(group: FormGroup) {
    const password = group.get('password')?.value;
    const confirmPassword = group.get('confirmPassword')?.value;
    return password === confirmPassword ? null : { mismatch: true };
  }

  // Генерация никнейма (до 20 символов)
  generateNickname() {
    const adjectives = ['Веселый', 'Серьезный', 'Смелый', 'Тихий', 'Быстрый', 'Умный', 'Добрый', 'Яркий'];
    const nouns = ['перец', 'заяц', 'тигр', 'волк', 'орел', 'медведь', 'сокол', 'дракон'];
    const randomAdj = adjectives[Math.floor(Math.random() * adjectives.length)];
    const randomNoun = nouns[Math.floor(Math.random() * nouns.length)];
    const nickname = `${randomAdj} ${randomNoun}`.slice(0, 20);
    this.personalForm.get('nickname')?.setValue(nickname);
  }

  // Загрузка аватара
  onAvatarUpload(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      const reader = new FileReader();
      reader.onload = (e: ProgressEvent<FileReader>) => {
        this.avatarPreview = e.target?.result as string;
        console.log('Avatar preview:', this.avatarPreview);
      };
      reader.readAsDataURL(input.files[0]);
    }
  }

  // Триггер для открытия выбора файла
  triggerFileInput() {
    document.getElementById('avatar-upload')?.click();
  }

  // Сохранение изменений
  saveChanges() {
    if (this.personalForm?.valid) {
      const userId = this.authService.getUserId();
      if (!userId) {
        this.errorMessage = 'Ошибка: ID пользователя не найден.';
        return;
      }

      const formValue = this.personalForm.value;

      const userData = {
        FirstName: formValue.firstName,
        LastName: formValue.lastName,
        SecondName: formValue.middleName,
        Email: formValue.email,
        UserName: formValue.nickname,
        Password: formValue.password,
        Avatar: this.avatarPreview || null
      };

      const addressData = {
        IdUser: userId,
        AddrIndex: formValue.postalCode,
        AddrCity: formValue.city,
        AddrStreet: formValue.street,
        AddrHouse: formValue.house,
        AddrStructure: formValue.building,
        AddrApart: formValue.apartment
      };

      this.authService.updateUser(userId, userData).subscribe({
        next: (userResponse) => {
          console.log('Данные пользователя успешно обновлены', userResponse);
          this.authService.updateAddress(userId, addressData).subscribe({
            next: (addressResponse) => {
              console.log('Данные адреса успешно обновлены', addressResponse);
              this.errorMessage = null;
              this.userData = userResponse;
              this.personalForm.patchValue({
                postalCode: addressResponse.AddrIndex,
                city: addressResponse.AddrCity,
                street: addressResponse.AddrStreet,
                building: addressResponse.AddrStructure,
                house: addressResponse.AddrHouse,
                apartment: addressResponse.AddrApart
              }, { emitEvent: false });
              alert('Данные успешно сохранены!');
            },
            error: (err) => {
              console.error('Ошибка обновления адреса', err);
              this.errorMessage = err.error?.detail || 'Ошибка при обновлении адреса';
            }
          });
        },
        error: (err) => {
          console.error('Ошибка обновления пользователя', err);
          this.errorMessage = err.error?.detail || 'Ошибка при обновления пользователя';
        }
      });
    } else {
      console.log('Форма невалидна:', this.personalForm?.errors);
      this.errorMessage = 'Проверьте введённые данные.';
    }
  }

}
