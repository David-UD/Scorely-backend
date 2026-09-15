from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AffiliationViewSet,
    CompetitionTypeViewSet,
    CompetitionViewSet,
    LocationViewSet,
    StatusCompetitionViewSet,
)

router = DefaultRouter()
router.register('competition-types', CompetitionTypeViewSet)
router.register('affiliations', AffiliationViewSet)
router.register('locations', LocationViewSet)
router.register('status-competitions', StatusCompetitionViewSet)
router.register('competitions', CompetitionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
