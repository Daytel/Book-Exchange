import { Component, OnInit } from '@angular/core';
import { MessageService } from 'src/services/message.service';
import { AuthService } from 'src/services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-feedback',
  templateUrl: './feedback.component.html',
  styleUrls: ['./feedback.component.css']
})
export class FeedbackComponent implements OnInit {
  question: string = '';
  successMessage: string = '';
  errorMessage: string = '';
  userName: string | null = null;
  avatar: string | null = null;
  isLoggedIn = false;

  constructor(private messageService: MessageService, private authService: AuthService, private router: Router) {}

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
  }

  goToProfile() {
    this.router.navigate(['/my-exchange/personal']);
  }

  logout() {
    this.authService.logout().subscribe(() => {
      this.authService.clearUserData && this.authService.clearUserData();
      window.location.reload();
    });
  }

  showAuthAlert(event: Event) {
    event.preventDefault();
    alert('Для доступа к разделу "Мои обмены" необходимо авторизоваться!');
  }

  onSubmit() {
    const userId = this.authService.getUserId();
    if (!userId) {
      this.errorMessage = 'Необходимо авторизоваться для отправки сообщения.';
      this.successMessage = '';
      return;
    }
    const msg = {
      IdUser: userId,
      CreateAt: new Date().toISOString(),
      Text: this.question,
      Notes: null,
      IdStatus: 21,
      Type: false
    };
    this.messageService.sendMessage(msg).subscribe({
      next: () => {
        this.successMessage = 'Ваш вопрос отправлен администратору.';
        this.errorMessage = '';
        this.question = '';
        setTimeout(() => this.successMessage = '', 4000);
      },
      error: () => {
        this.errorMessage = 'Ошибка при отправке сообщения. Попробуйте позже.';
        this.successMessage = '';
      }
    });
  }
}
