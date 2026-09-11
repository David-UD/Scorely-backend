import pytest
from django.core.exceptions import ValidationError

from apps.competitions.models import Competition, StatusCompetition


@pytest.mark.django_db
class TestCompetitionModels:
    def test_create_competition_type(self, competition_type):
        assert competition_type.code == 'CROSSFIT'
        assert str(competition_type) == 'CrossFit'

    def test_create_affiliation(self, affiliation):
        assert affiliation.name == 'Mamba CrossFit Studio'
        assert str(affiliation) == 'Mamba CrossFit Studio'

    def test_create_location(self, location):
        assert location.name == 'Centro Deportivo'
        assert str(location) == 'Centro Deportivo'

    def test_create_competition(self, competition):
        assert competition.name == 'TJ Summer Games'
        assert competition.competition_type.code == 'CROSSFIT'
        assert str(competition) == 'TJ Summer Games'

    def test_year_derived_from_start_date(self, competition):
        assert competition.year == 2028


@pytest.mark.django_db
class TestCompetitionConstraints:
    def test_unique_slug(self, competition, status_competition, competition_type, affiliation, location):
        with pytest.raises(ValidationError):
            Competition.objects.create(
                name='Another Summer Games',
                competition_type=competition_type,
                status=status_competition,
                affiliation=affiliation,
                location=location,
                start_date='2028-07-01',
                end_date='2028-07-03',
                slug='tj-summer-games',
            )

    def test_end_date_before_start_date_raises(
        self, status_competition, competition_type, affiliation, location
    ):
        with pytest.raises(ValidationError):
            Competition.objects.create(
                name='Bad Dates Comp',
                competition_type=competition_type,
                status=status_competition,
                affiliation=affiliation,
                location=location,
                start_date='2028-07-03',
                end_date='2028-07-01',
                slug='bad-dates-comp',
            )

    def test_different_slug_allowed(
        self, status_competition, competition_type, affiliation, location
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
        assert competition2.year == 2029