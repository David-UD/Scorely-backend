from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CompetitorViewSet, PersonViewSet, TeamMemberViewSet, TeamViewSet

router = DefaultRouter()
router.register('persons', PersonViewSet)
router.register('teams', TeamViewSet)
router.register('team-members', TeamMemberViewSet)
router.register('competitors', CompetitorViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
