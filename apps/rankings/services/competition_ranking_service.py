from collections import defaultdict

from apps.events.models import EnabledCompetitionCategory, EventCompetitor
from apps.participants.models import Competitor


class CompetitionRankingService:
    """Calculate Final Score and overall competition ranking."""

    def calculate_competition_ranking(self, competition, stage):
        """
        Calculate the competition ranking for a specific competition and stage.

        Args:
            competition: Competition instance
            stage: CompetitionStage instance

        Returns:
            dict: Ranking data grouped by category
        """
        enabled_categories = EnabledCompetitionCategory.objects.filter(
            competition=competition,
        )

        results = {}

        for enabled_category in enabled_categories:
            competitors = Competitor.objects.filter(
                competition=competition,
                enabled_competition_category=enabled_category,
            )

            competitor_scores = []

            for competitor in competitors:
                event_competitors = EventCompetitor.objects.filter(
                    competitor=competitor,
                    event__competition_stage=stage,
                )

                final_score = sum(ec.score or 0 for ec in event_competitors)
                event_ranks = list(
                    event_competitors.values_list('event_rank', flat=True)
                )
                event_scores = list(
                    event_competitors.values_list('score', flat=True)
                )

                competitor_scores.append({
                    'competitor': competitor,
                    'final_score': final_score,
                    'event_ranks': event_ranks,
                    'event_scores': event_scores,
                })

            ranked = self._rank_competitors(competitor_scores)
            results[enabled_category] = ranked

        return results

    def _rank_competitors(self, competitor_scores):
        """
        Rank competitors with tie-breaking rules:
        1. Higher Final Score
        2. More 1st-place finishes
        3. More 2nd-place finishes
        4. More 3rd-place finishes
        5. Best result in last common event
        6. Maintain tie
        """
        competitor_scores.sort(
            key=lambda x: (
                x['final_score'],
                x['event_ranks'].count(1),
                x['event_ranks'].count(2),
                x['event_ranks'].count(3),
            ),
            reverse=True,
        )

        ranked = []
        current_rank = 1

        i = 0
        while i < len(competitor_scores):
            current = competitor_scores[i]

            if i > 0:
                prev = competitor_scores[i - 1]
                if self._are_tied(prev, current):
                    rank = ranked[-1]['rank']
                else:
                    rank = current_rank
            else:
                rank = current_rank

            ranked.append({
                'competitor': current['competitor'],
                'final_score': current['final_score'],
                'rank': rank,
                'event_ranks': current['event_ranks'],
                'event_scores': current['event_scores'],
            })

            current_rank += 1
            i += 1

        return ranked

    def _are_tied(self, a, b):
        """Check if two competitors are tied."""
        if a['final_score'] != b['final_score']:
            return False

        a_ranks = a['event_ranks']
        b_ranks = b['event_ranks']

        for place in [1, 2, 3]:
            if a_ranks.count(place) != b_ranks.count(place):
                return False

        return True