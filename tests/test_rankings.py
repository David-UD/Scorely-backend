import pytest

from apps.events.models import Event, EventCompetitor
from apps.events.services.event_ranking_service import EventRankingService
from apps.events.services.result_parser import ResultParser
from apps.participants.models import Athlete, Competitor
from apps.rankings.services.competition_ranking_service import CompetitionRankingService
from apps.rankings.services.final_qualification_service import FinalQualificationService


@pytest.mark.django_db
class TestResultParser:
    def test_parse_time(self):
        assert ResultParser.parse('04:36', 'TIME') == 276

    def test_parse_time_with_hours(self):
        assert ResultParser.parse('01:04:36', 'TIME') == 3876

    def test_parse_reps(self):
        assert ResultParser.parse('150', 'REPS') == 150

    def test_parse_weight(self):
        assert ResultParser.parse('125.5', 'WEIGHT') == 125.5

    def test_parse_distance(self):
        assert ResultParser.parse('1000', 'DISTANCE') == 1000.0

    def test_parse_points(self):
        assert ResultParser.parse('50', 'POINTS') == 50


@pytest.mark.django_db
class TestRealEventRanking:
    def _make_competitors(self, competition, enabled_category, n):
        competitors = []
        for i in range(n):
            a = Athlete.objects.create(
                first_name=f'Atleta{i + 1}',
                last_name='Lopez',
                gender='M',
            )
            c = Competitor.objects.create(
                competition=competition,
                competitor_type=Competitor.CompetitorType.INDIVIDUAL,
                athlete=a,
                registration_number=f'C{i + 1:03d}',
                enabled_competition_category=enabled_category,
            )
            competitors.append(c)
        return competitors

    def test_event_ranking_asc_time(self, event, status_valid, competition, enabled_category):
        competitors = self._make_competitors(competition, enabled_category, 4)

        results_map = {
            competitors[0]: '05:00',
            competitors[1]: '04:00',
            competitors[2]: '03:00',
            competitors[3]: '06:00',
        }
        for comp, result in results_map.items():
            EventCompetitor.objects.create(
                competitor=comp,
                event=event,
                result=result,
                status=status_valid,
            )

        EventRankingService.calculate_event_ranking(event)

        ranks = {}
        for comp in competitors:
            ec = EventCompetitor.objects.get(competitor=comp, event=event)
            ranks[comp.registration_number] = ec.event_rank

        assert ranks['C003'] == 1  # 03:00 fastest
        assert ranks['C002'] == 2  # 04:00
        assert ranks['C001'] == 3  # 05:00
        assert ranks['C004'] == 4  # 06:00

    def test_dense_ranking_ties(self, event, status_valid, competition, enabled_category, scoring_rules):
        competitors = self._make_competitors(competition, enabled_category, 4)

        results_map = {
            competitors[0]: '03:00',
            competitors[1]: '04:00',
            competitors[2]: '04:00',  # tie with competitor 1
            competitors[3]: '06:00',
        }
        for comp, result in results_map.items():
            EventCompetitor.objects.create(
                competitor=comp,
                event=event,
                result=result,
                status=status_valid,
            )

        EventRankingService.calculate_event_ranking(event)

        ranks = {}
        for comp in competitors:
            ec = EventCompetitor.objects.get(competitor=comp, event=event)
            ranks[comp.registration_number] = (ec.event_rank, ec.score)

        assert ranks['C001'][0] == 1    # 03:00 → 1st
        assert ranks['C001'][1] == 100  # 100 pts
        assert ranks['C002'][0] == 2    # 04:00 → 2nd (tie)
        assert ranks['C002'][1] == 94
        assert ranks['C003'][0] == 2    # 04:00 → 2nd (tie)
        assert ranks['C003'][1] == 94
        assert ranks['C004'][0] == 4    # 06:00 → 4th (skips 3rd)
        assert ranks['C004'][1] == 82

    def test_disqualified_not_ranked(self, event, status_valid, status_disqualified, competition, enabled_category):
        competitors = self._make_competitors(competition, enabled_category, 2)

        EventCompetitor.objects.create(
            competitor=competitors[0],
            event=event,
            result='03:00',
            status=status_valid,
        )
        EventCompetitor.objects.create(
            competitor=competitors[1],
            event=event,
            result='02:00',
            status=status_disqualified,
        )

        EventRankingService.calculate_event_ranking(event)

        ranked = EventCompetitor.objects.filter(event=event, event_rank__isnull=False)
        assert ranked.count() == 1
        assert ranked[0].competitor == competitors[0]


