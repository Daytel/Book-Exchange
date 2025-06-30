import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MyArchiveComponent } from './my-archive.component';

describe('MyArchiveComponent', () => {
  let component: MyArchiveComponent;
  let fixture: ComponentFixture<MyArchiveComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [MyArchiveComponent]
    });
    fixture = TestBed.createComponent(MyArchiveComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
