from datetime import date

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.competitions.models import (
    Affiliation,
    Competition,
    CompetitionType,
    Location,
    StatusCompetition,
)
from apps.events.models import (
    CompetitionCategory,
    EnabledCompetitionCategory,
    Event,
    EventCompetitor,
)
from apps.events.services.event_ranking_service import EventRankingService
from apps.participants.models import Athlete, Competitor, Team, TeamMember
from apps.scoring.models import ScoringRule


class Command(BaseCommand):
    help = 'Seed initial catalog data and demo data for Scorely.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Scorely data...')

        self._seed_competition_statuses()
        self._seed_competition_types()
        self._seed_categories()

        self._seed_affiliations()
        self._seed_locations()
        self._seed_competitions()
        self._seed_enabled_categories()
        self._seed_stages_and_events()
        self._seed_scoring_rules()
        self._seed_participants()
        self._seed_results()
        self._compute_event_rankings(phase=Event.Phase.QUALIFIER)
        self._seed_final_results()
        self._compute_event_rankings(phase=Event.Phase.FINAL)

        self.stdout.write(self.style.SUCCESS('Seed completed successfully.'))

    def _seed_competition_statuses(self):
        statuses = [
            ('DRAFT', 'Draft'),
            ('PUBLISHED', 'Published'),
            ('FINISHED', 'Finished'),
            ('CANCELLED', 'Cancelled'),
        ]
        for code, name in statuses:
            obj, created = StatusCompetition.objects.get_or_create(code=code, defaults={'name': name})
            status = 'created' if created else 'exists'
            self.stdout.write(f'  StatusCompetition {code} {status}')

    def _seed_competition_types(self):
        types = [
            ('CROSSFIT', 'CrossFit'),
            ('HYROX', 'HYROX'),
        ]
        for code, name in types:
            obj, created = CompetitionType.objects.get_or_create(code=code, defaults={'name': name})
            status = 'created' if created else 'exists'
            self.stdout.write(f'  CompetitionType {code} {status}')

    def _seed_categories(self):
        categories = [
            ('Individual Male', 1, 1),
            ('Individual Female', 1, 1),
            ('Team Male', 2, 2),
            ('Team Female', 2, 2),
            ('Team Mixed', 2, 2),
            ('Master Male', 1, 1),
            ('Master Female', 1, 1),
            ('Principiantes Individual', 1, 1),
            ('Intermedios Individual', 1, 1),
            ('RX Individual', 1, 1),
            ('Principiantes Mixto', 2, 2),
            ('Intermedios Duo', 2, 2),
            ('Relevos 4', 4, 4),
        ]
        for name, min_members, max_members in categories:
            obj, created = CompetitionCategory.objects.get_or_create(
                name=name,
                defaults={'min_members': min_members, 'max_members': max_members},
            )
            status = 'created' if created else 'exists'
            self.stdout.write(f'  CompetitionCategory {name} {status}')

    def _seed_affiliations(self):
        affiliations = [
            {
                'name': 'CrossFit North Box',
                'city': 'Madrid',
                'state': 'Madrid',
                'country': 'Spain',
            },
            {
                'name': 'CrossFit South Box',
                'city': 'Sevilla',
                'state': 'Andalucía',
                'country': 'Spain',
            },
            {
                'name': 'CrossFit East Box',
                'city': 'Valencia',
                'state': 'Comunidad Valenciana',
                'country': 'Spain',
            },
            {
                'name': 'CrossFit West Box',
                'city': 'Bilbao',
                'state': 'País Vasco',
                'country': 'Spain',
            },
            {
                'name': 'HYROX Core Madrid',
                'city': 'Madrid',
                'state': 'Madrid',
                'country': 'Spain',
            },
            {
                'name': 'HYROX Core Barcelona',
                'city': 'Barcelona',
                'state': 'Cataluña',
                'country': 'Spain',
            },
        ]
        self._affiliations = {}
        for data in affiliations:
            obj, created = Affiliation.objects.get_or_create(
                name=data['name'],
                defaults={
                    'city': data['city'],
                    'state': data['state'],
                    'country': data['country'],
                },
            )
            self._affiliations[data['name']] = obj
            status = 'created' if created else 'exists'
            self.stdout.write(f'  Affiliation {data["name"]} {status}')

    def _seed_locations(self):
        locations = [
            {
                'name': 'Sede CrossFit North',
                'address': 'Calle Deportes 1',
                'city': 'Madrid',
                'state': 'Madrid',
                'country': 'Spain',
            },
            {
                'name': 'Sede CrossFit South',
                'address': 'Avenida Atletas 2',
                'city': 'Sevilla',
                'state': 'Andalucía',
                'country': 'Spain',
            },
            {
                'name': 'Sede HYROX Madrid',
                'address': 'Paseo del Fitness 3',
                'city': 'Madrid',
                'state': 'Madrid',
                'country': 'Spain',
            },
            {
                'name': 'Sede HYROX Barcelona',
                'address': 'Ronda Deportiva 4',
                'city': 'Barcelona',
                'state': 'Cataluña',
                'country': 'Spain',
            },
        ]
        self._locations = {}
        for data in locations:
            obj, created = Location.objects.get_or_create(
                name=data['name'],
                defaults={
                    'address': data['address'],
                    'city': data['city'],
                    'state': data['state'],
                    'country': data['country'],
                },
            )
            self._locations[data['name']] = obj
            status = 'created' if created else 'exists'
            self.stdout.write(f'  Location {data["name"]} {status}')

    def _seed_competitions(self):
        cf_type = CompetitionType.objects.get(code='CROSSFIT')
        hy_type = CompetitionType.objects.get(code='HYROX')
        published = StatusCompetition.objects.get(code='PUBLISHED')

        definitions = [
            {
                'key': 'cf_a',
                'name': 'Summer Games CrossFit',
                'competition_type': cf_type,
                'affiliation': self._affiliations['CrossFit North Box'],
                'location': self._locations['Sede CrossFit North'],
                'year': 2026,
            },
            {
                'key': 'cf_b',
                'name': 'Open CrossFit Teams',
                'competition_type': cf_type,
                'affiliation': self._affiliations['CrossFit South Box'],
                'location': self._locations['Sede CrossFit South'],
                'year': 2026,
            },
            {
                'key': 'hy_a',
                'name': 'HYROX Madrid Race',
                'competition_type': hy_type,
                'affiliation': self._affiliations['HYROX Core Madrid'],
                'location': self._locations['Sede HYROX Madrid'],
                'year': 2026,
            },
            {
                'key': 'hy_b',
                'name': 'HYROX Barcelona Race',
                'competition_type': hy_type,
                'affiliation': self._affiliations['HYROX Core Barcelona'],
                'location': self._locations['Sede HYROX Barcelona'],
                'year': 2026,
            },
        ]
        self._competitions = {}
        for definition in definitions:
            competition, created = Competition.objects.get_or_create(
                name=definition['name'],
                defaults={
                    'competition_type': definition['competition_type'],
                    'status': published,
                    'affiliation': definition['affiliation'],
                    'location': definition['location'],
                    'start_date': date(definition['year'], 6, 1),
                    'end_date': date(definition['year'], 6, 3),
                    'slug': slugify(definition['name']),
                },
            )
            self._competitions[definition['key']] = competition
            status = 'created' if created else 'exists'
            self.stdout.write(f'  Competition {definition["name"]} {status}')

    def _seed_enabled_categories(self):
        self._enabled_categories = {}
        plans = {
            'cf_a': {
                'Principiantes Individual': 2,
                'Intermedios Individual': 2,
                'Principiantes Mixto': 2,
            },
            'cf_b': {
                'Relevos 4': 2,
            },
            'hy_a': {
                'RX Individual': 0,
            },
            'hy_b': {
                'RX Individual': 0,
            },
        }
        for key, category_map in plans.items():
            competition = self._competitions[key]
            self._enabled_categories[key] = []
            for category_name, slots in category_map.items():
                category = CompetitionCategory.objects.get(name=category_name)
                obj, created = EnabledCompetitionCategory.objects.get_or_create(
                    competition=competition,
                    competition_category=category,
                    defaults={'finalist_slots': slots},
                )
                if not created and obj.finalist_slots != slots:
                    obj.finalist_slots = slots
                    obj.save(update_fields=['finalist_slots'])
                self._enabled_categories[key].append(obj)
                status = 'created' if created else 'exists'
                self.stdout.write(f'  EnabledCompetitionCategory {competition} - {category_name} (slots={slots}) {status}')

    def _seed_stages_and_events(self):
        self._events = {}

        def create_event(competition, phase, event_number, name, workout, is_ascending):
            event, created = Event.objects.get_or_create(
                competition=competition,
                phase=phase,
                event_number=event_number,
                defaults={
                    'name': name,
                    'workout': workout,
                    'is_ascending': is_ascending,
                },
            )
            status = 'created' if created else 'exists'
            self.stdout.write(f'  Event {name} {status}')
            return event

        self._events['cf_a'] = {}
        self._events['cf_b'] = {}

        self._events['cf_a']['qualifier'] = [
            create_event(self._competitions['cf_a'], Event.Phase.QUALIFIER, 1, 'Fran', '21-15-9: Thrusters (43kg) + Pull-ups', True),
            create_event(self._competitions['cf_a'], Event.Phase.QUALIFIER, 2, 'AMRAP 12 min', 'AMRAP 12 min: 10 Burpees, 10 Box Jump, 10 KB Swing', False),
            create_event(self._competitions['cf_a'], Event.Phase.QUALIFIER, 3, 'Max Snatch', '1RM Snatch — peso máximo en 10 min', False),
        ]
        self._events['cf_a']['final'] = [
            create_event(self._competitions['cf_a'], Event.Phase.FINAL, 4, 'WOD Final', 'Evento final por tiempo', True),
        ]

        self._events['cf_b']['qualifier'] = [
            create_event(self._competitions['cf_b'], Event.Phase.QUALIFIER, 1, 'Fran', '21-15-9: Thrusters (43kg) + Pull-ups', True),
            create_event(self._competitions['cf_b'], Event.Phase.QUALIFIER, 2, 'AMRAP 12 min', 'AMRAP 12 min: 10 Burpees, 10 Box Jump, 10 KB Swing', False),
            create_event(self._competitions['cf_b'], Event.Phase.QUALIFIER, 3, 'Max Snatch', '1RM Snatch — peso máximo en 10 min', False),
            create_event(self._competitions['cf_b'], Event.Phase.QUALIFIER, 4, 'Run 5K', 'Carrera 5000m en pista', False),
        ]
        self._events['cf_b']['final'] = [
            create_event(self._competitions['cf_b'], Event.Phase.FINAL, 5, 'WOD Final', 'Evento final por tiempo', True),
        ]

        self._events['hy_a'] = {}
        self._events['hy_b'] = {}
        self._events['hy_a']['qualifier'] = [
            create_event(self._competitions['hy_a'], Event.Phase.QUALIFIER, 1, 'HYROX Race', 'Carrera HYROX por tiempo', True),
        ]
        self._events['hy_b']['qualifier'] = [
            create_event(self._competitions['hy_b'], Event.Phase.QUALIFIER, 1, 'HYROX Race', 'Carrera HYROX por tiempo', True),
        ]

    def _seed_scoring_rules(self):
        points_by_position = {
            1: 100,
            2: 94,
            3: 88,
            4: 82,
            5: 76,
            6: 70,
            7: 64,
            8: 58,
            9: 52,
            10: 46,
        }
        for competition in self._competitions.values():
            for position, points in points_by_position.items():
                obj, created = ScoringRule.objects.get_or_create(
                    competition=competition,
                    position=position,
                    defaults={'points': points},
                )
                status = 'created' if created else 'exists'
                self.stdout.write(f'  ScoringRule {competition} pos {position} {status}')

    def _seed_participants(self):
        self._competitors = {
            'cf_a': [],
            'cf_b': [],
            'hy_a': [],
            'hy_b': [],
        }

        def get_athlete(first_name, last_name):
            athlete, created = Athlete.objects.get_or_create(
                first_name=first_name,
                last_name=last_name,
                defaults={'gender': 'M'},
            )
            status = 'created' if created else 'exists'
            self.stdout.write(f'  Athlete {first_name} {last_name} {status}')
            return athlete

        def create_individual(key, category_name, first_name, last_name, reg_number):
            competition = self._competitions[key]
            enabled = next(
                ec for ec in self._enabled_categories[key]
                if ec.competition_category.name == category_name
            )
            athlete = get_athlete(first_name, last_name)
            competitor, created = Competitor.objects.get_or_create(
                competition=competition,
                competitor_type=Competitor.CompetitorType.INDIVIDUAL,
                athlete=athlete,
                enabled_competition_category=enabled,
                defaults={'registration_number': reg_number},
            )
            self._competitors[key].append(competitor)
            status = 'created' if created else 'exists'
            self.stdout.write(f'  Competitor {first_name} {last_name} {status}')

        def create_team(key, category_name, team_name, athlete_names, reg_number):
            competition = self._competitions[key]
            enabled = next(
                ec for ec in self._enabled_categories[key]
                if ec.competition_category.name == category_name
            )
            team = Team.objects.filter(name=team_name).first()
            created_t = team is None
            if created_t:
                team = Team.objects.create(name=team_name)
            for first_name, last_name in athlete_names:
                athlete = get_athlete(first_name, last_name)
                TeamMember.objects.get_or_create(team=team, athlete=athlete)
            competitor, created_c = Competitor.objects.get_or_create(
                competition=competition,
                competitor_type=Competitor.CompetitorType.TEAM,
                team=team,
                enabled_competition_category=enabled,
                defaults={'registration_number': reg_number},
            )
            self._competitors[key].append(competitor)
            status = 'created' if created_t else 'exists'
            self.stdout.write(f'  Team {team_name} {status}')
            status = 'created' if created_c else 'exists'
            self.stdout.write(f'  Competitor {team_name} {status}')

        create_individual('cf_a', 'Principiantes Individual', 'Carlos', 'Primero', 'DEMO-CFA-001')
        create_individual('cf_a', 'Principiantes Individual', 'Luis', 'Segundo', 'DEMO-CFA-002')
        create_individual('cf_a', 'Principiantes Individual', 'Daniel', 'Nuevo', 'DEMO-CFA-006')
        create_individual('cf_a', 'Intermedios Individual', 'Ana', 'Tercero', 'DEMO-CFA-003')
        create_team(
            'cf_a',
            'Principiantes Mixto',
            'Duo Alpha',
            [('Marta', 'Cuatro'), ('Pedro', 'Cinco')],
            'DEMO-CFA-004',
        )
        create_team(
            'cf_a',
            'Principiantes Mixto',
            'Duo Beta',
            [('Lucía', 'Seis'), ('Jorge', 'Siete')],
            'DEMO-CFA-005',
        )

        create_team(
            'cf_b',
            'Relevos 4',
            'Relay Alpha',
            [('Miguel', 'Uno'), ('Sofía', 'Dos'), ('Diego', 'Tres'), ('Elena', 'Cuatro')],
            'DEMO-CFB-001',
        )
        create_team(
            'cf_b',
            'Relevos 4',
            'Relay Beta',
            [('Raúl', 'Cinco'), ('Nuria', 'Seis'), ('Iker', 'Siete'), ('Clara', 'Ocho')],
            'DEMO-CFB-002',
        )

        create_individual('hy_a', 'RX Individual', 'Hugo', 'Madrid1', 'DEMO-HYA-001')
        create_individual('hy_a', 'RX Individual', 'Paula', 'Madrid2', 'DEMO-HYA-002')
        create_individual('hy_b', 'RX Individual', 'Alex', 'Barna1', 'DEMO-HYB-001')
        create_individual('hy_b', 'RX Individual', 'Nora', 'Barna2', 'DEMO-HYB-002')

    def _seed_results(self):
        results_by_competitor = {
            'DEMO-CFA-001': {
                'Fran': '04:36',
                'AMRAP 12 min': '315',
                'Max Snatch': '97.5',
            },
            'DEMO-CFA-002': {
                'Fran': '04:52',
                'AMRAP 12 min': '289',
                'Max Snatch': '82.5',
            },
            'DEMO-CFA-003': {
                'Fran': '04:20',
                'AMRAP 12 min': '341',
                'Max Snatch': '105.0',
            },
            'DEMO-CFA-004': {
                'Fran': '05:10',
                'AMRAP 12 min': '278',
                'Max Snatch': '90.0',
            },
            'DEMO-CFA-005': {
                'Fran': '05:10',
                'AMRAP 12 min': '265',
                'Max Snatch': '95.0',
            },
            'DEMO-CFA-006': {
                'Fran': '05:20',
                'AMRAP 12 min': '250',
                'Max Snatch': '70.0',
            },
            'DEMO-CFB-001': {
                'Fran': '05:30',
                'AMRAP 12 min': '310',
                'Max Snatch': '110.0',
                'Run 5K': '5000',
            },
            'DEMO-CFB-002': {
                'Fran': '06:02',
                'AMRAP 12 min': '295',
                'Max Snatch': '100.0',
                'Run 5K': '4850',
            },
            'DEMO-HYA-001': {
                'HYROX Race': '01:12:30',
            },
            'DEMO-HYA-002': {
                'HYROX Race': '01:18:15',
            },
            'DEMO-HYB-001': {
                'HYROX Race': '01:10:45',
            },
            'DEMO-HYB-002': {
                'HYROX Race': '01:16:52',
            },
        }

        created_count = 0
        updated_count = 0
        for competitors in self._competitors.values():
            for competitor in competitors:
                results = results_by_competitor.get(competitor.registration_number, {})
                events = self._qualifier_events_for(competitor)
                for event in events:
                    default_result = str(event.event_number)
                    result = results.get(event.name, default_result)
                    obj, created = EventCompetitor.objects.update_or_create(
                        competitor=competitor,
                        event=event,
                        defaults={'result': result},
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
        self.stdout.write(f'  EventCompetitor {created_count} created, {updated_count} updated')

    def _seed_final_results(self):
        results_by_competitor = {
            'DEMO-CFA-001': {'WOD Final': '09:12'},
            'DEMO-CFA-002': {'WOD Final': '10:05'},
            'DEMO-CFA-003': {'WOD Final': '08:47'},
            'DEMO-CFA-004': {'WOD Final': '11:22'},
            'DEMO-CFA-005': {'WOD Final': '11:58'},
            'DEMO-CFB-001': {'WOD Final': '12:40'},
            'DEMO-CFB-002': {'WOD Final': '13:25'},
        }

        from apps.rankings.services.competition_ranking_service import CompetitionRankingService
        service = CompetitionRankingService()

        created_count = 0
        for key in ('cf_a', 'cf_b'):
            competition = self._competitions[key]

            ranking = service.calculate_competition_ranking(
                competition, Event.Phase.QUALIFIER,
            )

            for enabled_category, ranked_competitors in ranking.items():
                slots = enabled_category.finalist_slots
                if not slots:
                    continue

                qualifiers = [
                    item['competitor']
                    for item in ranked_competitors[:slots]
                ]

                for competitor in qualifiers:
                    results = results_by_competitor.get(competitor.registration_number, {})
                    for event in self._events[key].get('final', []):
                        default_result = str(event.event_number)
                        result = results.get(event.name, default_result)
                        obj, created = EventCompetitor.objects.update_or_create(
                            competitor=competitor,
                            event=event,
                            defaults={'result': result},
                        )
                        if created:
                            created_count += 1

        self.stdout.write(f'  EventCompetitor (final) {created_count} created')

    def _qualifier_events_for(self, competitor):
        competition_key = None
        for key in ('cf_a', 'cf_b', 'hy_a', 'hy_b'):
            if competitor.competition_id == self._competitions[key].id:
                competition_key = key
                break
        if competition_key is None:
            return []
        return self._events[competition_key].get('qualifier', [])

    def _compute_event_rankings(self, phase=None):
        for key in ('cf_a', 'cf_b', 'hy_a', 'hy_b'):
            for stage_key in self._events[key]:
                for event in self._events[key][stage_key]:
                    if phase and event.phase != phase:
                        continue
                    ranked = EventRankingService.calculate_event_ranking(event)
                    self.stdout.write(f'  EventRanking {event.name}: {len(ranked)} scored')