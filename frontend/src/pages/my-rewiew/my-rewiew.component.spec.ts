import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MyRewiewComponent } from './my-rewiew.component';

describe('MyRewiewComponent', () => {
  let component: MyRewiewComponent;
  let fixture: ComponentFixture<MyRewiewComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [MyRewiewComponent]
    });
    fixture = TestBed.createComponent(MyRewiewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
