from rest_framework import viewsets

from .models import CompetitionEditionAdmin, Role, User
from .serializers import (
    CompetitionEditionAdminSerializer,
    RoleSerializer,
    UserCreateSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    search_fields = ('email', 'first_name', 'last_name')
    ordering_fields = ('email', 'created_at')
    filterset_fields = ('role', 'is_active')

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class CompetitionEditionAdminViewSet(viewsets.ModelViewSet):
    queryset = CompetitionEditionAdmin.objects.all()
    serializer_class = CompetitionEditionAdminSerializer
