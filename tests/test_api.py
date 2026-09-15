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
        response = client.get('/api/v1/auth/me/')
        assert response.status_code == 200
        assert response.data['email'] == user.email

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
    def test_create_user(self, superadmin):
        client = APIClient()
        client.force_authenticate(user=superadmin)
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
    def test_list_events(self, user, superadmin, event):
        from apps.users.models import CompetitionAdmin

        competition = event.competition
        CompetitionAdmin.objects.create(
            user=user,
            competition=competition,
            is_active=True,
            assigned_by=superadmin,
        )
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

    def test_final_leaderboard_is_global_with_nulls(
        self, user, superadmin, event, competitor, scoring_rules, competition
    ):
        from apps.events.models import Event, EventCompetitor
        from apps.events.services.event_ranking_service import EventRankingService
        from apps.users.models import CompetitionAdmin

        CompetitionAdmin.objects.create(
            user=user,
            competition=competition,
            is_active=True,
            assigned_by=superadmin,
        )

        final_event = Event.objects.create(
            competition=competition,
            phase=Event.Phase.FINAL,
            event_number=2,
            name='WOD Final',
            workout='Finisher',
            is_ascending=True,
        )

        # Competitor only has a record in the qualifier event (did not qualify)
        EventCompetitor.objects.create(competitor=competitor, event=event, result='04:36')
        EventRankingService.calculate_event_ranking(event)
        EventRankingService.calculate_event_ranking(final_event)

        client = APIClient()
        response = client.get(f'/api/v1/leaderboards/competition/{competition.id}/final/')
        assert response.status_code == 200

        entries = response.data[0]['entries']
        assert len(entries) == 1

        entry = entries[0]
        assert len(entry['event_results']) == 2
        qualifier_row = entry['event_results'][0]
        final_row = entry['event_results'][1]

        assert qualifier_row['event_name'] == 'WOD 1'
        assert qualifier_row['result'] == '04:36'

        assert final_row['event_name'] == 'WOD Final'
        assert final_row['result'] is None
        assert final_row['event_rank'] is None
        assert final_row['score'] is None

        assert entry['final_score'] == qualifier_row['score']

    def test_final_leaderboard_computes_global_total(
        self, user, superadmin, event, competitor, scoring_rules, competition
    ):
        from apps.events.models import Event, EventCompetitor
        from apps.events.services.event_ranking_service import EventRankingService
        from apps.users.models import CompetitionAdmin

        CompetitionAdmin.objects.create(
            user=user,
            competition=competition,
            is_active=True,
            assigned_by=superadmin,
        )

        final_event = Event.objects.create(
            competition=competition,
            phase=Event.Phase.FINAL,
            event_number=2,
            name='WOD Final',
            workout='Finisher',
            is_ascending=True,
        )

        for ec_event in (event, final_event):
            EventCompetitor.objects.create(competitor=competitor, event=ec_event, result='04:36')

        for ec_event in (event, final_event):
            EventRankingService.calculate_event_ranking(ec_event)

        client = APIClient()
        response = client.get(f'/api/v1/leaderboards/competition/{competition.id}/final/')
        assert response.status_code == 200

        entry = response.data[0]['entries'][0]
        assert len(entry['event_results']) == 2
        assert entry['final_score'] == 200  # 100 qualifier + 100 final

    def test_leaderboard_includes_event_results(
        self, user, superadmin, event, competitor, scoring_rules, competition
    ):
        from apps.events.models import EventCompetitor
        from apps.events.services.event_ranking_service import EventRankingService
        from apps.users.models import CompetitionAdmin

        CompetitionAdmin.objects.create(
            user=user,
            competition=competition,
            is_active=True,
            assigned_by=superadmin,
        )
        EventCompetitor.objects.create(competitor=competitor, event=event, result='04:36')
        EventRankingService.calculate_event_ranking(event)

        second_event = event.__class__.objects.create(
            competition=competition,
            phase=event.phase,
            event_number=2,
            name='WOD 2',
            workout='AMRAP',
            is_ascending=False,
        )
        EventCompetitor.objects.create(competitor=competitor, event=second_event, result='150')
        EventRankingService.calculate_event_ranking(second_event)

        client = APIClient()
        response = client.get(f'/api/v1/leaderboards/competition/{competition.id}/qualifier/')
        assert response.status_code == 200

        assert isinstance(response.data, list)
        entries = response.data[0]['entries']
        assert len(entries) == 1

        entry = entries[0]
        assert 'event_results' in entry
        assert len(entry['event_results']) == 2

        first = entry['event_results'][0]
        assert set(first.keys()) == {
            'event_id', 'event_number', 'event_name', 'phase',
            'result', 'event_rank', 'score',
        }
        assert first['event_name'] == 'WOD 1'
        assert first['result'] == '04:36'
        assert first['event_rank'] == 1
        assert first['score'] == 100

        assert sum(row['score'] for row in entry['event_results']) == entry['final_score']


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

    def test_status_competitions_list_requires_auth(self):
        client = APIClient()
        response = client.get('/api/v1/status-competitions/')
        assert response.status_code == 401

    def test_status_competitions_list_authenticated(self, superadmin, status_competition):
        client = APIClient()
        client.force_authenticate(user=superadmin)
        response = client.get('/api/v1/status-competitions/')
        assert response.status_code == 200
        assert len(response.data['results']) >= 1

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

    # ── events ────────────────────────────────────────────────────────

    def test_event_list_public(self, event):
        client = APIClient()
        response = client.get(
            f'/api/v1/events/?competition={event.competition.id}&phase={event.phase}'
        )
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_event_create_requires_auth(self, competition):
        client = APIClient()
        data = {
            'competition': competition.id,
            'phase': 'QUALIFIER',
            'event_number': 99,
            'name': 'WOD Intruder',
            'workout': 'Proto de intruso',
            'is_ascending': True,
        }
        response = client.post('/api/v1/events/', data, format='json')
        assert response.status_code == 401

    # ── regression with authentication ────────────────────────────────

    def test_public_reads_work_with_superadmin(self, superadmin, competition, event):
        client = APIClient()
        client.force_authenticate(user=superadmin)
        assert client.get('/api/v1/competitions/').status_code == 200
        assert client.get(
            f'/api/v1/events/?competition={competition.id}').status_code == 200

    # ── leaderboard still public ──────────────────────────────────────

    def test_leaderboard_still_public(self, competition):
        client = APIClient()
        response = client.get(
            f'/api/v1/leaderboards/competition/{competition.id}/qualifier/'
        )
        assert response.status_code in (200, 404)