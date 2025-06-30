import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MyPersonalComponent } from './my-personal.component';

describe('MyPersonalComponent', () => {
  let component: MyPersonalComponent;
  let fixture: ComponentFixture<MyPersonalComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [MyPersonalComponent]
    });
    fixture = TestBed.createComponent(MyPersonalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
