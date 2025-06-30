import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StartAddressComponent } from './start-address.component';

describe('StartAddressComponent', () => {
  let component: StartAddressComponent;
  let fixture: ComponentFixture<StartAddressComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [StartAddressComponent]
    });
    fixture = TestBed.createComponent(StartAddressComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
