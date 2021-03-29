# Twitter Bot Analyzer
Twitter Bot Analyzer is application written as a main part of my Bachelor of Engineering thesis with some later upgrades.
### Table of contents
* [Description](#description)
    * [About](#about)
    * [Detailed way of work](#detailed-way-of-work)
    * [Classification model](#classification-model)
    * [Logic and presentation layers](#logic-and-presentation-layers)
* [Technologies](#technologies)
  * [Logic layer](#logic-layer)
  * [Presentation layer](#presentation-layer)  
* [How to play](#how-to-play)
    * [Installation](#installation)
    * [Manual](#manual)
    
    
### Description  
##### About
This application is designed help people with identifying and monitoring social bots on the Twitter. It uses simple machine learning model to calculate
account's likelihood of being a bot which I called ***bot score***. Then the application lets to compare *bot scores* of different accounts on different days.
It also provides information which factors were most important in calculating ***bot score***.
##### Detailed way of work
User after registration is able to check Twitter accounts. After manual account check, user can add account to his list. Then the application will
make snapshots of all of his accounts every day. User will be able to check snapshots, and the bot scores on the main panel chart. It is also 
available to check details of every snapshot and compare it with previous one.
##### Classification model
Application uses **Logistic Regression** with two classes (0 - not bot, 1 - bot) as a classification model which was trained with data from 
[Botometer Bot Repository](https://botometer.osome.iu.edu/bot-repository/). ***Bot score*** means likelihood of belonging to class 1 - bot. 
Classifier is based on Logistic Regression provided by [scikit-learn](https://scikit-learn.org/stable/). Model uses 8 features from 
[Twitter user object](https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/user):
* **Statuses count** - number of account's statuses
* **Followers count** - number of account's followers
* **Friends count** - number of accounts this account is following
* **Favourites count** - number of given likes
* **Listed count** - number of account's lists
* **Default profile** - is the theme of profile was changed
* **Verified** - is account verified
* **Protected** - are account's Tweets hidden

Model has ACC=82% and AUC=80.8%
##### Logic and Presentation layers
Application works as a Web application according to REST architecture.
###### Logic layer
Logic layer is based on [Django](https://www.djangoproject.com/) and uses [Django Rest Framework](https://www.django-rest-framework.org/) to create API 
endpoints. It uses [Tweepy](https://www.tweepy.org/) to communicate with Twitter API.
###### Presentation layer
Presentation layer is based on [Angular](https://angular.io/) using [Angular Material](https://material.angular.io/) and 
[Angular Flex-layout](https://www.npmjs.com/package/@angular/flex-layout). It works for every size of display (smartphone, tablet, desktop).
This part was the least important part of a project, so there are no tests and code quality could be better, probably it will be developed in the future.

### Technologies
#### Logic layer:
* [**Python 3.9.2**](https://www.python.org/)
* [**Django 3.1.7**](https://www.djangoproject.com/)
* [**Django Rest Framework 3.12.2**](https://www.django-rest-framework.org/)
* [**django-cors-headers 3.7.0**](https://pypi.org/project/django-cors-headers/)
* [**scikit-learn 0.24.1**](https://scikit-learn.org/)
* [**NumPy 1.20.1**](https://numpy.org/)
* [**Tweepy 3.10.0**](https://www.tweepy.org/)
  
  (all of them available in backend/requirements.txt)
#### Presentation layer:
* [**Angular CLI 11.0.1**](https://cli.angular.io/)
* [**Angular Material 11.0.3**](https://material.angular.io/)
* [**Angular Flex Layout 11.0.0-beta.33**](https://www.npmjs.com/package/@angular/flex-layout)
* [**ChartJS 2.9.4**](https://www.chartjs.org/)
  
  and other mentioned in frontend/package.json
### How to use
##### Launching up
Firstly, download whole application manually or type 
```commandline
git clone https://github.com/peterCcw/twitter_bot_activity_analyzer
```
###### Backend
You can install packages into your main Python, but the best way is to create virtual environment. To create virtual environment,
move to the project's directory and type
```
python -m venv venv
```
Then, to activate virtual environment, move to venv/scripts and type 
```
activate
```
Now, to install packages, move to backend directory and type
```
pip install -r requirements.txt
```
Packages are installed, so next step is to migrate the database. Type
```
python manage.py migrate
```
Server is ready, you can start it by typing 
```
python manage.py runserver
```
**IMPORTANT**:

You have to create file backend/bot_scorer/twitter_api_keys.py according to manual from comment in backend/bot_scorer/views.py
to get access to Twitter API. If you want to activate cyclical snapshots, you have to set backend/bot_scorer/cron.py to be run every day by our Python
virtual environment. For Windows you can use Task Scheduler.

###### Frontend
A first, download Node.js from [here](https://nodejs.org/en/download/). Then install Angular CLI by typing
```
npm install -g @angular/cli
```
Next, you should install packages by going to the frontend directory and typing
```
npm install
```
Last step is launching Angular server by typing
```
ng serve
```
Now, when both Django and Angular server are working, application is available under localhost:4200


![Full width](/readme_images/scorer_1.png)
![Mobile](/readme_images/scorer_2.png)