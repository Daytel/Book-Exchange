import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-my-personal',
  templateUrl: './my-personal.component.html',
  styleUrls: ['./my-personal.component.css']
})
export class MyPersonalComponent implements OnInit {
  avatarPreview: string | null = null;
  userData = {
    lastName: '',
    firstName: '',
    middleName: '',
    email: '',
    nickname: '',
    password: '',
    confirmPassword: '',
    postalCode: '',
    city: '',
    street: '',
    building: '',
    house: '',
    apartment: ''
  };
  personalForm!: FormGroup;

  constructor(private fb: FormBuilder) {}

  ngOnInit() {
    this.personalForm = this.fb.group({
      lastName: ['', [Validators.required, Validators.pattern('[А-Яа-яЁё]{1,50}'), Validators.maxLength(50)]],
      firstName: ['', [Validators.required, Validators.pattern('[А-Яа-яЁё]{1,25}'), Validators.maxLength(25)]],
      middleName: ['', [Validators.pattern('[А-Яа-яЁё]{0,25}'), Validators.maxLength(25)]],
      email: ['', [Validators.required, Validators.email, Validators.maxLength(50)]],
      nickname: ['', [Validators.required, Validators.maxLength(20)]], // Убрали pattern
      password: ['', [Validators.required, Validators.minLength(8), Validators.maxLength(15)]], // Упрощённый валидатор пароля
      confirmPassword: ['', [Validators.required]],
      postalCode: ['', [Validators.required, Validators.pattern('\\d{6}'), Validators.maxLength(6)]],
      city: ['', [Validators.required, Validators.pattern('[А-Яа-яЁё\\s\\-]{1,15}'), Validators.maxLength(15)]],
      street: ['', [Validators.required, Validators.maxLength(25)]], // Убрали pattern
      building: ['', [Validators.pattern('[А-Яа-яЁё0-9]{0,10}'), Validators.maxLength(10)]],
      house: ['', [Validators.required, Validators.pattern('[А-Яа-яЁё0-9]{1,5}'), Validators.maxLength(5)]],
      apartment: ['', [Validators.pattern('\\d{0,3}'), Validators.maxLength(3)]]
    }, { validators: this.passwordMatchValidator });

    // Инициализация формы данными
    this.personalForm.patchValue(this.userData);
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
    if (this.personalForm.valid) {
      this.userData = { ...this.personalForm.value };
      console.log('Данные сохранены:', this.userData);
      alert('Данные успешно сохранены!');
      // Здесь можно добавить логику отправки данных на сервер
    } else {
      console.log('Форма невалидна:', this.personalForm.errors);
    }
  }
}