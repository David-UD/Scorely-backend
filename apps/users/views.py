from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CompetitionAdmin, User
from .permissions import IsSuperAdmin
from .serializers import (
    CompetitionAdminSerializer,
    UserCreateSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSuperAdmin,)
    search_fields = ('email', 'first_name', 'last_name')
    ordering_fields = ('email', 'created_at')
    filterset_fields = ('is_active',)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer


class CurrentUserView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class CompetitionAdminViewSet(viewsets.ModelViewSet):
    queryset = CompetitionAdmin.objects.all()
    serializer_class = CompetitionAdminSerializer
    filterset_fields = ('user', 'competition', 'is_active')

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsSuperAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = CompetitionAdmin.objects.all()
        if user.is_authenticated and not user.is_superuser:
            queryset = queryset.filter(user=user)
        return queryset
