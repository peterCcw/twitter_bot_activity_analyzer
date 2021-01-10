import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { ApiService } from '../api.service';
import { CookieService } from 'ngx-cookie-service';
import { Observable, Subscription } from 'rxjs';
import { MatSnackBar } from '@angular/material/snack-bar';
import { dictionary } from '../dictionary';

interface TokenObj{
  token: string;
}

@Component({
  selector: 'app-auth',
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.css']
})
export class AuthComponent implements OnInit {
  dict = dictionary;

  constructor(
    private apiService: ApiService,
    private cookieService: CookieService,
    private _snackBar: MatSnackBar
  ) { }

  @Output() loggedInEmitter = new EventEmitter();

  errorMessages = null;
  @Input() mode: string;

  // forms
  logInForm = new FormGroup({
    username: new FormControl('', Validators.required),
    password: new FormControl('', Validators.required)
  });

  registerForm = new FormGroup({
    username: new FormControl('', Validators.required),
    password: new FormControl('', Validators.required),
    confirmedPassword: new FormControl('', Validators.required)
  });
  //

  // listeners of navbar buttons cliks
  private logInClickedSubscription: Subscription;
  @Input() logInClicked: Observable<void>;
  
  private registerClickedSubscription: Subscription;
  @Input() registerClicked: Observable<void>;
  //

  ngOnInit(): void {
      this.logInClickedSubscription = this.logInClicked.subscribe(() => {
      this.mode = 'logIn'
      this.logInForm.get('username').setValue('');
      this.logInForm.get('password').setValue('');
      this.errorMessages = null;
    });

    this.registerClickedSubscription = this.registerClicked.subscribe(() => {
      this.mode = 'register'
      this.registerForm.get('username').setValue('');
      this.registerForm.get('password').setValue('');
      this.registerForm.get('confirmedPassword').setValue('');
      this.errorMessages = null;
    });
  }
  
  logIn(){
    this.apiService.loginUser(this.logInForm.value).subscribe(
      (result: TokenObj) => {
        this.errorMessages = null;
        this.cookieService.set('authToken', result.token);
        this.cookieService.set('username', this.logInForm.get('username').value);
        this.loggedInEmitter.emit();
      },
      error => {
        console.log(error.error);
        this.errorMessages = error.error;
        this.openErrorBar();
      }
    );
  }

  register(){
    const formValues = {
     username: this.registerForm.get('username').value,
     password: this.registerForm.get('password').value,
     confirmed_password: this.registerForm.get('confirmedPassword').value
    }
    this.apiService.registerUser(formValues).subscribe(
      result => {
        this.logInForm.get('username').setValue(formValues.username);
        this.logInForm.get('password').setValue(formValues.password);
        this.logIn();
      },
      error => {
        this.errorMessages = error.error;
        this.openErrorBar();
      }
    );
  }

  openErrorBar() {
    let output = '';
    for (let [key, value] of Object.entries(this.errorMessages)) {
      var str: string = key + " : " + value + "\n";
      output = output.concat(str);
    }

    this._snackBar.open(output, dictionary.snackbarClose, {
      duration: 3000,
      panelClass: ['error-snackbar']
    });
  }
}
