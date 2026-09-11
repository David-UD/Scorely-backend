from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import (
    CompetitionCategory,
    CompetitionStage,
    EnabledCompetitionCategory,
    Event,
    EventCompetitor,
)
from .serializers import (
    CompetitionCategorySerializer,
    CompetitionStageSerializer,
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


class CompetitionStageViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = CompetitionStage.objects.all()
    serializer_class = CompetitionStageSerializer
    filterset_fields = ('competition', 'stage_type')


class EventViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filterset_fields = ('competition_stage',)
    search_fields = ('name',)


class EventCompetitorViewSet(viewsets.ModelViewSet):
    queryset = EventCompetitor.objects.all()
    serializer_class = EventCompetitorSerializer
    filterset_fields = ('event', 'competitor')