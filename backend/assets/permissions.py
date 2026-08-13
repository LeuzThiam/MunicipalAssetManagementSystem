from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.models import Utilisateur


class PermissionBorne(BasePermission):
    """Lecture ouverte a tout utilisateur authentifie, ecriture (creation,
    modification) reservee aux gestionnaires et administrateurs.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user.role in (
            Utilisateur.Role.GESTIONNAIRE,
            Utilisateur.Role.ADMIN,
        )