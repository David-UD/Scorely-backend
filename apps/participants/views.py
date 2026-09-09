from rest_framework import viewsets

from .models import Competitor, Person, Team, TeamMember
from .serializers import (
    CompetitorSerializer,
    PersonSerializer,
    TeamMemberSerializer,
    TeamSerializer,
)


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    search_fields = ('first_name', 'last_name')
    filterset_fields = ('gender', 'affiliation')


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    search_fields = ('name',)
    filterset_fields = ('competition_edition', 'affiliation')


class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    filterset_fields = ('team', 'person')


class CompetitorViewSet(viewsets.ModelViewSet):
    queryset = Competitor.objects.all()
    serializer_class = CompetitorSerializer
    search_fields = ('registration_number',)
    filterset_fields = ('competition_edition', 'competitor_type', 'competition_enabled_category')
