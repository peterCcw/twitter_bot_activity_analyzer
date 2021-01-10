import { Component, Input, OnInit } from '@angular/core';
import { ApiService } from '../api.service';
import { dictionary } from '../dictionary';

@Component({
  selector: 'app-detail',
  templateUrl: './detail.component.html',
  styleUrls: ['./detail.component.css']
})
export class DetailComponent implements OnInit {
  dict = dictionary;

  constructor(
    private apiService: ApiService,
  ) { }

  @Input() detailInfo = null;

  allSnapshots = null;
  detailedSnapshot = null;

  nextButtonAvailable = false;
  previousButtonAvailable = false;

  ngOnInit(): void {
    this.apiService.getSnapshotList(this.detailInfo.accountId).subscribe(
      result => {
        this.allSnapshots = result;

        if(this.detailInfo.snapshotId != null){
          this.apiService.getSnapshotDetail(this.detailInfo.snapshotId).subscribe(
            result => {
              this.detailedSnapshot = result;
              this.buttonsCheck();
            },
            error => {
              console.log(error.error);
            }
          );
        }
        else{
          var id = this.allSnapshots[this.allSnapshots.length - 1].id;
          this.apiService.getSnapshotDetail(id).subscribe(
            result => {
              this.detailInfo.snapshotId = id;
              this.detailedSnapshot = result;
              this.buttonsCheck();
            },
            error => {
              console.log(error.error);
            }
          );
        }
      },
      error => {
        console.log(error.error);
      }
    );
  }

  nextSnapshot(){
    var index = this.allSnapshots.findIndex(acc => acc.id == this.detailInfo.snapshotId);
    var idOfNext = this.allSnapshots[index + 1].id;
    this.apiService.getSnapshotDetail(idOfNext).subscribe(
      result => {
        this.detailedSnapshot = result;
        this.detailInfo = {snapshotId: idOfNext, accountId: this.detailInfo.accountId};
        this.buttonsCheck();
      },
      error => {
        console.log(error.error);
      }
    );
  }

  previousSnapshot(){
    var index = this.allSnapshots.findIndex(acc => acc.id == this.detailInfo.snapshotId);
    var idOfPrevious = this.allSnapshots[index - 1].id;
    this.apiService.getSnapshotDetail(idOfPrevious).subscribe(
      result => {
        this.detailedSnapshot = result;
        this.detailInfo = {snapshotId: idOfPrevious, accountId: this.detailInfo.accountId};
        this.buttonsCheck();
      },
      error => {
        console.log(error.error);
      }
    );
  }

  buttonsCheck(){
    var index = this.allSnapshots.findIndex(acc => acc.id == this.detailInfo.snapshotId);
      if(this.allSnapshots[index + 1] != null){
        this.nextButtonAvailable = true;
      }
      else{
        this.nextButtonAvailable = false;
      }
      if(this.allSnapshots[index - 1] != null){
        this.previousButtonAvailable = true;
      }
      else{
        this.previousButtonAvailable = false;
      }
  }
}
