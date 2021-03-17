import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { CookieService } from 'ngx-cookie-service';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  constructor(
    private httpClient: HttpClient,
    private cookieService: CookieService
  ) { }

  url = 'http://127.0.0.1:8000/api/';

  headers = new HttpHeaders({
    'Content-Type': 'application/json',
  });

  getAuthHeaders(){
    const tokenStr = "Token ".concat(this.cookieService.get("authToken"));
    return new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: tokenStr});
  }

  loginUser(authData){
    const body = JSON.stringify(authData);
    const url = this.url.concat("user/login/");
    return this.httpClient.post(url, body, {headers: this.headers});
  }

  logoutUser(){
    const url = this.url.concat("user/logout/");
    return this.httpClient.get(url, {headers: this.getAuthHeaders()});
  }

  registerUser(authData){
    const url = this.url.concat("user/register/");
    const body = JSON.stringify(authData);
    return this.httpClient.post(url, body, {headers: this.getAuthHeaders()});
  }

  getAccounts(){
    const url = this.url.concat("account/");
    return this.httpClient.get(url, {headers: this.getAuthHeaders()});
  }

  deleteAccount(id: number){
    const url = this.url.concat("account/").concat(id.toString()).concat("/");
    return this.httpClient.delete(url, {headers: this.getAuthHeaders()});
  }
  
  addToList(twitter_id: number, screen_name: string){
    const url = this.url.concat('account/');
    const body = JSON.stringify({twitter_id: twitter_id, screen_name: screen_name});
    return this.httpClient.post(url, body, {headers: this.getAuthHeaders()});
  }

  checkAccount(screen_name: string){
    const url = this.url.concat("snapshot/single/");
    const params = new HttpParams().set('screen_name', screen_name);
    const options = {headers: this.getAuthHeaders(), params: params} 
    return this.httpClient.get(url, options);
  }

  getSnapshotList(id:number){
    //const url = this.url.concat('snapshots/').concat(id.toString()).concat('/list/');
    const url = this.url.concat('snapshot/').concat(id.toString()).concat('/');
	return this.httpClient.get(url, {headers: this.getAuthHeaders()});
  }

  getSnapshotDetail(id:number){
    const url = this.url.concat('snapshot/').concat(id.toString()).concat('/details/');
    return this.httpClient.get(url, {headers: this.getAuthHeaders()});
  }
}
