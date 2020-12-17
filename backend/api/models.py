from django.contrib.auth.models import User
from django.db import models


class Account(models.Model):
    twitter_id = models.PositiveIntegerField(unique=True)
    screen_name = models.CharField(max_length=128)
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.screen_name


class AccountSnapshot(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    name = models.CharField(max_length=256)
    location = models.CharField(max_length=256, blank=True)
    url = models.URLField(blank=True)
    description = models.CharField(max_length=512, blank=True)
    created_at = models.DateTimeField()
    statuses_count = models.PositiveIntegerField()
    followers_count = models.PositiveIntegerField()
    friends_count = models.PositiveIntegerField()
    favourites_count = models.PositiveIntegerField()
    listed_count = models.PositiveIntegerField()
    default_profile = models.BooleanField()
    verified = models.BooleanField()
    protected = models.BooleanField()
    bot_score = models.FloatField()
    is_active = models.BooleanField()
    date_of_snapshot = models.DateTimeField(auto_now=True)
    suspended_info = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return f"{self.account.screen_name} " \
               f"{self.date_of_snapshot.strftime('%d-%m-%Y %H:%M')}"
