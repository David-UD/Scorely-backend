import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.participants.models import Competitor


@pytest.mark.django_db
class TestPerson:
    def test_create_person(self, person):
        assert person.first_name == 'John'
        assert person.last_name == 'Doe'


@pytest.mark.django_db
class TestTeam:
    def test_create_team(self, team):
        assert team.name == 'LOS TD-AH'
        assert str(team) == 'LOS TD-AH'


@pytest.mark.django_db
class TestTeamMember:
    def test_create_team_member(self, team_member):
        assert team_member.team.name == 'LOS TD-AH'
        assert team_member.person.first_name == 'John'

    def test_unique_team_person(self, team, person, team_member):
        from apps.participants.models import TeamMember

        with pytest.raises(IntegrityError):
            TeamMember.objects.create(team=team, person=person)


@pytest.mark.django_db
class TestCompetitorModel:
    def test_create_individual(self, competitor):
        assert competitor.competitor_type == Competitor.CompetitorType.INDIVIDUAL
        assert competitor.person is not None
        assert competitor.team is None

    def test_create_team_competitor(self, team_competitor):
        assert team_competitor.competitor_type == Competitor.CompetitorType.TEAM
        assert team_competitor.team is not None
        assert team_competitor.person is None

    def test_clean_requires_person_for_individual(self, edition, enabled_category):
        with pytest.raises(ValidationError):
            competitor = Competitor(
                competition_edition=edition,
                competitor_type=Competitor.CompetitorType.INDIVIDUAL,
                competition_enabled_category=enabled_category,
            )
            competitor.clean()

    def test_clean_rejects_person_and_team_for_individual(self, edition, enabled_category, person, team):
        with pytest.raises(ValidationError):
            competitor = Competitor(
                competition_edition=edition,
                competitor_type=Competitor.CompetitorType.INDIVIDUAL,
                person=person,
                team=team,
                competition_enabled_category=enabled_category,
            )
            competitor.clean()

    def test_clean_requires_team_for_team(self, edition, enabled_team_category):
        with pytest.raises(ValidationError):
            competitor = Competitor(
                competition_edition=edition,
                competitor_type=Competitor.CompetitorType.TEAM,
                competition_enabled_category=enabled_team_category,
            )
            competitor.clean()