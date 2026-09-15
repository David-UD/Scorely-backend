from django.core.management import call_command

from apps.competitions.models import Affiliation, Competition, Location
from apps.events.models import (
    CompetitionCategory,
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
    assert Event.objects.count() == 11
    assert ScoringRule.objects.count() == 40

    assert Athlete.objects.count() == 20
    assert Team.objects.count() == 4
    assert TeamMember.objects.count() == 12
    assert Competitor.objects.count() == 12
    assert EventCompetitor.objects.count() == 37


def test_seed_data_is_idempotent(db):
    call_command('seed_data')
    call_command('seed_data')

    counts = [
        Affiliation.objects.count(),
        Competition.objects.count(),
        EnabledCompetitionCategory.objects.count(),
        Event.objects.count(),
        ScoringRule.objects.count(),
        Athlete.objects.count(),
        Team.objects.count(),
        TeamMember.objects.count(),
        Competitor.objects.count(),
        EventCompetitor.objects.count(),
    ]
    assert counts == [6, 4, 6, 11, 40, 20, 4, 12, 12, 37]


def test_seed_data_computes_event_ranks_and_scores(db):
    call_command('seed_data')

    scored = EventCompetitor.objects.filter(event_rank__isnull=False, score__isnull=False)
    assert scored.count() == 37
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


def test_seed_data_final_events_only_for_qualified(db):
    from apps.rankings.services.competition_ranking_service import CompetitionRankingService

    call_command('seed_data')

    service = CompetitionRankingService()
    competitions = Competition.objects.filter(
        name__in=['Summer Games CrossFit', 'Open CrossFit Teams'],
    )

    for competition in competitions:
        ranking = service.calculate_competition_ranking(competition, Event.Phase.QUALIFIER)

        slots_by_category = {
            ec.id: ec.finalist_slots
            for ec in EnabledCompetitionCategory.objects.filter(competition=competition)
        }

        qualified_ids = {
            item['competitor'].id
            for enabled_category, items in ranking.items()
            for item in items[:slots_by_category.get(enabled_category.id, 0)]
        }

        final_competitor_ids = set(
            EventCompetitor.objects.filter(
                event__competition=competition,
                event__phase=Event.Phase.FINAL,
            ).values_list('competitor_id', flat=True)
        )

        assert final_competitor_ids
        assert final_competitor_ids <= qualified_ids