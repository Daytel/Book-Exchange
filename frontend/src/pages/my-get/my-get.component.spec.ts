import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MyGetComponent } from './my-get.component';

describe('MyGetComponent', () => {
  let component: MyGetComponent;
  let fixture: ComponentFixture<MyGetComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [MyGetComponent]
    });
    fixture = TestBed.createComponent(MyGetComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
