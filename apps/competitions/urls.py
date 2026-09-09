from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AffiliationViewSet,
    CompetitionEditionViewSet,
    CompetitionTypeViewSet,
    CompetitionViewSet,
    LocationViewSet,
)

router = DefaultRouter()
router.register('competition-types', CompetitionTypeViewSet)
router.register('affiliations', AffiliationViewSet)
router.register('locations', LocationViewSet)
router.register('competitions', CompetitionViewSet)
router.register('competition-editions', CompetitionEditionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
