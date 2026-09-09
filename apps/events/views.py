from rest_framework import viewsets

from .models import (
    CompetitionCategory,
    CompetitionEnabledCategory,
    CompetitionStage,
    Event,
    EventCompetitor,
    EventResultType,
    RankDirection,
    StatusEventCompetitor,
)
from .serializers import (
    CompetitionCategorySerializer,
    CompetitionEnabledCategorySerializer,
    CompetitionStageSerializer,
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


class CompetitionEnabledCategoryViewSet(viewsets.ModelViewSet):
    queryset = CompetitionEnabledCategory.objects.all()
    serializer_class = CompetitionEnabledCategorySerializer
    filterset_fields = ('competition_edition',)


class CompetitionStageViewSet(viewsets.ModelViewSet):
    queryset = CompetitionStage.objects.all()
    serializer_class = CompetitionStageSerializer
    filterset_fields = ('competition_edition', 'stage_type')


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
