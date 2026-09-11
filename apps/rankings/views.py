from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.competitions.models import Competition
from apps.events.models import CompetitionStage
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
        return self._get_leaderboard(competition_id, CompetitionStage.StageType.QUALIFIER)

    @extend_schema(
        summary='Final leaderboard for a competition',
        parameters=[OpenApiParameter('competition_id', OpenApiTypes.INT, location=OpenApiParameter.PATH)],
        responses={200: LeaderboardSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], url_path='competition/(?P<competition_id>[^/.]+)/final')
    def final(self, request, competition_id=None):
        return self._get_leaderboard(competition_id, CompetitionStage.StageType.FINAL)

    def _get_leaderboard(self, competition_id, stage_type):
        try:
            competition = Competition.objects.get(pk=competition_id)
        except Competition.DoesNotExist:
            return Response({'detail': 'Competition not found.'}, status=404)

        try:
            stage = CompetitionStage.objects.get(
                competition=competition,
                stage_type=stage_type,
            )
        except CompetitionStage.DoesNotExist:
            return Response({'detail': f'No {stage_type} stage for this competition.'}, status=404)

        service = CompetitionRankingService()
        ranking = service.calculate_competition_ranking(competition, stage)

        result = [
            {
                'category': category,
                'entries': entries,
            }
            for category, entries in ranking.items()
        ]

        serializer = LeaderboardSerializer(result, many=True)
        return Response(serializer.data)