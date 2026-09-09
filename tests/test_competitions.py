import pytest
from django.db import IntegrityError

from apps.competitions.models import CompetitionEdition


@pytest.mark.django_db
class TestCompetitionModels:
    def test_create_competition_type(self, competition_type):
        assert competition_type.code == 'CROSSFIT'
        assert str(competition_type) == 'CROSSFIT'

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

    def test_create_edition(self, edition):
        assert edition.year == 2028
        assert edition.status == CompetitionEdition.Status.PUBLISHED
        assert str(edition) == 'TJ Summer Games 2028'


@pytest.mark.django_db
class TestCompetitionEditionConstraints:
    def test_unique_competition_year(self, competition, edition):
        with pytest.raises(IntegrityError):
            CompetitionEdition.objects.create(
                competition=competition,
                year=2028,
                start_date='2028-07-01',
                end_date='2028-07-03',
            )

    def test_different_year_allowed(self, competition):
        edition2 = CompetitionEdition.objects.create(
            competition=competition,
            year=2029,
            start_date='2029-07-01',
            end_date='2029-07-03',
        )
        assert edition2.year == 2029

    def test_status_transition(self, edition):
        edition.status = CompetitionEdition.Status.FINISHED
        edition.save()
        edition.refresh_from_db()
        assert edition.status == CompetitionEdition.Status.FINISHED