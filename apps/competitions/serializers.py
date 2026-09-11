from rest_framework import serializers

from .models import Affiliation, Competition, CompetitionType, Location, StatusCompetition


class CompetitionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionType
        fields = ('id', 'code', 'name')


class AffiliationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Affiliation
        fields = ('id', 'name', 'description', 'logo', 'city', 'state', 'country')


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name', 'address', 'city', 'state', 'country', 'latitude', 'longitude')


class StatusCompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusCompetition
        fields = ('id', 'code', 'name')


class CompetitionSerializer(serializers.ModelSerializer):
    competition_type = CompetitionTypeSerializer(read_only=True)
    status = StatusCompetitionSerializer(read_only=True)
    affiliation = AffiliationSerializer(read_only=True)
    location = LocationSerializer(read_only=True)

    class Meta:
        model = Competition
        fields = (
            'id', 'name', 'description', 'competition_type', 'status',
            'affiliation', 'location', 'year', 'start_date', 'end_date', 'slug',
        )


class CompetitionWriteSerializer(serializers.ModelSerializer):
    competition_type = serializers.PrimaryKeyRelatedField(queryset=CompetitionType.objects.all())
    status = serializers.PrimaryKeyRelatedField(queryset=StatusCompetition.objects.all())
    affiliation = serializers.PrimaryKeyRelatedField(queryset=Affiliation.objects.all())
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())

    class Meta:
        model = Competition
        fields = (
            'id', 'name', 'description', 'competition_type', 'status',
            'affiliation', 'location', 'start_date', 'end_date', 'slug',
        )
