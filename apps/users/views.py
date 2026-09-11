from rest_framework import viewsets

from .models import CompetitionAdmin, User
from .serializers import (
    CompetitionAdminSerializer,
    UserCreateSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    search_fields = ('email', 'first_name', 'last_name')
    ordering_fields = ('email', 'created_at')
    filterset_fields = ('is_active',)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer


class CompetitionAdminViewSet(viewsets.ModelViewSet):
    queryset = CompetitionAdmin.objects.all()
    serializer_class = CompetitionAdminSerializer
    filterset_fields = ('user', 'competition', 'is_active')
