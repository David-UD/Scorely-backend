from rest_framework import viewsets

from .models import Athlete, Competitor, Team, TeamMember
from .serializers import (
    AthleteSerializer,
    CompetitorSerializer,
    TeamMemberSerializer,
    TeamSerializer,
)


class AthleteViewSet(viewsets.ModelViewSet):
    queryset = Athlete.objects.all()
    serializer_class = AthleteSerializer
    search_fields = ('first_name', 'last_name')
    filterset_fields = ('gender', 'affiliation')


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    search_fields = ('name',)
    filterset_fields = ('competition', 'affiliation')


class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    filterset_fields = ('team', 'athlete')


class CompetitorViewSet(viewsets.ModelViewSet):
    queryset = Competitor.objects.all()
    serializer_class = CompetitorSerializer
    search_fields = ('registration_number',)
    filterset_fields = ('competition', 'competitor_type', 'enabled_competition_category')