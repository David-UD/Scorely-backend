import pytest
from django.db import IntegrityError

from apps.events.models import Event, EventCompetitor


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
class TestEvent:
    def test_create_qualifier(self, event):
        assert event.event_number == 1
        assert event.phase == Event.Phase.QUALIFIER
        assert event.workout == '21-15-9: Thrusters + Pull-ups'
        assert event.is_ascending is True
        assert event.is_active is True
        assert event.competition is not None

    def test_create_final(self, competition):
        event = Event.objects.create(
            competition=competition,
            phase=Event.Phase.FINAL,
            event_number=3,
            name='WOD Final',
            workout='Evento final',
            is_ascending=True,
        )
        assert event.phase == Event.Phase.FINAL

    def test_same_event_number_allowed_across_phases(self, event):
        final_event = Event.objects.create(
            competition=event.competition,
            phase=Event.Phase.FINAL,
            event_number=1,
            name='WOD Final',
            workout='Evento final',
            is_ascending=True,
        )
        assert final_event.event_number == 1
        assert final_event.phase == Event.Phase.FINAL

    def test_unique_event_number_per_competition_and_phase(self, event):
        with pytest.raises(IntegrityError):
            Event.objects.create(
                competition=event.competition,
                phase=Event.Phase.QUALIFIER,
                event_number=1,
                name='WOD Duplicate',
                workout='Duplicado',
                is_ascending=True,
            )

    def test_same_event_number_allowed_in_other_competition(self, event, competition_type,
                                                            status_competition, affiliation,
                                                            location):
        from apps.competitions.models import Competition

        other = Competition.objects.create(
            name='Other Games',
            competition_type=competition_type,
            status=status_competition,
            affiliation=affiliation,
            location=location,
            start_date='2028-09-01',
            slug='other-games',
        )
        event2 = Event.objects.create(
            competition=other,
            phase=Event.Phase.QUALIFIER,
            event_number=1,
            name='WOD 2',
            workout='AMRAP 12 min',
            is_ascending=False,
        )
        assert event2.event_number == 1


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