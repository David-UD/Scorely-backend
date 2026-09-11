import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.participants.models import Competitor


@pytest.mark.django_db
class TestAthlete:
    def test_create_athlete(self, athlete):
        assert athlete.first_name == 'John'
        assert athlete.last_name == 'Doe'


@pytest.mark.django_db
class TestTeam:
    def test_create_team(self, team):
        assert team.name == 'LOS TD-AH'
        assert str(team) == 'LOS TD-AH'


@pytest.mark.django_db
class TestTeamMember:
    def test_create_team_member(self, team_member):
        assert team_member.team.name == 'LOS TD-AH'
        assert team_member.athlete.first_name == 'John'

    def test_unique_team_athlete(self, team, athlete, team_member):
        from apps.participants.models import TeamMember

        with pytest.raises(IntegrityError):
            TeamMember.objects.create(team=team, athlete=athlete)


@pytest.mark.django_db
class TestCompetitorModel:
    def test_create_individual(self, competitor):
        assert competitor.competitor_type == Competitor.CompetitorType.INDIVIDUAL
        assert competitor.athlete is not None
        assert competitor.team is None

    def test_create_team_competitor(self, team_competitor):
        assert team_competitor.competitor_type == Competitor.CompetitorType.TEAM
        assert team_competitor.team is not None
        assert team_competitor.athlete is None

    def test_clean_requires_athlete_for_individual(self, competition, enabled_category):
        with pytest.raises(ValidationError):
            competitor = Competitor(
                competition=competition,
                competitor_type=Competitor.CompetitorType.INDIVIDUAL,
                enabled_competition_category=enabled_category,
            )
            competitor.clean()

    def test_clean_rejects_athlete_and_team_for_individual(
        self, competition, enabled_category, athlete, team
    ):
        with pytest.raises(ValidationError):
            competitor = Competitor(
                competition=competition,
                competitor_type=Competitor.CompetitorType.INDIVIDUAL,
                athlete=athlete,
                team=team,
                enabled_competition_category=enabled_category,
            )
            competitor.clean()

    def test_clean_requires_team_for_team(self, competition, enabled_team_category):
        with pytest.raises(ValidationError):
            competitor = Competitor(
                competition=competition,
                competitor_type=Competitor.CompetitorType.TEAM,
                enabled_competition_category=enabled_team_category,
            )
            competitor.clean()