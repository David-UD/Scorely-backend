from apps.events.models import EnabledCompetitionCategory, Event
from apps.rankings.services.competition_ranking_service import CompetitionRankingService


class FinalQualificationService:
    """Determine qualifiers from Qualifier to Final."""

    def __init__(self):
        self.ranking_service = CompetitionRankingService()

    def get_qualifiers(self, competition):
        """
        Get qualifiers from the Qualifier phase for all categories.

        Args:
            competition: Competition instance

        Returns:
            dict: Qualifiers grouped by category
        """
        enabled_categories = EnabledCompetitionCategory.objects.filter(
            competition=competition,
            finalist_slots__gt=0,
        )
        if not enabled_categories.exists():
            return {}

        ranking = self.ranking_service.calculate_competition_ranking(
            competition, Event.Phase.QUALIFIER,
        )

        qualifiers = {}

        for enabled_category in enabled_categories:
            ranked_competitors = ranking.get(enabled_category, [])
            qualifiers[enabled_category] = [
                item['competitor']
                for item in ranked_competitors[:enabled_category.finalist_slots]
            ]

        return qualifiers