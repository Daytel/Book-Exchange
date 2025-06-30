import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-main-page',
  templateUrl: './main-page.component.html',
  styleUrls: ['./main-page.component.css']
})
export class MainPageComponent implements OnInit {
  isLoggedIn = false;
  userName: string | null = null;
  avatar: string | null = null;

  constructor(private authService: AuthService, private router: Router) {}

  ngOnInit(): void {
    const userId = this.authService.getUserId();
    if (userId) {
      this.isLoggedIn = true;
      this.authService.getUserById(userId).subscribe({
        next: (user: any) => {
          this.userName = user.UserName || user.userName || user.Email;
          if (user.Avatar) {
            this.avatar = 'data:image/png;base64,' + user.Avatar;
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
      this.authService.clearUserData();
      window.location.reload();
    });
  }
}
