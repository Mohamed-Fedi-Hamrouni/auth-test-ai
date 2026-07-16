import { TestBed } from '@angular/core/testing';

import { AppComponent } from './app.component';

describe('AppComponent', () => {
  it('renders the application title', async () => {
    await TestBed.configureTestingModule({imports: [AppComponent]}).compileComponents();
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('h1').textContent).toContain('AuthTest AI');
  });
});

