from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CompetitionCategoryViewSet,
    EnabledCompetitionCategoryViewSet,
    EventCompetitorViewSet,
    EventViewSet,
)

router = DefaultRouter()
router.register('competition-categories', CompetitionCategoryViewSet)
router.register('enabled-competition-categories', EnabledCompetitionCategoryViewSet)
router.register('events', EventViewSet)
router.register('event-competitors', EventCompetitorViewSet)

urlpatterns = [
    path('', include(router.urls)),
]