import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { AuthorizationComponent } from './authorization.component';

describe('AuthorizationComponent', () => {
    let component: AuthorizationComponent;
    let fixture: ComponentFixture<AuthorizationComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [AuthorizationComponent],
            imports: [ReactiveFormsModule]
        }).compileComponents();

        fixture = TestBed.createComponent(AuthorizationComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should initialize loginForm with email and password controls', () => {
        expect(component.loginForm).toBeDefined();
        expect(component.loginForm.get('email')).toBeDefined();
        expect(component.loginForm.get('password')).toBeDefined();
    });

    it('should initialize registerForm with required controls', () => {
        expect(component.registerForm).toBeDefined();
        expect(component.registerForm.get('firstName')).toBeDefined();
        expect(component.registerForm.get('lastName')).toBeDefined();
        expect(component.registerForm.get('secondName')).toBeDefined();
        expect(component.registerForm.get('email')).toBeDefined();
        expect(component.registerForm.get('userName')).toBeDefined();
        expect(component.registerForm.get('password')).toBeDefined();
        expect(component.registerForm.get('confirmPassword')).toBeDefined();
    });

    it('should set mode to login', () => {
        component.setMode('login');
        expect(component.mode).toBe('login');
    });

    it('should set mode to register', () => {
        component.setMode('register');
        expect(component.mode).toBe('register');
    });

    it('should validate login form as invalid when empty', () => {
        expect(component.loginForm.valid).toBeFalsy();
    });

    it('should validate register form as invalid when passwords do not match', () => {
        component.registerForm.setValue({
            firstName: 'Test',
            lastName: 'User',
            secondName: '',
            email: 'test@example.com',
            userName: 'testuser',
            password: 'password123',
            confirmPassword: 'password124'
        });
        expect(component.registerForm.hasError('passwordMismatch')).toBeTruthy();
    });
});