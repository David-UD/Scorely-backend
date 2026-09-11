from rest_framework import serializers

from .models import Athlete, Competitor, Team, TeamMember


class AthleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Athlete
        fields = ('id', 'first_name', 'last_name', 'birth_date', 'gender', 'profile_photo', 'affiliation')


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name', 'competition', 'affiliation')


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ('id', 'team', 'athlete')


class CompetitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competitor
        fields = (
            'id', 'competitor_type', 'athlete', 'team',
            'registration_number', 'competition', 'enabled_competition_category',
        )

    def validate(self, data):
        competitor_type = data.get('competitor_type')
        athlete = data.get('athlete')
        team = data.get('team')

        if competitor_type == Competitor.CompetitorType.INDIVIDUAL:
            if not athlete:
                raise serializers.ValidationError('Athlete is required for individual competitors.')
            if team:
                raise serializers.ValidationError('Team must be null for individual competitors.')
        elif competitor_type == Competitor.CompetitorType.TEAM:
            if not team:
                raise serializers.ValidationError('Team is required for team competitors.')
            if athlete:
                raise serializers.ValidationError('Athlete must be null for team competitors.')
        return data