from django.urls import path
from .views import snapshot_list, snapshot_detail, account_list, \
    account_create, account_delete, user_create, user_logout, show_score
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('snapshots/list/<int:account_id>/', snapshot_list),
    path('snapshots/detail/<int:id_snapshot>/', snapshot_detail),
    path('snapshots/single/', show_score),
    path('accounts/', account_list),
    path('accounts/add/', account_create),
    path('accounts/delete/<int:id_account>/', account_delete),
    path('users/register/', user_create),
    path('users/login/', obtain_auth_token),
    path('users/logout/', user_logout),
]
