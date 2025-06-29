import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MyActiveComponent } from './my-active.component';

describe('MyActiveComponent', () => {
  let component: MyActiveComponent;
  let fixture: ComponentFixture<MyActiveComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [MyActiveComponent]
    });
    fixture = TestBed.createComponent(MyActiveComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
