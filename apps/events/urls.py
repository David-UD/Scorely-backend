from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CompetitionCategoryViewSet,
    CompetitionEnabledCategoryViewSet,
    CompetitionStageViewSet,
    EventCompetitorViewSet,
    EventResultTypeViewSet,
    EventViewSet,
    RankDirectionViewSet,
    StatusEventCompetitorViewSet,
)

router = DefaultRouter()
router.register('competition-categories', CompetitionCategoryViewSet)
router.register('competition-enabled-categories', CompetitionEnabledCategoryViewSet)
router.register('competition-stages', CompetitionStageViewSet)
router.register('event-result-types', EventResultTypeViewSet)
router.register('rank-directions', RankDirectionViewSet)
router.register('events', EventViewSet)
router.register('status-event-competitors', StatusEventCompetitorViewSet)
router.register('event-competitors', EventCompetitorViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
