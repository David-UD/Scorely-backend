from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.users.permissions import IsCompetitionAdmin

from .models import Affiliation, Competition, CompetitionType, Location, StatusCompetition
from .serializers import (
    AffiliationSerializer,
    CompetitionSerializer,
    CompetitionTypeSerializer,
    CompetitionWriteSerializer,
    LocationSerializer,
    StatusCompetitionSerializer,
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


class StatusCompetitionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StatusCompetition.objects.all()
    serializer_class = StatusCompetitionSerializer
    search_fields = ('code', 'name')


class CompetitionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, IsCompetitionAdmin)
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    search_fields = ('name',)
    filterset_fields = ('competition_type', 'status')

    def get_queryset(self):
        queryset = self.queryset.all()
        user = self.request.user
        if user.is_authenticated and not user.is_superuser:
            queryset = queryset.filter(
                admins__user=user,
                admins__is_active=True,
            ).distinct()
        return queryset

    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied('Solo el superusuario puede crear competiciones.')
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied('Solo el superusuario puede eliminar competiciones.')
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CompetitionWriteSerializer
        return CompetitionSerializer

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_value = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)
        if lookup_value is None:
            return super().get_object()
        try:
            int(lookup_value)
        except (TypeError, ValueError):
            obj = get_object_or_404(queryset, slug=lookup_value)
        else:
            obj = get_object_or_404(queryset, pk=lookup_value)
        self.check_object_permissions(self.request, obj)
        return obj
