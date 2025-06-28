import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { RouterModule, Routes } from '@angular/router';
import { AppComponent } from './app.component';
import { NotFoundErrorComponent } from '../pages/not-found-error/not-found-error.component';
import { MainPageComponent } from '../pages/main-page/main-page.component';
import { AuthorizationComponent } from 'src/pages/authorization/authorization.component';
import { MyExchangeComponent } from 'src/pages/my-exchange/my-exchange.component';
import { StartExchangeComponent } from 'src/pages/start-exchange/start-exchange.component';
import { CheckEmailComponent } from 'src/pages/check-email/check-email.component';
import { VerifyEmailComponent } from 'src/pages/verify-email/verify-email.component';
import { FeedbackComponent } from '../pages/feedback/feedback.component';
import { AdminPanelComponent } from 'src/pages/admin-panel/admin-panel.component';

const routes: Routes = [
  {path: '', component: MainPageComponent},
  {path: 'auth/:mode', component: AuthorizationComponent}, // Регистрация и авторизация
  {path: 'check-email', component: CheckEmailComponent}, // Отправка письма подтверждения
  {path: 'verify-email', component: VerifyEmailComponent}, // Ручка обработки подтверждения авторизации
  {path: 'my-exchange', component: MyExchangeComponent}, // ЛК
  {path: 'start-exchange', component: StartExchangeComponent}, // Страница обмена
  {path: 'feedback', component: FeedbackComponent}, // Обратная связь
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
    AdminPanelComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    RouterModule.forRoot(routes)
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
