import { Component, OnInit } from '@angular/core';
import { MessageService, UserMsg, Status } from '../../services/message.service';

@Component({
  selector: 'app-my-message',
  templateUrl: './my-message.component.html',
  styleUrls: ['./my-message.component.css']
})
export class MyMessageComponent implements OnInit {
  messages: UserMsg[] = [];
  loading = false;
  error = '';
  statuses: Status[] = [];
  emailPrefs: { [statusId: number]: boolean } = {};

  constructor(private messageService: MessageService) {}

  ngOnInit() {
    this.fetchStatuses();
    this.fetchMessages();
  }

  fetchMessages() {
    this.loading = true;
    // Здесь userId должен быть получен из авторизации или профиля пользователя
    const userId = 1; // TODO: заменить на актуальный id пользователя
    this.messageService.getReceivedMessages(userId)
      .subscribe({
        next: (msgs) => {
          this.messages = msgs;
          this.loading = false;
        },
        error: (err) => {
          this.error = 'Ошибка загрузки сообщений';
          this.loading = false;
        }
      });
  }

  fetchStatuses() {
    this.messageService.getStatuses().subscribe({
      next: (statuses) => {
        this.statuses = statuses;
        // Инициализация emailPrefs (по умолчанию все false)
        for (const s of statuses) {
          if (!(s.IdStatus in this.emailPrefs)) {
            this.emailPrefs[s.IdStatus] = false;
          }
        }
      },
      error: () => {
        this.statuses = [];
      }
    });
  }

  // Пример отправки сообщения:
  // sendMessage() {
  //   const msg: UserMsg = {
  //     IdUserMsg: 0,
  //     IdUser: 1, // id получателя
  //     Text: 'Текст сообщения',
  //     Notes: 'Примечание',
  //     IdStatus: 2, // id статуса
  //     Type: true,
  //     CreateAt: new Date().toISOString()
  //   };
  //   // Теперь письмо всегда отправляется вместе с записью в БД
  //   this.messageService.sendMessage(msg)
  //     .subscribe({
  //       next: (res) => alert('Сообщение отправлено и email отправлен!'),
  //       error: (err) => alert('Ошибка отправки')
  //     });
  // }
}
