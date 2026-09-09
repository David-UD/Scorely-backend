import pytest

from apps.competitions.models import (
    Affiliation,
    Competition,
    CompetitionEdition,
    CompetitionType,
    Location,
)
from apps.events.models import (
    CompetitionCategory,
    CompetitionEnabledCategory,
    CompetitionStage,
    Event,
    EventResultType,
    RankDirection,
    StatusEventCompetitor,
)
from apps.participants.models import Competitor, Person, Team, TeamMember
from apps.scoring.models import ScoringRule
from apps.users.models import Role, User


@pytest.fixture
def role_superadmin(db):
    return Role.objects.create(code='SUPERADMIN', name='Superadmin')


@pytest.fixture
def role_admin(db):
    return Role.objects.create(code='ADMIN', name='Admin')


@pytest.fixture
def user(db, role_admin):
    return User.objects.create_user(
        email='test@scorely.com',
        password='testpass123',
        first_name='Test',
        last_name='User',
        role=role_admin,
    )


@pytest.fixture
def superadmin(db, role_superadmin):
    return User.objects.create_user(
        email='super@scorely.com',
        password='superpass123',
        first_name='Super',
        last_name='Admin',
        role=role_superadmin,
    )


@pytest.fixture
def competition_type(db):
    return CompetitionType.objects.create(code='CROSSFIT', name='CrossFit')


@pytest.fixture
def affiliation(db):
    return Affiliation.objects.create(
        name='Mamba CrossFit Studio',
        city='CDMX',
        state='CDMX',
        country='MX',
    )


@pytest.fixture
def location(db):
    return Location.objects.create(
        name='Centro Deportivo',
        address='Av. Siempreviva 123',
        city='CDMX',
        state='CDMX',
        country='MX',
    )


@pytest.fixture
def competition(db, competition_type, affiliation, location):
    return Competition.objects.create(
        competition_type=competition_type,
        affiliation=affiliation,
        location=location,
        name='TJ Summer Games',
    )


@pytest.fixture
def edition(db, competition):
    return CompetitionEdition.objects.create(
        competition=competition,
        year=2028,
        start_date='2028-07-01',
        end_date='2028-07-03',
        status=CompetitionEdition.Status.PUBLISHED,
    )


@pytest.fixture
def category(db):
    return CompetitionCategory.objects.create(
        name='Individual Male',
        min_members=1,
        max_members=1,
    )


@pytest.fixture
def team_category(db):
    return CompetitionCategory.objects.create(
        name='Team Mixed',
        min_members=2,
        max_members=2,
    )


@pytest.fixture
def enabled_category(db, edition, category):
    return CompetitionEnabledCategory.objects.create(
        competition_edition=edition,
        competition_category=category,
    )


@pytest.fixture
def enabled_team_category(db, edition, team_category):
    return CompetitionEnabledCategory.objects.create(
        competition_edition=edition,
        competition_category=team_category,
    )


@pytest.fixture
def stage_qualifier(db, edition):
    return CompetitionStage.objects.create(
        competition_edition=edition,
        stage_type=CompetitionStage.StageType.QUALIFIER,
        qualification_count=5,
        order=1,
    )


@pytest.fixture
def stage_final(db, edition):
    return CompetitionStage.objects.create(
        competition_edition=edition,
        stage_type=CompetitionStage.StageType.FINAL,
        qualification_count=0,
        order=2,
    )


@pytest.fixture
def event_result_type_time(db):
    return EventResultType.objects.create(code='TIME', name='Time')


@pytest.fixture
def event_result_type_reps(db):
    return EventResultType.objects.create(code='REPS', name='Reps')


@pytest.fixture
def event_result_type_weight(db):
    return EventResultType.objects.create(code='WEIGHT', name='Weight')


@pytest.fixture
def rank_direction_asc(db):
    return RankDirection.objects.create(code='ASC', name='Ascending')


@pytest.fixture
def rank_direction_desc(db):
    return RankDirection.objects.create(code='DESC', name='Descending')


@pytest.fixture
def event(db, stage_qualifier, event_result_type_time, rank_direction_asc):
    return Event.objects.create(
        competition_stage=stage_qualifier,
        event_number=1,
        name='WOD 1',
        event_result_type=event_result_type_time,
        rank_direction=rank_direction_asc,
    )


@pytest.fixture
def status_valid(db):
    return StatusEventCompetitor.objects.create(code='VALID', name='Valid')


@pytest.fixture
def status_pending(db):
    return StatusEventCompetitor.objects.create(code='PENDING', name='Pending')


@pytest.fixture
def status_disqualified(db):
    return StatusEventCompetitor.objects.create(code='DISQUALIFIED', name='Disqualified')


@pytest.fixture
def scoring_rules(db, edition):
    rules_data = [
        (1, 100),
        (2, 94),
        (3, 88),
        (4, 82),
        (5, 76),
    ]
    rules = []
    for position, points in rules_data:
        rules.append(ScoringRule.objects.create(
            competition_edition=edition,
            position=position,
            points=points,
        ))
    return rules


@pytest.fixture
def person(db):
    return Person.objects.create(
        first_name='John',
        last_name='Doe',
        birth_date='1995-05-15',
        gender='M',
    )


@pytest.fixture
def competitor(db, edition, enabled_category, person):
    return Competitor.objects.create(
        competition_edition=edition,
        competitor_type=Competitor.CompetitorType.INDIVIDUAL,
        person=person,
        registration_number='C001',
        competition_enabled_category=enabled_category,
    )


@pytest.fixture
def team(db, edition, enabled_team_category):
    return Team.objects.create(
        competition_edition=edition,
        competition_enabled_category=enabled_team_category,
        name='LOS TD-AH',
    )


@pytest.fixture
def team_member(db, team, person):
    return TeamMember.objects.create(team=team, person=person)


@pytest.fixture
def team_competitor(db, edition, enabled_team_category, team):
    return Competitor.objects.create(
        competition_edition=edition,
        competitor_type=Competitor.CompetitorType.TEAM,
        team=team,
        registration_number='T001',
        competition_enabled_category=enabled_team_category,
    )