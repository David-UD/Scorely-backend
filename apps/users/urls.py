from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CompetitionAdminViewSet, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('competition-admins', CompetitionAdminViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
