import { Component, OnInit } from '@angular/core';
import { AuthService } from 'src/services/auth.service';
import { MessageService, UserMsg } from 'src/services/message.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-my-message',
  templateUrl: './my-message.component.html',
  styleUrls: ['./my-message.component.css']
})
export class MyMessageComponent implements OnInit {
  user: any = {};
  messages: UserMsg[] = [];
  expandedMsgs: { [id: number]: boolean } = {};
  isLoggedIn = false;
  userName: string | null = null;
  avatar: string | null = null;

  constructor(private authService: AuthService, private messageService: MessageService, private router: Router) {}

  ngOnInit() {
    const userId = this.authService.getUserId();
    if (userId) {
      this.isLoggedIn = true;
      this.authService.getUserById(userId).subscribe({
        next: (user: any) => {
          this.user = user;
          this.userName = user.UserName || user.userName || user.Email;
          if (user.Avatar) {
            this.avatar = 'data:image/jpeg;base64,' + user.Avatar;
          }
          if (user && user.IdUser) {
            this.messageService.getReceivedMessages(user.IdUser).subscribe(
              (msgs: UserMsg[]) => this.messages = msgs,
              () => this.messages = []
            );
          } else {
            this.messages = [];
          }
        },
        error: () => {
          this.isLoggedIn = false;
        }
      });
    }
    this.authService.refreshSession().subscribe({
      next: () => {},
      error: () => {}
    });
  }

  toggleMessage(msg: UserMsg, event: MouseEvent) {
    if ((event.target as HTMLElement).tagName === 'BUTTON') return;
    this.expandedMsgs[msg.IdUserMsg] = !this.expandedMsgs[msg.IdUserMsg];
  }

  deleteMessage(msg: UserMsg, event: MouseEvent) {
    event.stopPropagation();
    if (confirm('Вы уверены, что хотите удалить это сообщение?')) {
      this.messageService.deleteMessage(msg.IdUserMsg).subscribe({
        next: () => {
          this.messages = this.messages.filter(m => m.IdUserMsg !== msg.IdUserMsg);
          delete this.expandedMsgs[msg.IdUserMsg];
        },
        error: () => {
          alert('Ошибка при удалении сообщения на сервере.');
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
}
