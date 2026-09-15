from rest_framework import permissions

from .models import CompetitionAdmin


def visible_competitions_q(user):
    from apps.competitions.models import Competition

    if user and user.is_authenticated and user.is_superuser:
        return Competition.objects.all()
    if not user or not user.is_authenticated:
        return Competition.objects.all()
    return Competition.objects.filter(
        admins__user=user,
        admins__is_active=True,
    ).distinct()


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )


class IsCompetitionAdmin(permissions.BasePermission):
    def resolve_competition(self, obj):
        return getattr(obj, "competition", obj)

    def has_object_permission(self, request, view, obj):
        method = getattr(request, 'method', None)
        if method is not None and method in permissions.SAFE_METHODS:
            return True
        if request.user and request.user.is_authenticated and request.user.is_superuser:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        return CompetitionAdmin.objects.filter(
            user=request.user,
            competition=self.resolve_competition(obj),
            is_active=True,
        ).exists()