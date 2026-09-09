from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

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
        summary='Qualifier leaderboard for an edition',
        parameters=[OpenApiParameter('edition_id', OpenApiTypes.INT, location=OpenApiParameter.PATH)],
        responses={200: LeaderboardSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], url_path='edition/(?P<edition_id>[^/.]+)/qualifier')
    def qualifier(self, request, edition_id=None):
        return self._get_leaderboard(edition_id, CompetitionStage.StageType.QUALIFIER)

    @extend_schema(
        summary='Final leaderboard for an edition',
        parameters=[OpenApiParameter('edition_id', OpenApiTypes.INT, location=OpenApiParameter.PATH)],
        responses={200: LeaderboardSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], url_path='edition/(?P<edition_id>[^/.]+)/final')
    def final(self, request, edition_id=None):
        return self._get_leaderboard(edition_id, CompetitionStage.StageType.FINAL)

    def _get_leaderboard(self, edition_id, stage_type):
        from apps.competitions.models import CompetitionEdition

        try:
            edition = CompetitionEdition.objects.get(pk=edition_id)
        except CompetitionEdition.DoesNotExist:
            return Response({'detail': 'Edition not found.'}, status=404)

        try:
            stage = CompetitionStage.objects.get(
                competition_edition=edition,
                stage_type=stage_type,
            )
        except CompetitionStage.DoesNotExist:
            return Response({'detail': f'No {stage_type} stage for this edition.'}, status=404)

        service = CompetitionRankingService()
        ranking = service.calculate_competition_ranking(edition, stage)

        result = [
            {
                'category': category,
                'entries': entries,
            }
            for category, entries in ranking.items()
        ]

        serializer = LeaderboardSerializer(result, many=True)
        return Response(serializer.data)