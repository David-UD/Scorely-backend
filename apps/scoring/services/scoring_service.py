from apps.scoring.models import ScoringRule


class ScoringService:
    """Convert position to points using ScoringRule."""

    def get_points(self, edition, position):
        """
        Get points for a given position in an edition.

        Args:
            edition: CompetitionEdition instance
            position: Integer position (1-based)

        Returns:
            int: Points for the position, 0 if no rule exists
        """
        try:
            rule = ScoringRule.objects.get(
                competition_edition=edition,
                position=position,
            )
            return rule.points
        except ScoringRule.DoesNotExist:
            return 0
