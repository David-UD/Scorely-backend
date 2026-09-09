import pytest
from django.db import IntegrityError

from apps.scoring.models import ScoringRule
from apps.scoring.services.scoring_service import ScoringService


@pytest.mark.django_db
class TestScoringRule:
    def test_create_rules(self, scoring_rules):
        assert len(scoring_rules) == 5
        assert scoring_rules[0].position == 1
        assert scoring_rules[0].points == 100

    def test_unique_position_per_edition(self, edition, scoring_rules):
        with pytest.raises(IntegrityError):
            ScoringRule.objects.create(
                competition_edition=edition,
                position=1,
                points=50,
            )

    def test_different_edition_can_have_different_table(self, competition, scoring_rules):
        edition2 = __import__(
            'apps.competitions.models', fromlist=['CompetitionEdition']
        ).CompetitionEdition.objects.create(
            competition=competition,
            year=2029,
            start_date='2029-07-01',
            end_date='2029-07-03',
        )
        rule = ScoringRule.objects.create(
            competition_edition=edition2,
            position=1,
            points=99,
        )
        assert rule.points == 99


@pytest.mark.django_db
class TestScoringService:
    def test_get_points_position_1(self, edition, scoring_rules):
        service = ScoringService()
        assert service.get_points(edition, 1) == 100

    def test_get_points_position_2(self, edition, scoring_rules):
        service = ScoringService()
        assert service.get_points(edition, 2) == 94

    def test_get_points_position_3(self, edition, scoring_rules):
        service = ScoringService()
        assert service.get_points(edition, 3) == 88

    def test_get_points_no_rule(self, edition, scoring_rules):
        service = ScoringService()
        assert service.get_points(edition, 50) == 0