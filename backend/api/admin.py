from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Account, AccountSnapshot


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['twitter_id', 'screen_name']


admin.site.register(AccountSnapshot)
admin.site.unregister(Group)
