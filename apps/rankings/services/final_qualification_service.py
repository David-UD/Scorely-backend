from apps.events.models import CompetitionStage
from apps.rankings.services.competition_ranking_service import CompetitionRankingService


class FinalQualificationService:
    """Determine qualifiers from Qualifier to Final."""

    def __init__(self):
        self.ranking_service = CompetitionRankingService()

    def get_qualifiers(self, edition):
        """
        Get qualifiers from the Qualifier stage for all categories.

        Args:
            edition: CompetitionEdition instance

        Returns:
            dict: Qualifiers grouped by category
        """
        try:
            qualifier_stage = CompetitionStage.objects.get(
                competition_edition=edition,
                stage_type=CompetitionStage.StageType.QUALIFIER,
            )
        except CompetitionStage.DoesNotExist:
            return {}

        ranking = self.ranking_service.calculate_competition_ranking(
            edition, qualifier_stage,
        )

        qualifiers = {}

        for enabled_category, ranked_competitors in ranking.items():
            qualification_count = qualifier_stage.qualification_count
            qualifiers[enabled_category] = [
                item['competitor']
                for item in ranked_competitors[:qualification_count]
            ]

        return qualifiers
