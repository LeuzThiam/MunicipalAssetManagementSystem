from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


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