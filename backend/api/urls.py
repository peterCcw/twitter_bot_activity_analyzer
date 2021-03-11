from django.urls import path, include

from rest_framework.routers import SimpleRouter

from .views import AccountViewSet, AccountSnapshotViewSet, UserViewSet

router = SimpleRouter()
router.register(r'account', AccountViewSet, basename='account')
router.register(r'snapshot', AccountSnapshotViewSet, basename='snapshot')
router.register(r'user', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls'))
]
