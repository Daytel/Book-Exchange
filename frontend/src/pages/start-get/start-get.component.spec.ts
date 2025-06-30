import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StartGetComponent } from './start-get.component';

describe('StartGetComponent', () => {
  let component: StartGetComponent;
  let fixture: ComponentFixture<StartGetComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [StartGetComponent]
    });
    fixture = TestBed.createComponent(StartGetComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
