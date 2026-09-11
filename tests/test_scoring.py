import pytest
from django.db import IntegrityError

from apps.competitions.models import Competition
from apps.scoring.models import ScoringRule
from apps.scoring.services.scoring_service import ScoringService


@pytest.mark.django_db
class TestScoringRule:
    def test_create_rules(self, scoring_rules):
        assert len(scoring_rules) == 5
        assert scoring_rules[0].position == 1
        assert scoring_rules[0].points == 100

    def test_unique_position_per_competition(self, competition, scoring_rules):
        with pytest.raises(IntegrityError):
            ScoringRule.objects.create(
                competition=competition,
                position=1,
                points=50,
            )

    def test_different_competition_can_have_different_table(
        self, status_competition, competition_type, affiliation, location, scoring_rules
    ):
        competition2 = Competition.objects.create(
            name='TJ Winter Games',
            competition_type=competition_type,
            status=status_competition,
            affiliation=affiliation,
            location=location,
            start_date='2029-01-15',
            end_date='2029-01-17',
            slug='tj-winter-games',
        )
        rule = ScoringRule.objects.create(
            competition=competition2,
            position=1,
            points=99,
        )
        assert rule.points == 99


@pytest.mark.django_db
class TestScoringService:
    def test_get_points_position_1(self, competition, scoring_rules):
        service = ScoringService()
        assert service.get_points(competition, 1) == 100

    def test_get_points_position_2(self, competition, scoring_rules):
        service = ScoringService()
        assert service.get_points(competition, 2) == 94

    def test_get_points_position_3(self, competition, scoring_rules):
        service = ScoringService()
        assert service.get_points(competition, 3) == 88

    def test_get_points_no_rule(self, competition, scoring_rules):
        service = ScoringService()
        assert service.get_points(competition, 50) == 0