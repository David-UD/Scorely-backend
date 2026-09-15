from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.users.permissions import IsCompetitionAdmin, visible_competitions_q

from .models import (
    CompetitionCategory,
    EnabledCompetitionCategory,
    Event,
    EventCompetitor,
)
from .serializers import (
    CompetitionCategorySerializer,
    EnabledCompetitionCategorySerializer,
    EventCompetitorSerializer,
    EventSerializer,
)


class CompetitionCategoryViewSet(viewsets.ModelViewSet):
    queryset = CompetitionCategory.objects.all()
    serializer_class = CompetitionCategorySerializer
    search_fields = ('name',)


class EnabledCompetitionCategoryViewSet(viewsets.ModelViewSet):
    queryset = EnabledCompetitionCategory.objects.all()
    serializer_class = EnabledCompetitionCategorySerializer
    filterset_fields = ('competition',)


class EventViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, IsCompetitionAdmin)
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filterset_fields = ('competition', 'phase')
    search_fields = ('name',)

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


class EventCompetitorViewSet(viewsets.ModelViewSet):
    queryset = EventCompetitor.objects.all()
    serializer_class = EventCompetitorSerializer
    filterset_fields = ('event', 'competitor')