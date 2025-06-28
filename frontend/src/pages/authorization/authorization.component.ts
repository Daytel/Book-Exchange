
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ValidationErrors, AbstractControl } from '@angular/forms';

@Component({
    selector: 'app-authorization',
    templateUrl: './authorization.component.html',
    styleUrls: ['./authorization.component.css']
})
export class AuthorizationComponent implements OnInit {
    mode: 'login' | 'register' = 'login';
    loginForm: FormGroup;
    registerForm: FormGroup;

    constructor(private fb: FormBuilder) {
        this.loginForm = this.fb.group({
            email: ['', [Validators.required, Validators.email]],
            password: ['', [Validators.required, Validators.maxLength(15)]]
        });

        this.registerForm = this.fb.group({
            firstName: ['', Validators.required],
            lastName: ['', Validators.required],
            secondName: [''],
            email: ['', [Validators.required, Validators.email]],
            userName: ['', Validators.required],
            password: ['', [Validators.required, Validators.maxLength(15)]],
            confirmPassword: ['', [Validators.required, Validators.maxLength(15)]]
        }, { validators: this.passwordMatchValidator });
    }

    ngOnInit(): void {}

    // Валидатор для проверки совпадения паролей
    passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
        const password = control.get('password')?.value;
        const confirmPassword = control.get('confirmPassword')?.value;
        return password === confirmPassword ? null : { passwordMismatch: true };
    }

    setMode(mode: 'login' | 'register'): void {
        this.mode = mode;
    }

    onLoginSubmit(): void {
        if (this.loginForm.valid) {
            console.log('Login data:', this.loginForm.value);
            // TODO: Отправить данные на сервер для авторизации
        }
    }

    onRegisterSubmit(): void {
        if (this.registerForm.valid) {
            console.log('Register data:', this.registerForm.value);
            // TODO: Отправить данные на сервер для регистрации
        }
    }
}
