from rest_framework import permissions

from .models import CompetitionEditionAdmin


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role
            and request.user.role.code == 'SUPERADMIN'
        )


class IsEditionAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role and request.user.role.code == 'SUPERADMIN':
            return True
        return CompetitionEditionAdmin.objects.filter(
            user=request.user,
            competition_edition=obj.competition_edition,
        ).exists()
