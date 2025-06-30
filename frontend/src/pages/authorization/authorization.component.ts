import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ValidationErrors, AbstractControl } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { Observable } from 'rxjs';

@Component({
    selector: 'app-authorization',
    templateUrl: './authorization.component.html',
    styleUrls: ['./authorization.component.css']
})
export class AuthorizationComponent implements OnInit {
    // Определяем переменные
    mode: 'login' | 'register' = 'login';
    loginForm: FormGroup;
    registerForm: FormGroup;
    errorMessage: string | null = null;

    constructor(
        private fb: FormBuilder,
        private route: ActivatedRoute,
        private router: Router,
        private authService: AuthService
    ) {
        // Инициализация форм с валидацией
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

    ngOnInit(): void {
        // Логика при отображении окна (например, проверка текущей сессии)
        this.route.paramMap.subscribe(params => {
            const modeParam = params.get('mode');
            this.mode = modeParam === 'register' ? 'register' : 'login';
            this.errorMessage = null; // Сбрасываем сообщение при переключении
        });
    }

    passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
        const password = control.get('password')?.value;
        const confirmPassword = control.get('confirmPassword')?.value;
        return password === confirmPassword ? null : { passwordMismatch: true };
    }

    setMode(mode: 'login' | 'register'): void {
        this.mode = mode;
        this.errorMessage = null;
        this.router.navigate(['/auth', mode]);
    }

    onLoginSubmit(): void {
        if (this.loginForm.valid) {
            console.log('Login data:', this.loginForm.value);
            const { email, password } = this.loginForm.value;
            this.authService.login(email, password).subscribe({
                next: (response: any) => {
                    console.log('Logged in successfully', response);
                    const user = response.user;
                    const id = user.IdUser;
                    const role = user.IsStaff ? 'admin' : 'user';
                    this.authService.setUserData(id, role);
                    const redirectUrl = role === 'admin' ? '/admin' : '/';
                    this.router.navigate([redirectUrl]);
                },
                error: (err) => {
                    console.error('Login failed', err);
                    this.errorMessage = err.error?.detail || 'Неверный email или пароль';
                }
            });
        }
    }

    onRegisterSubmit(): void {
        if (this.registerForm.valid) {
            console.log('Register data:', this.registerForm.value);
            const { firstName, lastName, secondName, email, userName, password } = this.registerForm.value;
            this.authService.register({ firstName, lastName, secondName, email, userName, password }).subscribe({
                next: (response) => {
                    console.log('Registered successfully', response);
                    this.router.navigate(['/']);
                },
                error: (err) => {
                    console.error('Registration failed', err);
                    this.errorMessage = err.error?.detail || 'Ошибка при регистрации';
                }
            });
        }
    }
}
