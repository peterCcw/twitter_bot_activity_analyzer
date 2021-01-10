import { Component, OnInit } from '@angular/core';
import { CookieService } from 'ngx-cookie-service';
import { AuthComponent } from './auth/auth.component';
import { ApiService } from './api.service';
import { Subject } from 'rxjs';
import { dictionary } from './dictionary';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit{
  dict = dictionary;

  constructor(
    private cookieService: CookieService,
    private apiService: ApiService,
    public authComponent: AuthComponent,
    ) { }

    component: string;

  ngOnInit(): void {
    this.checkIsLoggedAndChangeComponent('panel');
  }  

  // auth elements
  authMode: string;

  userGotLogged(val){
    this.component = 'panel';
  }

  logOut() {
    this.apiService.logoutUser().subscribe(
        result => {
          this.cookieService.delete('authToken');
          this.cookieService.delete('username');
          this.authMode = 'loggedOut';
          this.component = 'auth';
        },
        error => console.log(error)
    )
  }
  logIn() {
    this.authMode = "logIn";
    this.logInSubjectEmit();
    this.component = 'auth';
  }

  register(){
    this.authMode = 'register';
    this.registerSubjectEmit();
    this.component = 'auth';
  }

  gotLogged() {
    this.checkIsLoggedAndChangeComponent('panel');
  }


  isLogged(){
    const authToken = this.cookieService.get('authToken');
    if(authToken){
      return true;
    }
    else{
      return false;
    }
  }
  logInSubject: Subject<void> = new Subject<void>();

  logInSubjectEmit() {
    this.logInSubject.next();
  }

  registerSubject: Subject<void> = new Subject<void>();

  registerSubjectEmit() {
    this.registerSubject.next();
  }
  // end of auth elements

  //list elements
  addAccount(){
    this.checkIsLoggedAndChangeComponent('check');
  }

  displayList() {
    this.checkIsLoggedAndChangeComponent('list');
  }
  //end of list elements

  //check elements
  displayCheckAccount() {
    this.checkSubjectEmit();
    this.checkIsLoggedAndChangeComponent('check');
  }

  checkSubject: Subject<void> = new Subject<void>();

  checkSubjectEmit() {
    this.checkSubject.next();
  }
  //end of check elements

  displayHome() {
    this.checkIsLoggedAndChangeComponent('panel');
  }
  displayPanel() {
    this.checkIsLoggedAndChangeComponent('panel');
  }

  //detail elements
    detailInfo = null;

    goDetail(value){
      this.detailInfo = value;
      this.component = 'detail';
    }
  //end of detail elements

  //other elements
  title = 'frontend';
  checkIsLoggedAndChangeComponent(targetComponent: string){
    this.authMode = "logIn";
    if(this.isLogged()){
      this.component = targetComponent;
    }
    else{
      this.component = 'auth';
    }
  }
}
