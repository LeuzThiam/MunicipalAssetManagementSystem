from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.models import Utilisateur


class PermissionIntervention(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in (
            Utilisateur.Role.GESTIONNAIRE,
            Utilisateur.Role.ADMIN,
        )

    def has_object_permission(self, request, view, objet):
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in (
            Utilisateur.Role.GESTIONNAIRE,
            Utilisateur.Role.ADMIN,
        )
