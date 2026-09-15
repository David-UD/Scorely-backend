from collections import defaultdict

from apps.events.models import EnabledCompetitionCategory, Event, EventCompetitor
from apps.participants.models import Competitor


class CompetitionRankingService:
    """Calculate Final Score and overall competition ranking."""

    def calculate_competition_ranking(self, competition, phase):
        """
        Calculate the competition ranking for a specific phase.

        Args:
            competition: Competition instance
            phase: Event.Phase value (QUALIFIER or FINAL)

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
                event_competitors = list(
                    EventCompetitor.objects.filter(
                        competitor=competitor,
                        event__competition=competition,
                        event__phase=phase,
                    )
                    .select_related('event')
                    .order_by('event__event_number')
                )

                final_score = sum(ec.score or 0 for ec in event_competitors)
                event_ranks = [ec.event_rank for ec in event_competitors]
                event_scores = [ec.score for ec in event_competitors]
                event_results = [
                    {
                        'event_id': ec.event_id,
                        'event_number': ec.event.event_number,
                        'event_name': ec.event.name,
                        'phase': ec.event.phase,
                        'result': ec.result,
                        'event_rank': ec.event_rank,
                        'score': ec.score,
                    }
                    for ec in event_competitors
                ]

                competitor_scores.append({
                    'competitor': competitor,
                    'final_score': final_score,
                    'event_ranks': event_ranks,
                    'event_scores': event_scores,
                    'event_results': event_results,
                })

            ranked = self._rank_competitors(competitor_scores)
            results[enabled_category] = ranked

        return results

    def calculate_overall_ranking(self, competition):
        """
        Calculate overall competition ranking across all phases.

        Includes ALL events and ALL competitors. Competitors without a
        record in a given event get null for result/event_rank/score
        (the frontend renders this as "—").

        Args:
            competition: Competition instance

        Returns:
            dict: Overall ranking data grouped by category
        """
        all_events = list(
            Event.objects.filter(competition=competition)
            .order_by('event_number')
        )

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
                event_competitors = list(
                    EventCompetitor.objects.filter(
                        competitor=competitor,
                        event__competition=competition,
                    )
                    .select_related('event')
                )

                ec_by_event = {ec.event_id: ec for ec in event_competitors}

                event_results = []
                for event in all_events:
                    ec = ec_by_event.get(event.id)
                    if ec:
                        event_results.append({
                            'event_id': ec.event_id,
                            'event_number': event.event_number,
                            'event_name': event.name,
                            'phase': event.phase,
                            'result': ec.result,
                            'event_rank': ec.event_rank,
                            'score': ec.score,
                        })
                    else:
                        event_results.append({
                            'event_id': event.id,
                            'event_number': event.event_number,
                            'event_name': event.name,
                            'phase': event.phase,
                            'result': None,
                            'event_rank': None,
                            'score': None,
                        })

                final_score = sum(er['score'] or 0 for er in event_results)
                event_ranks = [er['event_rank'] for er in event_results]
                event_scores = [er['score'] for er in event_results]

                competitor_scores.append({
                    'competitor': competitor,
                    'final_score': final_score,
                    'event_ranks': event_ranks,
                    'event_scores': event_scores,
                    'event_results': event_results,
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
                'event_results': current['event_results'],
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