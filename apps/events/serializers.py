from rest_framework import serializers

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


class CompetitionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionCategory
        fields = ('id', 'name', 'min_members', 'max_members')


class EnabledCompetitionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EnabledCompetitionCategory
        fields = ('id', 'competition', 'competition_category')


class CompetitionStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionStage
        fields = ('id', 'competition', 'stage_type', 'qualification_count', 'order')


class EventResultTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventResultType
        fields = ('id', 'code', 'name')


class RankDirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RankDirection
        fields = ('id', 'code', 'name')


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'competition_stage', 'event_number', 'name', 'description', 'event_result_type', 'rank_direction')


class StatusEventCompetitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusEventCompetitor
        fields = ('id', 'code', 'name')


class EventCompetitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCompetitor
        fields = ('id', 'competitor', 'event', 'result', 'event_rank', 'score', 'status')
        read_only_fields = ('event_rank', 'score')