import { Component, OnInit, Input } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Observable, Subscription } from 'rxjs';
import { ApiService } from '../api.service';
import { dictionary } from '../dictionary';

@Component({
  selector: 'app-check',
  templateUrl: './check.component.html',
  styleUrls: ['./check.component.css']
})
export class CheckComponent implements OnInit {
  dict = dictionary;

  constructor(
    private apiService: ApiService,
    private _snackBar: MatSnackBar
  ) { }

  // listener for navbar button click
  private checkClickedSubscription: Subscription;
  @Input() checkClicked: Observable<void>;
  //

  result = null;
  errorMessages = null;

  checkForm = new FormGroup({
    screenName: new FormControl('', Validators.required),
  });

  ngOnInit(): void {
    this.checkClickedSubscription = this.checkClicked.subscribe(() => {
      this.result = null;
      this.checkForm.get('screenName').setValue('');
      this.errorMessages = null;
    });
  }

  checkAccount(){
    this.errorMessages = null;
    this.apiService.checkAccount(this.checkForm.get('screenName').value).subscribe(
      result=> {
        this.result = result;
      },
      error => {
        this.errorMessages = error.error;
        this.openErrorBar();
      }
    );
  }

  addToList(){
    this.apiService.addToList(this.result.twitter_id, this.result.screen_name).subscribe(
      result=> {
        this.result.added = "added";
      },
      error => {
        this.errorMessages = error.error;
        this.openErrorBar();
      }
    );
  }

  openErrorBar() {
    this._snackBar.open(this.errorMessages.message, 'Close', {
      duration: 3000,
      panelClass: ['error-snackbar']
    });
  }
}
