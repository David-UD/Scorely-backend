from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.participants.models import Competitor


class LeaderboardEntrySerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    competitor_id = serializers.IntegerField(source='competitor.id', read_only=True)
    display_name = serializers.SerializerMethodField()
    final_score = serializers.IntegerField()
    event_ranks = serializers.ListField(child=serializers.IntegerField())
    event_scores = serializers.ListField(
        child=serializers.IntegerField(allow_null=True),
        required=False,
    )

    @extend_schema_field(serializers.CharField)
    def get_display_name(self, obj):
        competitor = obj['competitor']
        if competitor.competitor_type == Competitor.CompetitorType.INDIVIDUAL:
            return str(competitor.athlete)
        return competitor.team.name


class LeaderboardSerializer(serializers.Serializer):
    category = serializers.SerializerMethodField()
    entries = LeaderboardEntrySerializer(many=True)

    @extend_schema_field(serializers.CharField)
    def get_category(self, obj):
        return str(obj['category'].competition_category.name)