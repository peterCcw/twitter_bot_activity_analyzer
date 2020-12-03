from django.contrib.auth.models import User
from django.db import models


class Account(models.Model):
    twitter_id = models.PositiveIntegerField(unique=True)
    screen_name = models.CharField(max_length=16)
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.screen_name


class AccountSnapshot(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)


# class AccountList(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     accounts = models.ManyToManyField(Account)

