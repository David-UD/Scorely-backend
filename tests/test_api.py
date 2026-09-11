import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestAPIAuth:
    def test_unauthorized_access_returns_401(self):
        client = APIClient()
        response = client.get('/api/v1/users/')
        assert response.status_code == 401

    def test_authorized_access_returns_200(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/v1/users/')
        assert response.status_code == 200

    def test_login_returns_tokens(self, user):
        client = APIClient()
        response = client.post('/api/v1/auth/token/', {
            'email': 'test@scorely.com',
            'password': 'testpass123',
        })
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data


@pytest.mark.django_db
class TestAPIUsers:
    def test_create_user(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/api/v1/users/', {
            'email': 'new@test.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'securepass123',
        })
        assert response.status_code == 201
        assert response.data['email'] == 'new@test.com'


@pytest.mark.django_db
class TestAPICompetitions:
    def test_create_competition(self, superadmin, competition_type, status_competition, affiliation, location):
        client = APIClient()
        client.force_authenticate(user=superadmin)
        data = {
            'name': 'New Comp',
            'competition_type': competition_type.id,
            'status': status_competition.id,
            'affiliation': affiliation.id,
            'location': location.id,
            'description': '',
            'start_date': '2027-07-01',
            'end_date': '2027-07-03',
            'slug': 'new-comp',
        }
        response = client.post('/api/v1/competitions/', data, format='json')
        assert response.status_code in (200, 201)


@pytest.mark.django_db
class TestAPIEventCompetitors:
    def test_list_events(self, user, event):
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/v1/events/')
        assert response.status_code == 200
        assert len(response.data['results']) == 1


@pytest.mark.django_db
class TestAPIRankings:
    def test_qualifier_leaderboard(self, competition):
        client = APIClient()
        response = client.get(f'/api/v1/leaderboards/competition/{competition.id}/qualifier/')
        assert response.status_code in (200, 404)

    def test_final_leaderboard(self, competition):
        client = APIClient()
        response = client.get(f'/api/v1/leaderboards/competition/{competition.id}/final/')
        assert response.status_code in (200, 404)