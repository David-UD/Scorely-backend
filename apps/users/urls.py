from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CompetitionEditionAdminViewSet, RoleViewSet, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('roles', RoleViewSet)
router.register('edition-admins', CompetitionEditionAdminViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
