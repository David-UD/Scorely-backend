from rest_framework import serializers

from .models import Competitor, Person, Team, TeamMember


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ('id', 'first_name', 'last_name', 'birth_date', 'gender', 'profile_photo', 'affiliation')


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'competition_edition', 'competition_enabled_category', 'affiliation', 'name')


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ('id', 'team', 'person')


class CompetitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competitor
        fields = (
            'id', 'competition_edition', 'competitor_type', 'person', 'team',
            'registration_number', 'competition_enabled_category',
        )

    def validate(self, data):
        competitor_type = data.get('competitor_type')
        person = data.get('person')
        team = data.get('team')

        if competitor_type == Competitor.CompetitorType.INDIVIDUAL:
            if not person:
                raise serializers.ValidationError('Person is required for individual competitors.')
            if team:
                raise serializers.ValidationError('Team must be null for individual competitors.')
        elif competitor_type == Competitor.CompetitorType.TEAM:
            if not team:
                raise serializers.ValidationError('Team is required for team competitors.')
            if person:
                raise serializers.ValidationError('Person must be null for team competitors.')
        return data
