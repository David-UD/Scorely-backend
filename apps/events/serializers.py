from rest_framework import serializers

from .models import (
    CompetitionCategory,
    CompetitionStage,
    EnabledCompetitionCategory,
    Event,
    EventCompetitor,
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


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'competition_stage', 'event_number', 'name', 'workout', 'description', 'is_ascending', 'is_active')


class EventCompetitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCompetitor
        fields = ('id', 'competitor', 'event', 'result', 'event_rank', 'score')
        read_only_fields = ('event_rank', 'score')