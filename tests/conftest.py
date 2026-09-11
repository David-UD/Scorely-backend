import pytest

from apps.competitions.models import (
    Affiliation,
    Competition,
    CompetitionType,
    Location,
    StatusCompetition,
)
from apps.events.models import (
    CompetitionCategory,
    CompetitionStage,
    EnabledCompetitionCategory,
    Event,
    EventResultType,
    RankDirection,
    StatusEventCompetitor,
)
from apps.participants.models import Athlete, Competitor, Team, TeamMember
from apps.scoring.models import ScoringRule
from apps.users.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='test@scorely.com',
        password='testpass123',
        first_name='Test',
        last_name='User',
    )


@pytest.fixture
def superadmin(db):
    return User.objects.create_user(
        email='super@scorely.com',
        password='superpass123',
        first_name='Super',
        last_name='Admin',
        is_active=True,
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def competition_type(db):
    return CompetitionType.objects.create(code='CROSSFIT', name='CrossFit')


@pytest.fixture
def status_competition(db):
    return StatusCompetition.objects.create(code='PUBLISHED', name='Published')


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
def competition(db, competition_type, status_competition, affiliation, location):
    return Competition.objects.create(
        competition_type=competition_type,
        status=status_competition,
        affiliation=affiliation,
        location=location,
        name='TJ Summer Games',
        start_date='2028-07-01',
        end_date='2028-07-03',
        slug='tj-summer-games',
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
def enabled_category(db, competition, category):
    return EnabledCompetitionCategory.objects.create(
        competition=competition,
        competition_category=category,
    )


@pytest.fixture
def enabled_team_category(db, competition, team_category):
    return EnabledCompetitionCategory.objects.create(
        competition=competition,
        competition_category=team_category,
    )


@pytest.fixture
def stage_qualifier(db, competition):
    return CompetitionStage.objects.create(
        competition=competition,
        stage_type=CompetitionStage.StageType.QUALIFIER,
        qualification_count=5,
        order=1,
    )


@pytest.fixture
def stage_final(db, competition):
    return CompetitionStage.objects.create(
        competition=competition,
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
def scoring_rules(db, competition):
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
            competition=competition,
            position=position,
            points=points,
        ))
    return rules


@pytest.fixture
def athlete(db):
    return Athlete.objects.create(
        first_name='John',
        last_name='Doe',
        birth_date='1995-05-15',
        gender='M',
    )


@pytest.fixture
def competitor(db, competition, enabled_category, athlete):
    return Competitor.objects.create(
        competition=competition,
        competitor_type=Competitor.CompetitorType.INDIVIDUAL,
        athlete=athlete,
        registration_number='C001',
        enabled_competition_category=enabled_category,
    )


@pytest.fixture
def team(db, competition):
    return Team.objects.create(
        competition=competition,
        name='LOS TD-AH',
    )


@pytest.fixture
def team_member(db, team, athlete):
    return TeamMember.objects.create(team=team, athlete=athlete)


@pytest.fixture
def team_competitor(db, competition, enabled_team_category, team):
    return Competitor.objects.create(
        competition=competition,
        competitor_type=Competitor.CompetitorType.TEAM,
        team=team,
        registration_number='T001',
        enabled_competition_category=enabled_team_category,
    )