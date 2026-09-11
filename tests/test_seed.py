from django.core.management import call_command

from apps.competitions.models import Affiliation, Competition, Location
from apps.events.models import (
    CompetitionCategory,
    CompetitionStage,
    EnabledCompetitionCategory,
    Event,
    EventCompetitor,
)
from apps.participants.models import Athlete, Competitor, Team, TeamMember
from apps.scoring.models import ScoringRule


def test_seed_data_creates_demo_data(db):
    call_command('seed_data')

    assert Affiliation.objects.count() == 6
    assert Location.objects.count() == 4
    assert Competition.objects.count() == 4
    assert EnabledCompetitionCategory.objects.count() == 6
    assert CompetitionStage.objects.count() == 6
    assert Event.objects.count() == 11
    assert ScoringRule.objects.count() == 40

    assert Athlete.objects.count() == 19
    assert Team.objects.count() == 4
    assert TeamMember.objects.count() == 12
    assert Competitor.objects.count() == 11
    assert EventCompetitor.objects.count() == 34


def test_seed_data_is_idempotent(db):
    call_command('seed_data')
    call_command('seed_data')

    counts = [
        Affiliation.objects.count(),
        Competition.objects.count(),
        EnabledCompetitionCategory.objects.count(),
        CompetitionStage.objects.count(),
        Event.objects.count(),
        ScoringRule.objects.count(),
        Athlete.objects.count(),
        Team.objects.count(),
        TeamMember.objects.count(),
        Competitor.objects.count(),
        EventCompetitor.objects.count(),
    ]
    assert counts == [6, 4, 6, 6, 11, 40, 19, 4, 12, 11, 34]


def test_seed_data_computes_event_ranks_and_scores(db):
    call_command('seed_data')

    scored = EventCompetitor.objects.filter(event_rank__isnull=False, score__isnull=False)
    assert scored.count() == 34
    assert EventCompetitor.objects.filter(event_rank__isnull=True).count() == 0
    assert EventCompetitor.objects.filter(score__isnull=True).count() == 0
    assert EventCompetitor.objects.filter(score=100).exists()


def test_seed_data_creates_categories(db):
    call_command('seed_data')

    names = CompetitionCategory.objects.values_list('name', flat=True)
    for expected in [
        'Principiantes Individual',
        'Intermedios Individual',
        'RX Individual',
        'Principiantes Mixto',
        'Intermedios Duo',
        'Relevos 4',
    ]:
        assert expected in names

    relevos = CompetitionCategory.objects.get(name='Relevos 4')
    assert relevos.min_members == 4
    assert relevos.max_members == 4