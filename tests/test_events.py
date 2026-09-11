import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.events.models import CompetitionStage, Event, EventCompetitor


@pytest.mark.django_db
class TestCompetitionCategory:
    def test_create_category(self, category):
        assert category.name == 'Individual Male'
        assert category.min_members == 1
        assert category.max_members == 1


@pytest.mark.django_db
class TestEnabledCompetitionCategory:
    def test_enable_category(self, enabled_category):
        assert enabled_category.competition is not None
        assert enabled_category.competition_category.name == 'Individual Male'

    def test_unique_per_competition(self, competition, category, enabled_category):
        from apps.events.models import EnabledCompetitionCategory

        with pytest.raises(IntegrityError):
            EnabledCompetitionCategory.objects.create(
                competition=competition,
                competition_category=category,
            )


@pytest.mark.django_db
class TestCompetitionStage:
    def test_create_qualifier(self, stage_qualifier):
        assert stage_qualifier.stage_type == CompetitionStage.StageType.QUALIFIER
        assert stage_qualifier.qualification_count == 5

    def test_create_final(self, stage_final):
        assert stage_final.stage_type == CompetitionStage.StageType.FINAL

    def test_only_one_qualifier_per_competition(self, competition, stage_qualifier):
        second = CompetitionStage(
            competition=competition,
            stage_type=CompetitionStage.StageType.QUALIFIER,
            qualification_count=3,
            order=3,
        )
        with pytest.raises(ValidationError):
            second.clean()


@pytest.mark.django_db
class TestEvent:
    def test_create_time_event(self, event):
        assert event.event_number == 1
        assert event.workout == '21-15-9: Thrusters + Pull-ups'
        assert event.is_ascending is True
        assert event.is_active is True
        assert event.competition_stage.stage_type == CompetitionStage.StageType.QUALIFIER

    def test_unique_stage_event_number(self, stage_qualifier, event):
        with pytest.raises(IntegrityError):
            Event.objects.create(
                competition_stage=stage_qualifier,
                event_number=1,
                name='WOD Duplicate',
                workout='Duplicado',
                is_ascending=True,
            )

    def test_next_event_number_allowed(self, stage_qualifier):
        event2 = Event.objects.create(
            competition_stage=stage_qualifier,
            event_number=2,
            name='WOD 2',
            workout='AMRAP 12 min',
            is_ascending=False,
        )
        assert event2.event_number == 2


@pytest.mark.django_db
class TestEventCompetitor:
    def test_create_event_competitor(self, event, competitor):
        ec = EventCompetitor.objects.create(
            competitor=competitor,
            event=event,
            result='04:36',
        )
        assert ec.result == '04:36'
        assert ec.event_rank is None

    def test_unique_competitor_event(self, event, competitor):
        EventCompetitor.objects.create(
            competitor=competitor,
            event=event,
            result='04:36',
        )
        with pytest.raises(IntegrityError):
            EventCompetitor.objects.create(
                competitor=competitor,
                event=event,
                result='05:00',
            )