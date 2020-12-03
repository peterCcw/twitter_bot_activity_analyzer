from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from .views import snapshot_list, snapshot_detail, account_list, \
    account_create, account_delete, user_create, user_logout
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('snapshots/', snapshot_list),
    path('snapshots/<int:id_snapshot>/', snapshot_detail),
    path('accounts/', account_list),
    path('accounts/add/', account_create),
    path('accounts/delete/<int:id_account>/', account_delete),
    path('users/register/', user_create),
    path('users/login/', obtain_auth_token),
    path('users/logout/', user_logout),
    path('auth/', obtain_auth_token),
]
