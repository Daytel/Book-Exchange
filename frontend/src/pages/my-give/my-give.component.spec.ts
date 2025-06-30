import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MyGiveComponent } from './my-give.component';

describe('MyGiveComponent', () => {
  let component: MyGiveComponent;
  let fixture: ComponentFixture<MyGiveComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [MyGiveComponent]
    });
    fixture = TestBed.createComponent(MyGiveComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
