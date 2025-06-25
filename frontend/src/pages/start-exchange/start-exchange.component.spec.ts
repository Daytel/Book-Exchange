import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StartExchangeComponent } from './start-exchange.component';

describe('StartExchangeComponent', () => {
  let component: StartExchangeComponent;
  let fixture: ComponentFixture<StartExchangeComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [StartExchangeComponent]
    });
    fixture = TestBed.createComponent(StartExchangeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
