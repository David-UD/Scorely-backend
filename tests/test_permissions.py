from rest_framework.test import APIClient

from apps.users.models import CompetitionAdmin

# ── /auth/me/ ────────────────────────────────────────────────────────────────


def test_current_user_returns_superuser_flag(user):
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get('/api/v1/auth/me/')
    assert response.status_code == 200
    assert response.data['email'] == user.email
    assert response.data['is_superuser'] is False


def test_current_user_requires_auth():
    client = APIClient()
    response = client.get('/api/v1/auth/me/')
    assert response.status_code == 401


# ── Competition creation ──────────────────────────────────────────────────────


def test_superuser_can_create_competition(superadmin, competition_type, status_competition, affiliation, location):
    client = APIClient()
    client.force_authenticate(user=superadmin)
    data = {
        'name': 'Super Cup',
        'description': '',
        'competition_type': competition_type.pk,
        'status': status_competition.pk,
        'affiliation': affiliation.pk,
        'location': location.pk,
        'start_date': '2028-08-01',
    }
    response = client.post('/api/v1/competitions/', data)
    assert response.status_code == 201
    assert response.data['name'] == 'Super Cup'


def test_regular_user_cannot_create_competition(user, competition_type, status_competition, affiliation, location):
    client = APIClient()
    client.force_authenticate(user=user)
    data = {
        'name': 'Intruder Cup',
        'description': '',
        'competition_type': competition_type.pk,
        'status': status_competition.pk,
        'affiliation': affiliation.pk,
        'location': location.pk,
        'start_date': '2028-08-01',
    }
    response = client.post('/api/v1/competitions/', data)
    assert response.status_code == 403


# ── Competition scoping and object permissions ───────────────────────────────


