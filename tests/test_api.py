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


@pytest.mark.django_db
class TestAPIPublicReadOnly:

    # ── competitions ──────────────────────────────────────────────────

    def test_competition_list_public(self, competition):
        client = APIClient()
        response = client.get('/api/v1/competitions/')
        assert response.status_code == 200
        assert len(response.data['results']) >= 1

    def test_competition_detail_public(self, competition):
        client = APIClient()
        response = client.get(f'/api/v1/competitions/{competition.id}/')
        assert response.status_code == 200
        assert response.data['competition_type']['code'] == 'CROSSFIT'
        assert 'status' in response.data
        assert 'affiliation' in response.data
        assert 'location' in response.data

    def test_competition_detail_public_by_slug(self, competition):
        client = APIClient()
        response = client.get(f'/api/v1/competitions/{competition.slug}/')
        assert response.status_code == 200
        assert response.data['id'] == competition.id
        assert response.data['slug'] == competition.slug

    def test_competition_detail_unknown_slug_returns_404(self):
        client = APIClient()
        response = client.get('/api/v1/competitions/does-not-exist/')
        assert response.status_code == 404

    def test_competition_create_requires_auth(self, competition_type, status_competition, affiliation, location):
        client = APIClient()
        data = {
            'name': 'Public Intruder',
            'competition_type': competition_type.id,
            'status': status_competition.id,
            'affiliation': affiliation.id,
            'location': location.id,
            'description': '',
            'start_date': '2027-07-01',
            'end_date': '2027-07-03',
            'slug': 'public-intruder',
        }
        response = client.post('/api/v1/competitions/', data, format='json')
        assert response.status_code == 401

    def test_competition_destroy_requires_auth(self, competition):
        client = APIClient()
        response = client.delete(f'/api/v1/competitions/{competition.id}/')
        assert response.status_code == 401

    def test_competition_filter_public(self, competition):
        client = APIClient()
        response = client.get(f'/api/v1/competitions/?status={competition.status.id}')
        assert response.status_code == 200

    # ── competition-stages ────────────────────────────────────────────

    def test_stage_list_public(self, stage_qualifier):
        client = APIClient()
        response = client.get(
            f'/api/v1/competition-stages/?competition={stage_qualifier.competition.id}'
        )
        assert response.status_code == 200
        assert len(response.data['results']) >= 1

    def test_stage_create_requires_auth(self, competition):
        client = APIClient()
        data = {
            'competition': competition.id,
            'stage_type': 'QUALIFIER',
            'qualification_count': 5,
            'order': 1,
        }
        response = client.post('/api/v1/competition-stages/', data, format='json')
        assert response.status_code == 401

    # ── events ────────────────────────────────────────────────────────

    def test_event_list_public(self, event):
        client = APIClient()
        response = client.get(
            f'/api/v1/events/?competition_stage={event.competition_stage.id}'
        )
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_event_create_requires_auth(self, stage_qualifier):
        client = APIClient()
        data = {
            'competition_stage': stage_qualifier.id,
            'event_number': 99,
            'name': 'WOD Intruder',
            'workout': 'Proto de intruso',
            'is_ascending': True,
        }
        response = client.post('/api/v1/events/', data, format='json')
        assert response.status_code == 401

    # ── regression with authentication ────────────────────────────────

    def test_public_reads_work_with_superadmin(self, superadmin, competition,
                                               stage_qualifier, event):
        client = APIClient()
        client.force_authenticate(user=superadmin)
        assert client.get('/api/v1/competitions/').status_code == 200
        assert client.get(
            f'/api/v1/competition-stages/?competition={competition.id}').status_code == 200
        assert client.get(
            f'/api/v1/events/?competition_stage={stage_qualifier.id}').status_code == 200

    # ── leaderboard still public ──────────────────────────────────────

    def test_leaderboard_still_public(self, competition):
        client = APIClient()
        response = client.get(
            f'/api/v1/leaderboards/competition/{competition.id}/qualifier/'
        )
        assert response.status_code in (200, 404)