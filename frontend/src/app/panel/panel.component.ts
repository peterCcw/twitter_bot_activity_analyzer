import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MatSelectionListChange } from '@angular/material/list';
import { ApiService } from '../api.service';
import { Chart } from 'node_modules/chart.js';
import { dictionary } from '../dictionary';
import { colors } from '../colors';

interface accountListElement{
  id: number;
  screenName: string;
  isSelected: boolean;
  snapshots: any[];
}

@Component({
  selector: 'app-panel',
  templateUrl: './panel.component.html',
  styleUrls: ['./panel.component.css']
})
export class PanelComponent implements OnInit {
  dict = dictionary;
  cols = colors;

  constructor(
    private apiService: ApiService,
  ) { }

  accounts: accountListElement[] = []; // all accounts
  dates = []; // date objects for every day from start to end from form
  datasets = [];  // snapshots of selected account matching dates

  ctx = null;
  myChart = null;

  formGroup = new FormGroup({
    startDate: new FormControl('', Validators.required),
    endDate: new FormControl('', Validators.required),
    });


  @Output() detailEmitter = new EventEmitter();

  ngOnInit(): void {
    this.ctx = document.getElementById('myChart');

    var currentDate = new Date();
    var currDateMinus7 = new Date(currentDate.getTime() - (7 * 24 * 60 * 60 * 1000));

    this.formGroup.get('startDate').setValue(currDateMinus7);
    this.formGroup.get('endDate').setValue(currentDate);

    
    this.apiService.getAccounts().subscribe(
      result => {   // gets all accounts belonging to user from the server
        for (let key in result) {
          let value = result[key];
          let snapshots;
          this.apiService.getSnapshotList(value.id).subscribe(
            result =>{  // gets all snapshots for specific account
              snapshots = result;

              let new_element: accountListElement = {
                id: value.id,
                screenName: value.screen_name,
                isSelected: true,
                snapshots: snapshots
              }
              this.accounts.push(new_element);
              this.prepareData();
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

  prepareData(){
    this.dates = null;
    this.datasets = null;

    var form = this.formGroup;

    if(form.get('startDate').value != null && form.get('endDate').value != null && form.get('startDate').value != '' && form.get('endDate').value != ''){ //checks if fields are filled
      // unix timestamps od beginning and end
      var startTimestamp = Date.parse(form.get('startDate').value);
      var endTimestamp = Date.parse(form.get('endDate').value);

      //date set creating
        var dates = [];
        var date: Date = new Date(startTimestamp);
        date = new Date(Number(date.getTime()) + (60 * 60 * 1000));
        while(Number(date.getTime()) <= Number(form.get('endDate').value.getTime()) + (60 * 60 * 1000)){
          dates.push(date);
          var nextDate = new Date(date.getTime() + (24 * 60 * 60 * 1000));
          date = nextDate;
        }
        var outputDates = [];
        var self = this;
        dates.forEach(function(date: Date){
          var outputDate: string = '';
          outputDates.push(self.dateToString(date));
        });
      //

      var datasets = []; // datasets for chart

      // finding matching snapshots and preparing datasets
      this.accounts.forEach(function (account) {
        if(account.isSelected == true){
          
          // finding snapshots between startdate and enddate
          var snapshots = [];
          account.snapshots.forEach(function(snapshot){
            var snapshotTimestamp = Date.parse(snapshot.date_of_snapshot);
            if(snapshotTimestamp > startTimestamp && snapshotTimestamp < endTimestamp + (24 * 60 * 60 * 1000)){
              snapshots.push({
                snapshot: snapshot,
                date: new Date(snapshotTimestamp)
              });
            }
          });
          //

          // preparing dataset for days since startdate to enddate (nulls for days without snapshot, snapshot for days with snapshot)
          var data = [];
          dates.forEach(function(date){
            var id = snapshots.findIndex(snapshot => snapshot.date.getDate() == date.getDate() && snapshot.date.getMonth() == date.getMonth() && snapshot.date.getFullYear() == date.getFullYear());
            if(id != -1){
              data.push(snapshots[id].snapshot);
            }
            else{
              data.push(null);
            }
          });
          datasets.push(data);
          //
        }
      });
      //

      this.datasets = datasets;
      this.dates = outputDates;
      this.generatePlot();
    }
  }

  generatePlot(){
    var colors = this.cols;
    
    var datasets = [];
    var colorArrId = 0;
    this.datasets.forEach(function (dataset){
      var datasetScores = [];
      dataset.forEach(function(data){ // prepares array of scores (for Y-axis of chart)
        if(data != null){
          datasetScores.push(data.bot_score);
        }
        else{
          datasetScores.push(null);
        }
      });
      if(dataset.find(snap => snap != null) != undefined){  // push data to final dataset if there is at least one snapshot
        var accountScreenName = dataset.find(snap => snap != null).screen_name;
        datasets.push(  
        { 
          data: datasetScores,
          label: accountScreenName,
          borderColor: colors[colorArrId],
          backgroundColor: colors[colorArrId],
          fill: false,
          snapshots: dataset
          }
        );
        colorArrId = colorArrId + 1;
      }
    });

    if(this.myChart != null){   // destroys previous chart (prevents tooltip issues and others)
      this.myChart.destroy();
    }

    this.myChart = new Chart(this.ctx, {
      type: 'line',
      data: {
        labels: this.dates,
        datasets: datasets,
      },
      options: {
        title: {
          display: true,
          text: this.dict.botScores,
          fontSize: 20,
        },
        legend: {
          display: true,
          position: "bottom",
      },
        tooltips: {
          callbacks: {
            label: function(tooltipItem, data){ // label format: <color> - <screen name> - <full name>
              var snap = data.datasets[tooltipItem.datasetIndex].snapshots[tooltipItem.index];
              var label = " - " + snap.screen_name + " - " + snap.name;
              return label;
            },
            afterBody: function(tooltipItem, data) {  // prints data about score and features (features in order from most to least important)
              var snap = data.datasets[tooltipItem[0].datasetIndex].snapshots[tooltipItem[0].index];

              var snapshotId: any = document.getElementById("hiddenSnapshotId");
              snapshotId.value = snap.id;
  
              var accountId: any = document.getElementById("hiddenAccountId");
              accountId.value = snap.account;

              var tooltipString = [];
              tooltipString.push('');
              tooltipString.push(dictionary.score + ': ' + snap.bot_score.toPrecision(4));
              tooltipString.push('');
              tooltipString.push(dictionary.features + ":")
              for (let key in snap.features) {
                let value = snap.features[key];
                tooltipString.push("  - " + key + ": " + value);
              }
              return tooltipString;
            }
          },
        },
      }
    });

    var chart = this.myChart;

    this.ctx.onclick = function (evt) { // click on specific point on the chart
      var clickData = chart.getElementsAtEvent(evt);
      if(clickData[0] != null){
        var snapshotId: any = document.getElementById("hiddenSnapshotId");
        snapshotId.click();
      }
    };
  }

  dateToString(dateInput: Date){
    // converts Date obj to format dd-mm-yy
    var date = dateInput;
    var outputDate: string = '';
        
    var day: any = date.getDate();
    if(day < 10){
      day = '0' + day.toString();
    }
    else{
      day = day.toString();
    }
    outputDate = outputDate + day;
    outputDate = outputDate + "-";
        
    var month: any = date.getMonth();
    month = month + 1;
    if(month < 10){
      month = '0' + month.toString();
    }
    else{
      month = month.toString();
    }
    outputDate = outputDate + month;
    outputDate = outputDate + "-";
        
    var year = date.getFullYear();
    outputDate = outputDate + year.toString().substr((year.toString().length - 2));
    return outputDate;
  }

  onChangeList(change: MatSelectionListChange) { // changes isSelected property of clicked account
    var changed = this.accounts.filter(acc => acc.id == change.option.value)[0];
    if(change.option.selected == true){
      changed.isSelected = true;
    }
    else{
      changed.isSelected = false;
    }
    this.prepareData();
 }

  goSnapshotDetail(){ // emits event to main component
    var snapshotId: any = document.getElementById("hiddenSnapshotId");
    snapshotId = snapshotId.value;

    var accountId: any = document.getElementById("hiddenAccountId");
    accountId = accountId.value;

    this.detailEmitter.emit({snapshotId: snapshotId, accountId: accountId});
  }
}