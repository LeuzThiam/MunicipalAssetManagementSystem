from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Utilisateur
from .serializers import UtilisateurSerializer


class EstAdministrateur(IsAuthenticated):
    """Réserve l'administration des comptes aux administrateurs actifs."""

    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and request.user.role == Utilisateur.Role.ADMIN
        )


class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.order_by("nom", "prenom", "email")
    serializer_class = UtilisateurSerializer
    permission_classes = [EstAdministrateur]
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["role", "is_active"]
    search_fields = ["email", "prenom", "nom"]

    def perform_update(self, serializer):
        if (
            serializer.instance == self.request.user
            and serializer.validated_data.get("is_active") is False
        ):
            raise ValidationError("Vous ne pouvez pas désactiver votre propre compte.")
        serializer.save()


class UtilisateurCourantView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        utilisateur = request.user
        return Response({
            "id": utilisateur.id,
            "email": utilisateur.email,
            "prenom": utilisateur.prenom,
            "nom": utilisateur.nom,
            "role": utilisateur.role,
        })


class DeconnexionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        jeton_rafraichissement = request.data.get("refresh")
        if not jeton_rafraichissement:
            raise ValidationError("Le jeton de rafraichissement est requis.")

        RefreshToken(jeton_rafraichissement).blacklist()
        return Response(status=205)
