from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.competitions.models import Competition
from apps.events.models import Event
from apps.rankings.serializers import LeaderboardSerializer
from apps.rankings.services.competition_ranking_service import CompetitionRankingService


class LeaderboardViewSet(viewsets.ViewSet):
    """
    Public leaderboard endpoints.
    """

    permission_classes = [AllowAny]
    serializer_class = LeaderboardSerializer

    @extend_schema(
        summary='Qualifier leaderboard for a competition',
        parameters=[OpenApiParameter('competition_id', OpenApiTypes.INT, location=OpenApiParameter.PATH)],
        responses={200: LeaderboardSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], url_path='competition/(?P<competition_id>[^/.]+)/qualifier')
    def qualifier(self, request, competition_id=None):
        try:
            competition = Competition.objects.get(pk=competition_id)
        except Competition.DoesNotExist:
            return Response({'detail': 'Competition not found.'}, status=404)

        if not Event.objects.filter(competition=competition, phase=Event.Phase.QUALIFIER).exists():
            return Response({'detail': 'No qualifier events for this competition.'}, status=404)

        service = CompetitionRankingService()
        ranking = service.calculate_competition_ranking(competition, Event.Phase.QUALIFIER)
        return self._render(request, ranking)

    @extend_schema(
        summary='Overall leaderboard for a competition (all phases combined)',
        parameters=[OpenApiParameter('competition_id', OpenApiTypes.INT, location=OpenApiParameter.PATH)],
        responses={200: LeaderboardSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], url_path='competition/(?P<competition_id>[^/.]+)/final')
    def final(self, request, competition_id=None):
        try:
            competition = Competition.objects.get(pk=competition_id)
        except Competition.DoesNotExist:
            return Response({'detail': 'Competition not found.'}, status=404)

        service = CompetitionRankingService()
        ranking = service.calculate_overall_ranking(competition)
        return self._render(request, ranking)

    def _render(self, request, ranking):
        result = [
            {
                'category': category,
                'entries': entries,
            }
            for category, entries in ranking.items()
        ]
        serializer = LeaderboardSerializer(result, many=True)
        return Response(serializer.data)