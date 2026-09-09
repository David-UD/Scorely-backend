import pytest
from django.db import IntegrityError

from apps.users.models import CompetitionEditionAdmin, User
from apps.users.serializers import UserCreateSerializer
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            email='user@test.com',
            password='password123',
            first_name='Ana',
            last_name='Lopez',
        )
        assert user.email == 'user@test.com'
        assert user.check_password('password123')
        assert user.is_active is True
        assert user.is_staff is False

    def test_email_unique(self, user):
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email='test@scorely.com',
                password='otherpass123',
                first_name='Other',
                last_name='User',
            )

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email='root@test.com',
            password='rootpass123',
            first_name='Root',
            last_name='Admin',
        )
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_create_superuser_requires_staff(self):
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                email='root2@test.com',
                password='rootpass123',
                first_name='Root',
                last_name='Admin',
                is_staff=False,
            )

    def test_role_assignment(self, role_admin):
        user = User.objects.create_user(
            email='withrole@test.com',
            password='password123',
            first_name='Ana',
            last_name='Lopez',
            role=role_admin,
        )
        assert user.role == role_admin
        assert user.role.code == 'ADMIN'


@pytest.mark.django_db
class TestCompetitionEditionAdminModel:
    def test_create(self, user, edition):
        relation = CompetitionEditionAdmin.objects.create(
            user=user,
            competition_edition=edition,
        )
        assert relation.user == user
        assert relation.competition_edition == edition

    def test_unique_together(self, user, edition):
        CompetitionEditionAdmin.objects.create(user=user, competition_edition=edition)
        with pytest.raises(IntegrityError):
            CompetitionEditionAdmin.objects.create(user=user, competition_edition=edition)


@pytest.mark.django_db
class TestUserCreateSerializer:
    def test_password_not_serialized_out(self):
        data = {
            'email': 'new@test.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'securepass123',
        }
        serializer = UserCreateSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.email == 'new@test.com'
        assert 'password' not in serializer.data