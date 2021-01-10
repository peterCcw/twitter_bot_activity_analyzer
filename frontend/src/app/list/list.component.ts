import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { ApiService } from '../api.service';
import { dictionary } from '../dictionary';

@Component({
  selector: 'app-list',
  templateUrl: './list.component.html',
  styleUrls: ['./list.component.css']
})
export class ListComponent implements OnInit {
  dict = dictionary;

  constructor(
    private apiService: ApiService,
  ) { }

  @Output() addAccountClicked = new EventEmitter();
  accounts: any = [];

  displayedColumns: string[] = ['twitterId', 'screenName', 'delete'];

  ngOnInit(): void {
    this.apiService.getAccounts().subscribe(
      result => {
        this.accounts = result;
      },
      error => {
        console.log(error.error);
      }
    );
  }

  deleteAccount(id:number){
    this.apiService.deleteAccount(id).subscribe(
      data => {
        this.accounts = this.accounts.filter(acc => acc.id !== id);
      },
      error => console.log(error)
    );
  }

  addAccount(){
    this.addAccountClicked.emit(true);
  }
}