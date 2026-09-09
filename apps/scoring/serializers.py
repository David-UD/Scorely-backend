from rest_framework import serializers

from .models import ScoringRule


class ScoringRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoringRule
        fields = ('id', 'competition_edition', 'position', 'points')
