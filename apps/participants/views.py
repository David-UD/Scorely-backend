from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from apps.users.permissions import IsCompetitionAdmin, visible_competitions_q

from .models import Athlete, Competitor, Team, TeamMember
from .serializers import (
    AthleteSerializer,
    CompetitorSerializer,
    TeamMemberSerializer,
    TeamSerializer,
)


class AthleteViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Athlete.objects.all()
    serializer_class = AthleteSerializer
    search_fields = ('first_name', 'last_name')
    filterset_fields = ('gender', 'affiliation')


class TeamViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsCompetitionAdmin)
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    search_fields = ('name',)
    filterset_fields = ('competition', 'affiliation')

    def get_queryset(self):
        return self.queryset.filter(
            competition__in=visible_competitions_q(self.request.user),
        )

    def create(self, request, *args, **kwargs):
        competition_id = request.data.get('competition')
        visible = visible_competitions_q(request.user).filter(id=competition_id)
        if not request.user.is_superuser and not visible.exists():
            raise PermissionDenied('No tenés permisos sobre esa competición.')
        return super().create(request, *args, **kwargs)


class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    filterset_fields = ('team', 'athlete')


class CompetitorViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Competitor.objects.all()
    serializer_class = CompetitorSerializer
    search_fields = ('registration_number',)
    filterset_fields = ('competition', 'competitor_type', 'enabled_competition_category')