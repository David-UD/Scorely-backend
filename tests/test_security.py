import pytest
from datetime import timedelta
from types import SimpleNamespace
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.competitions.models import CompetitionEdition
from apps.users.models import CompetitionEditionAdmin, Role, User


@pytest.mark.django_db
class TestJWTAuthentication:
    def test_token_obtain(self, user):
        client = APIClient()
        response = client.post('/api/v1/auth/token/', {
            'email': 'test@scorely.com',
            'password': 'testpass123',
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_token_refresh(self, user):
        client = APIClient()
        refresh = RefreshToken.for_user(user)
        response = client.post('/api/v1/auth/token/refresh/', {
            'refresh': str(refresh),
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_invalid_credentials(self, user):
        client = APIClient()
        response = client.post('/api/v1/auth/token/', {
            'email': 'test@scorely.com',
            'password': 'wrongpassword',
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_expired_token(self, user):
        access = RefreshToken.for_user(user).access_token
        access.set_exp(lifetime=timedelta(seconds=-1))  # expirado
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        response = client.get('/api/v1/users/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestRolePermissions:
    def test_superadmin_full_access(self, superadmin):
        client = APIClient()
        client.force_authenticate(user=superadmin)
        response = client.get('/api/v1/users/')
        assert response.status_code == status.HTTP_200_OK

    def test_admin_access(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/v1/users/')
        assert response.status_code == status.HTTP_200_OK

    def test_edition_admin_assignment(self, user, edition, superadmin):
        relation = CompetitionEditionAdmin.objects.create(
            user=user,
            competition_edition=edition,
        )
        assert relation is not None

    def test_admin_cannot_manage_unassigned_edition(self, user, edition, competition):
        client = APIClient()
        client.force_authenticate(user=user)

        other_edition = CompetitionEdition.objects.create(
            competition=competition,
            year=2029,
            start_date='2029-07-01',
            end_date='2029-07-03',
            status=CompetitionEdition.Status.DRAFT,
        )

        from apps.users.permissions import IsEditionAdmin

        class Dummy:
            competition_edition = other_edition

        permission = IsEditionAdmin()
        request = SimpleNamespace(user=user)
        assert permission.has_object_permission(request, None, Dummy()) is False

    def test_superadmin_can_manage_all_editions(self, superadmin, edition):
        from apps.users.permissions import IsEditionAdmin

        class Dummy:
            competition_edition = edition

        permission = IsEditionAdmin()
        request = SimpleNamespace(user=superadmin)
        assert permission.has_object_permission(request, None, Dummy()) is True


@pytest.mark.django_db
class TestCORSSettings:
    def test_cors_headers_configured(self):
        from django.conf import settings
        assert hasattr(settings, 'CORS_ALLOWED_ORIGINS') or hasattr(settings, 'CORS_ALLOW_ALL_ORIGINS')

    def test_secret_key_not_hardcoded_in_production(self):
        from django.conf import settings
        if not settings.DEBUG:
            assert settings.SECRET_KEY != 'django-insecure-change-me-in-production'