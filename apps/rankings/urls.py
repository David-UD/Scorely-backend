from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LeaderboardViewSet

router = DefaultRouter()
router.register('leaderboards', LeaderboardViewSet, basename='leaderboard')

urlpatterns = [
    path('', include(router.urls)),
]