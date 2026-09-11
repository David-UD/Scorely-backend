import pytest
from django.db import IntegrityError

from apps.users.models import CompetitionAdmin, User
from apps.users.serializers import UserCreateSerializer


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
        assert user.is_active is True

    def test_create_superuser_requires_staff(self):
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                email='root2@test.com',
                password='rootpass123',
                first_name='Root',
                last_name='Admin',
                is_staff=False,
            )

    def test_full_name(self):
        user = User.objects.create_user(
            email='name@test.com',
            password='password123',
            first_name='Ana',
            last_name='Lopez',
        )
        assert user.full_name == 'Ana Lopez'


@pytest.mark.django_db
class TestCompetitionAdminModel:
    def test_create(self, user, competition):
        relation = CompetitionAdmin.objects.create(
            user=user,
            competition=competition,
        )
        assert relation.user == user
        assert relation.competition == competition

    def test_unique_together(self, user, competition):
        CompetitionAdmin.objects.create(user=user, competition=competition)
        with pytest.raises(IntegrityError):
            CompetitionAdmin.objects.create(user=user, competition=competition)


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