def test_regular_user_list_only_returns_assigned_competitions(
    user,
    superadmin,
    competition,
    competition_type,
    status_competition,
    affiliation,
    location,
):
    other = competition.__class__.objects.create(
        name='Other Games',
        competition_type=competition_type,
        status=status_competition,
        affiliation=affiliation,
        location=location,
        start_date='2028-09-01',
        slug='other-games',
    )
    CompetitionAdmin.objects.create(
        user=user,
        competition=competition,
        is_active=True,
        assigned_by=superadmin,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get('/api/v1/competitions/')
    assert response.status_code == 200
    ids = {item['id'] for item in response.data['results']}
    assert competition.id in ids
    assert other.id not in ids


def test_competition_admin_can_update_assigned_competition(
    user,
    superadmin,
    competition,
):
    CompetitionAdmin.objects.create(
        user=user,
        competition=competition,
        is_active=True,
        assigned_by=superadmin,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.patch(f'/api/v1/competitions/{competition.id}/', {'name': 'Renamed Games'})
    assert response.status_code == 200
    competition.refresh_from_db()
    assert competition.name == 'Renamed Games'


def test_regular_user_cannot_update_unassigned_competition(user, competition):
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.patch(f'/api/v1/competitions/{competition.id}/', {'name': 'Hacked'})
    assert response.status_code in (403, 404)


def test_anonymous_can_still_read_competition_detail(competition):
    client = APIClient()
    response = client.get(f'/api/v1/competitions/{competition.id}/')
    assert response.status_code == 200


def test_competition_admin_cannot_delete_assigned_competition(
    user,
    superadmin,
    competition,
):
    CompetitionAdmin.objects.create(
        user=user,
        competition=competition,
        is_active=True,
        assigned_by=superadmin,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.delete(f'/api/v1/competitions/{competition.id}/')
    assert response.status_code == 403


def test_superuser_can_delete_competition(superadmin, competition):
    client = APIClient()
    client.force_authenticate(user=superadmin)
    response = client.delete(f'/api/v1/competitions/{competition.id}/')
    assert response.status_code == 204


# ── CompetitionAdmin assignments ──────────────────────────────────────────────


def test_competition_admin_assignment_requires_superuser(
    user,
    competition,
):
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        '/api/v1/competition-admins/',
        {'user': user.pk, 'competition': competition.pk, 'is_active': True},
    )
    assert response.status_code == 403


def test_regular_user_sees_only_own_memberships(
    user,
    superadmin,
    competition,
):
    CompetitionAdmin.objects.create(
        user=user,
        competition=competition,
        is_active=True,
        assigned_by=superadmin,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get('/api/v1/competition-admins/')
    assert response.status_code == 200
    assert all(item['user'] == user.pk for item in response.data['results'])


def test_superuser_can_assign_competition_admin(
    superadmin,
    user,
    competition,
):
    client = APIClient()
    client.force_authenticate(user=superadmin)
    response = client.post(
        '/api/v1/competition-admins/',
        {'user': user.pk, 'competition': competition.pk, 'is_active': True},
    )
    assert response.status_code == 201


# ── User management ──────────────────────────────────────────────────────────


def test_regular_user_cannot_list_users(user):
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get('/api/v1/users/')
    assert response.status_code == 403


def test_superuser_can_list_users(superadmin):
    client = APIClient()
    client.force_authenticate(user=superadmin)
    response = client.get('/api/v1/users/')
    assert response.status_code == 200
    assert len(response.data['results']) >= 1


# ── Scoping: eventos, equipos ────────────────────────────────────────────────

from apps.competitions.models import Competition
from apps.events.models import Event
from apps.participants.models import Athlete, Team


def _assign(user, superadmin, competition):
    CompetitionAdmin.objects.create(
        user=user,
        competition=competition,
        is_active=True,
        assigned_by=superadmin,
    )


def _other_competition(competition, competition_type, status_competition, affiliation, location):
    return Competition.objects.create(
        name='Other Games',
        competition_type=competition_type,
        status=status_competition,
        affiliation=affiliation,
        location=location,
        start_date='2028-09-01',
        slug='other-games',
    )


def test_admin_sees_only_events_of_assigned_competition(
    user,
    superadmin,
    competition,
    event,
    competition_type,
    status_competition,
    affiliation,
    location,
):
    other = _other_competition(
        competition, competition_type, status_competition, affiliation, location
    )
    Event.objects.create(
        competition=other,
        phase=Event.Phase.QUALIFIER,
        event_number=1,
        name='WOD Forbidden',
        workout='Lift',
    )
    _assign(user, superadmin, competition)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get('/api/v1/events/')
    assert response.status_code == 200
    names = {item['name'] for item in response.data['results']}
    assert 'WOD 1' in names
    assert 'WOD Forbidden' not in names


def test_admin_cannot_create_event_outside_own_competition(
    user,
    superadmin,
    competition,
    event,
    competition_type,
    status_competition,
    affiliation,
    location,
):
    other = _other_competition(
        competition, competition_type, status_competition, affiliation, location
    )
    _assign(user, superadmin, competition)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        '/api/v1/events/',
        {'competition': other.pk, 'event_number': 2, 'name': 'Hack', 'workout': 'x'},
    )
    assert response.status_code == 403


def test_admin_can_create_event_in_own_competition(
    user,
    superadmin,
    competition,
):
    _assign(user, superadmin, competition)
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        '/api/v1/events/',
        {'competition': competition.pk, 'phase': Event.Phase.QUALIFIER, 'event_number': 9, 'name': 'WOD 9', 'workout': 'AMRAP 10'},
    )
    assert response.status_code == 201


def test_admin_sees_all_teams(user, team):
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get('/api/v1/teams/')
    assert response.status_code == 200
    names = {item['name'] for item in response.data['results']}
    assert 'LOS TD-AH' in names


def test_admin_can_create_team(user):
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post('/api/v1/teams/', {'name': 'My Team'})
    assert response.status_code == 201


def test_admin_can_create_athlete(user):
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        '/api/v1/athletes/',
        {'first_name': 'New', 'last_name': 'Athlete', 'birth_date': '1990-01-01', 'gender': 'F'},
    )
    assert response.status_code == 201