from rest_framework import permissions

from .models import CompetitionAdmin


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )


class IsCompetitionAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return CompetitionAdmin.objects.filter(
            user=request.user,
            competition=obj.competition,
            is_active=True,
        ).exists()