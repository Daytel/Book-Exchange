import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { RouterModule, Routes } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { NotFoundErrorComponent } from '../pages/not-found-error/not-found-error.component';
import { MainPageComponent } from '../pages/main-page/main-page.component';
import { AuthorizationComponent } from 'src/pages/authorization/authorization.component';
import { MyExchangeComponent } from 'src/pages/my-exchange/my-exchange.component';
import { StartExchangeComponent } from 'src/pages/start-exchange/start-exchange.component';
import { CheckEmailComponent } from 'src/pages/check-email/check-email.component';
import { VerifyEmailComponent } from 'src/pages/verify-email/verify-email.component';
import { FeedbackComponent } from '../pages/feedback/feedback.component';


import { HTTP_INTERCEPTORS } from '@angular/common/http';

import { AdminPanelComponent } from 'src/pages/admin-panel/admin-panel.component';
import { MyGiveComponent } from 'src/pages/my-give/my-give.component';
import { MyGetComponent } from '../pages/my-get/my-get.component';
import { MyActiveComponent } from 'src/pages/my-active/my-active.component';
import { MyPersonalComponent } from 'src/pages/my-personal/my-personal.component';
import { MyRewiewComponent } from 'src/pages/my-rewiew/my-rewiew.component';
import { MyMessageComponent } from 'src/pages/my-message/my-message.component';
import { MyArchiveComponent } from 'src/pages/my-archive/my-archive.component';
import { StartGetComponent } from 'src/pages/start-get/start-get.component';
import { StartAddressComponent } from '../pages/start-address/start-address.component';
import { AuthService } from 'src/services/auth.service';
import { AuthInterceptor } from 'src/services/auth.interceptor';

const routes: Routes = [
  {path: '', component: MainPageComponent}, // Главная страница
  {path: 'auth/login', component: AuthorizationComponent}, // Авторизация
  {path: 'auth/register', component: AuthorizationComponent}, // Регистрация
  {path: 'check-email', component: CheckEmailComponent}, // Отправка письма подтверждения
  {path: 'verify-email', component: VerifyEmailComponent}, // Ручка обработки подтверждения авторизации
  {path: 'my-exchange/offers', component: MyExchangeComponent}, // Мои обмены / Предложения обмена
  {path: 'my-exchange/give', component: MyGiveComponent}, // Мои обмены / Хочу обменять
  {path: 'my-exchange/get', component: MyGetComponent}, // Мои обмены / Хочу получить
  {path: 'my-exchange/active', component: MyActiveComponent}, // Мои обмены / Активные обмены
  {path: 'my-exchange/rewiews', component: MyRewiewComponent}, // Мои обмены / Отзывы на книги
  {path: 'my-exchange/personal', component: MyPersonalComponent}, // VМои обмены / Личные данные
  {path: 'my-exchange/messages', component: MyMessageComponent}, // Мои обмены / Сообщения
  {path: 'my-exchange/archive', component: MyArchiveComponent}, // Мои обмены / Архив
  {path: 'start-exchange/give', component: StartExchangeComponent}, // Бланк обмена / Хочу обменять
  {path: 'start-exchange/get', component: StartGetComponent}, // Бланк обмена / Хочу получить
  {path: 'start-exchange/address', component: StartAddressComponent}, // Бланк обмена / Доставка
  {path: 'feedback', component: FeedbackComponent}, // Задать вопрос
  {path: 'admin', component: AdminPanelComponent}, // Админка
  {path: '**', component: NotFoundErrorComponent} // Страница для ошибок
];

@NgModule({
  declarations: [
    AppComponent,
    MainPageComponent,
    AuthorizationComponent,
    CheckEmailComponent,
    VerifyEmailComponent,
    MyExchangeComponent,
    StartExchangeComponent,
    FeedbackComponent,
    NotFoundErrorComponent,
    AdminPanelComponent,
    MyGiveComponent,
    MyGetComponent,
    StartAddressComponent,
    MyActiveComponent,
    MyRewiewComponent,
    MyPersonalComponent,
    MyMessageComponent,
    MyArchiveComponent,
    StartGetComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule, ReactiveFormsModule, HttpClientModule, FormsModule,
    RouterModule.forRoot(routes)
  ],
  providers: [ AuthService,
          {
            provide: HTTP_INTERCEPTORS,
            useClass: AuthInterceptor,
            multi: true
        }],

  bootstrap: [AppComponent]
})
export class AppModule { }
