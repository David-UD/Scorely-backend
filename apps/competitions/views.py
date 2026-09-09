from rest_framework import viewsets

from .models import Affiliation, Competition, CompetitionEdition, CompetitionType, Location
from .serializers import (
    AffiliationSerializer,
    CompetitionEditionSerializer,
    CompetitionEditionWriteSerializer,
    CompetitionSerializer,
    CompetitionTypeSerializer,
    CompetitionWriteSerializer,
    LocationSerializer,
)


class CompetitionTypeViewSet(viewsets.ModelViewSet):
    queryset = CompetitionType.objects.all()
    serializer_class = CompetitionTypeSerializer
    search_fields = ('code', 'name')


class AffiliationViewSet(viewsets.ModelViewSet):
    queryset = Affiliation.objects.all()
    serializer_class = AffiliationSerializer
    search_fields = ('name',)
    filterset_fields = ('city', 'state', 'country')


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    search_fields = ('name',)
    filterset_fields = ('city', 'state', 'country')


class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    search_fields = ('name',)
    filterset_fields = ('competition_type',)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CompetitionWriteSerializer
        return CompetitionSerializer


class CompetitionEditionViewSet(viewsets.ModelViewSet):
    queryset = CompetitionEdition.objects.all()
    serializer_class = CompetitionEditionSerializer
    filterset_fields = ('status', 'year')
    search_fields = ('competition__name',)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CompetitionEditionWriteSerializer
        return CompetitionEditionSerializer
