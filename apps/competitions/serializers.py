from rest_framework import serializers

from .models import Affiliation, Competition, CompetitionEdition, CompetitionType, Location


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


class CompetitionSerializer(serializers.ModelSerializer):
    competition_type = CompetitionTypeSerializer(read_only=True)
    affiliation = AffiliationSerializer(read_only=True)
    location = LocationSerializer(read_only=True)

    class Meta:
        model = Competition
        fields = ('id', 'competition_type', 'affiliation', 'location', 'name', 'description')


class CompetitionWriteSerializer(serializers.ModelSerializer):
    competition_type = serializers.PrimaryKeyRelatedField(queryset=CompetitionType.objects.all())
    affiliation = serializers.PrimaryKeyRelatedField(queryset=Affiliation.objects.all())
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())

    class Meta:
        model = Competition
        fields = ('id', 'competition_type', 'affiliation', 'location', 'name', 'description')


class CompetitionEditionSerializer(serializers.ModelSerializer):
    competition = CompetitionSerializer(read_only=True)

    class Meta:
        model = CompetitionEdition
        fields = ('id', 'competition', 'year', 'start_date', 'end_date', 'status')


class CompetitionEditionWriteSerializer(serializers.ModelSerializer):
    competition = serializers.PrimaryKeyRelatedField(queryset=Competition.objects.all())

    class Meta:
        model = CompetitionEdition
        fields = ('id', 'competition', 'year', 'start_date', 'end_date', 'status')