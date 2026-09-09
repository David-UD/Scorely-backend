from django.core.management.base import BaseCommand

from apps.events.models import (
    CompetitionCategory,
    EventResultType,
    RankDirection,
    StatusEventCompetitor,
)
from apps.competitions.models import CompetitionType
from apps.users.models import Role


class Command(BaseCommand):
    help = 'Seed initial catalog data for Scorely.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Scorely data...')

        self._seed_roles()
        self._seed_competition_types()
        self._seed_statuses()
        self._seed_event_result_types()
        self._seed_rank_directions()
        self._seed_categories()

        self.stdout.write(self.style.SUCCESS('Seed completed successfully.'))

    def _seed_roles(self):
        roles = [
            ('SUPERADMIN', 'Superadmin'),
            ('ADMIN', 'Admin'),
        ]
        for code, name in roles:
            role, created = Role.objects.get_or_create(code=code, defaults={'name': name})
            status = 'created' if created else 'exists'
            self.stdout.write(f'  Role {code} {status}')

    def _seed_competition_types(self):
        types = [
            ('CROSSFIT', 'CrossFit'),
            ('HYROX', 'HYROX'),
        ]
        for code, name in types:
            obj, created = CompetitionType.objects.get_or_create(code=code, defaults={'name': name})
            status = 'created' if created else 'exists'
            self.stdout.write(f'  CompetitionType {code} {status}')

    def _seed_statuses(self):
        statuses = [
            ('PENDING', 'Pending'),
            ('VALID', 'Valid'),
            ('DISQUALIFIED', 'Disqualified'),
        ]
        for code, name in statuses:
            obj, created = StatusEventCompetitor.objects.get_or_create(code=code, defaults={'name': name})
            status = 'created' if created else 'exists'
            self.stdout.write(f'  StatusEventCompetitor {code} {status}')

    def _seed_event_result_types(self):
        types = [
            ('TIME', 'Time'),
            ('REPS', 'Reps'),
            ('WEIGHT', 'Weight'),
            ('DISTANCE', 'Distance'),
            ('POINTS', 'Points'),
        ]
        for code, name in types:
            obj, created = EventResultType.objects.get_or_create(code=code, defaults={'name': name})
            status = 'created' if created else 'exists'
            self.stdout.write(f'  EventResultType {code} {status}')

    def _seed_rank_directions(self):
        directions = [
            ('ASC', 'Ascending'),
            ('DESC', 'Descending'),
        ]
        for code, name in directions:
            obj, created = RankDirection.objects.get_or_create(code=code, defaults={'name': name})
            status = 'created' if created else 'exists'
            self.stdout.write(f'  RankDirection {code} {status}')

    def _seed_categories(self):
        categories = [
            ('Individual Male', 1, 1),
            ('Individual Female', 1, 1),
            ('Team Male', 2, 2),
            ('Team Female', 2, 2),
            ('Team Mixed', 2, 2),
            ('Master Male', 1, 1),
            ('Master Female', 1, 1),
        ]
        for name, min_members, max_members in categories:
            obj, created = CompetitionCategory.objects.get_or_create(
                name=name,
                defaults={'min_members': min_members, 'max_members': max_members},
            )
            status = 'created' if created else 'exists'
            self.stdout.write(f'  CompetitionCategory {name} {status}')