@pytest.mark.django_db
class TestCompetitionRankingService:
    def _make_competitors(self, competition, enabled_category, n):
        competitors = []
        for i in range(n):
            a = Athlete.objects.create(
                first_name=f'Atleta{i + 1}',
                last_name='Lopez',
                gender='M',
            )
            c = Competitor.objects.create(
                competition=competition,
                competitor_type=Competitor.CompetitorType.INDIVIDUAL,
                athlete=a,
                registration_number=f'CR{i + 1:03d}',
                enabled_competition_category=enabled_category,
            )
            competitors.append(c)
        return competitors

    def test_final_score_sum(self, event, status_valid, competition, enabled_category, scoring_rules):
        competitors = self._make_competitors(competition, enabled_category, 2)

        events = [event]
        for i in range(2, 6):
            events.append(Event.objects.create(
                competition_stage=event.competition_stage,
                event_number=i,
                name=f'WOD {i}',
                event_result_type=event.event_result_type,
                rank_direction=event.rank_direction,
            ))

        # Competitor 1: positions 2,1,2,1,1 → 94+100+94+100+100 = 488
        results_c1 = ['05:00', '04:00', '05:00', '04:00', '04:00']
        # Competitor 2: positions 1,2,1,2,2 → 100+94+100+94+94 = 482
        results_c2 = ['04:00', '05:00', '04:00', '05:00', '05:00']

        for idx, ec_event in enumerate(events):
            EventCompetitor.objects.create(
                competitor=competitors[0],
                event=ec_event,
                result=results_c1[idx],
                status=status_valid,
            )
            EventCompetitor.objects.create(
                competitor=competitors[1],
                event=ec_event,
                result=results_c2[idx],
                status=status_valid,
            )

        for ec_event in events:
            EventRankingService.calculate_event_ranking(ec_event)

        service = CompetitionRankingService()
        ranking = service.calculate_competition_ranking(competition, event.competition_stage)

        entry = ranking[list(ranking.keys())[0]]
        assert len(entry) == 2
        assert entry[0]['final_score'] == 488
        assert entry[1]['final_score'] == 482

    def test_tie_breaking_places(self, event, status_valid, competition, enabled_category, scoring_rules):
        # Both get 476, competitor 1 has 2 wins vs competitor 2 with 2 wins → tie maintained
        events = [event]
        for i in range(2, 6):
            events.append(Event.objects.create(
                competition_stage=event.competition_stage,
                event_number=i,
                name=f'WOD {i}',
                event_result_type=event.event_result_type,
                rank_direction=event.rank_direction,
            ))

        results_c1 = ['03:00', '03:00', '04:00', '04:00', '05:00']  # 1,1,2,2,3 → 100+100+94+94+88 = 476
        results_c2 = ['04:00', '04:00', '03:00', '03:00', '05:00']  # 2,2,1,1,3 → 94+94+100+100+88 = 476
        results_c3 = ['05:00', '05:00', '05:00', '05:00', '04:00']  # 3,3,3,3,2 → 88*4+94 = 446

        people = [
            Athlete.objects.create(first_name='X1', last_name='Lopez', gender='M'),
            Athlete.objects.create(first_name='X2', last_name='Lopez', gender='M'),
            Athlete.objects.create(first_name='X3', last_name='Lopez', gender='M'),
        ]
        comps = []
        for i, a in enumerate(people):
            comps.append(Competitor.objects.create(
                competition=competition,
                competitor_type=Competitor.CompetitorType.INDIVIDUAL,
                athlete=a,
                registration_number=f'CT{i + 1:03d}',
                enabled_competition_category=enabled_category,
            ))

        all_results = [results_c1, results_c2, results_c3]
        for idx, ec_event in enumerate(events):
            for ci, comp in enumerate(comps):
                EventCompetitor.objects.create(
                    competitor=comp,
                    event=ec_event,
                    result=all_results[ci][idx],
                    status=status_valid,
                )

        for ec_event in events:
            EventRankingService.calculate_event_ranking(ec_event)

        service = CompetitionRankingService()
        ranking = service.calculate_competition_ranking(competition, event.competition_stage)

        entry = ranking[list(ranking.keys())[0]]
        assert entry[0]['rank'] == 1
        assert entry[1]['rank'] == 1
        assert entry[2]['rank'] == 3


@pytest.mark.django_db
class TestFinalQualificationService:
    def test_qualifier_top_n(self, event, status_valid, competition, enabled_category, scoring_rules):
        competitors = []
        for i in range(8):
            a = Athlete.objects.create(first_name=f'A{i}', last_name='Lopez', gender='M')
            c = Competitor.objects.create(
                competition=competition,
                competitor_type=Competitor.CompetitorType.INDIVIDUAL,
                athlete=a,
                registration_number=f'Q{i:03d}',
                enabled_competition_category=enabled_category,
            )
            competitors.append(c)

        # different times → distinct ranks
        times = [f'0{i + 1}:00' if i + 1 < 10 else '10:00' for i in range(8)]
        for comp, t in zip(competitors, times):
            EventCompetitor.objects.create(
                competitor=comp,
                event=event,
                result=t,
                status=status_valid,
            )

        EventRankingService.calculate_event_ranking(event)

        service = FinalQualificationService()
        qualifiers = service.get_qualifiers(competition)

        category_key = list(qualifiers.keys())[0]
        qualified = qualifiers[category_key]
        assert len(qualified) == 5  # qualification_count = 5