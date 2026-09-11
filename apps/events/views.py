from rest_framework import viewsets

from .models import (
    CompetitionCategory,
    CompetitionStage,
    EnabledCompetitionCategory,
    Event,
    EventCompetitor,
    EventResultType,
    RankDirection,
    StatusEventCompetitor,
)
from .serializers import (
    CompetitionCategorySerializer,
    CompetitionStageSerializer,
    EnabledCompetitionCategorySerializer,
    EventCompetitorSerializer,
    EventResultTypeSerializer,
    EventSerializer,
    RankDirectionSerializer,
    StatusEventCompetitorSerializer,
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
    queryset = CompetitionStage.objects.all()
    serializer_class = CompetitionStageSerializer
    filterset_fields = ('competition', 'stage_type')


class EventResultTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventResultType.objects.all()
    serializer_class = EventResultTypeSerializer


class RankDirectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RankDirection.objects.all()
    serializer_class = RankDirectionSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filterset_fields = ('competition_stage',)
    search_fields = ('name',)


class StatusEventCompetitorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StatusEventCompetitor.objects.all()
    serializer_class = StatusEventCompetitorSerializer


class EventCompetitorViewSet(viewsets.ModelViewSet):
    queryset = EventCompetitor.objects.all()
    serializer_class = EventCompetitorSerializer
    filterset_fields = ('event', 'competitor', 'status')