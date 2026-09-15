from apps.events.models import EventCompetitor
from apps.events.services.result_parser import ResultParser
from apps.scoring.services.scoring_service import ScoringService


class EventRankingService:
    """Calculate event rankings with sports ranking (dense ranking)."""

    @staticmethod
    def calculate_event_ranking(event):
        """
        Calculate rankings for all competitors in an event.

        Args:
            event: The Event instance

        Returns:
            list: Updated EventCompetitor instances with ranks and scores
        """
        competitors = EventCompetitor.objects.filter(
            event=event,
        )

        if not competitors.exists():
            return []

        parsed_results = []
        for ec in competitors:
            parsed_value = ResultParser.parse(ec.result)
            parsed_results.append({
                'event_competitor': ec,
                'parsed_value': parsed_value,
            })

        reverse_sort = not event.is_ascending
        parsed_results.sort(key=lambda x: x['parsed_value'], reverse=reverse_sort)

        ranked = EventRankingService._apply_dense_ranking(parsed_results)

        competition = event.competition
        scoring_service = ScoringService()

        for item in ranked:
            ec = item['event_competitor']
            ec.event_rank = item['rank']
            ec.score = scoring_service.get_points(competition, item['rank'])
            ec.save()

        return ranked

    @staticmethod
    def _apply_dense_ranking(sorted_results):
        """
        Apply sports/dense ranking to sorted results.

        Rules:
        - Ties share the same position
        - Next position skips the tied count (1, 2, 2, 4)
        """
        if not sorted_results:
            return []

        ranked = []
        current_rank = 1

        i = 0
        while i < len(sorted_results):
            current_value = sorted_results[i]['parsed_value']
            group = [sorted_results[i]]

            j = i + 1
            while j < len(sorted_results) and sorted_results[j]['parsed_value'] == current_value:
                group.append(sorted_results[j])
                j += 1

            for item in group:
                ranked.append({
                    'event_competitor': item['event_competitor'],
                    'parsed_value': item['parsed_value'],
                    'rank': current_rank,
                })

            current_rank += len(group)
            i = j

        return ranked
