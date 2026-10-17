from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


MESSAGES_PAR_STATUT = {
    status.HTTP_400_BAD_REQUEST: "La requête est invalide.",
    status.HTTP_401_UNAUTHORIZED: "Authentification requise ou invalide.",
    status.HTTP_403_FORBIDDEN: "Vous n'avez pas l'autorisation d'effectuer cette action.",
    status.HTTP_404_NOT_FOUND: "La ressource demandée est introuvable.",
    status.HTTP_405_METHOD_NOT_ALLOWED: "Cette méthode n'est pas autorisée.",
    status.HTTP_429_TOO_MANY_REQUESTS: "Trop de requêtes ont été envoyées. Réessayez plus tard.",
}


def gestionnaire_exceptions(exc, context):
    """Normalise le format des erreurs renvoyees par l'API DRF au format
    {"code": ..., "message": ...} (avec "erreurs" en plus pour le detail
    champ par champ des erreurs de validation).
    """
    reponse = exception_handler(exc, context)

    if reponse is None:
        return Response(
            {
                "code": "ErreurInterne",
                "message": "Une erreur interne est survenue. Réessayez plus tard.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    code = exc.__class__.__name__

    if isinstance(reponse.data, dict) and "detail" in reponse.data:
        reponse.data = {
            "code": code,
            "message": MESSAGES_PAR_STATUT.get(
                reponse.status_code,
                str(reponse.data["detail"]),
            ),
        }
    else:
        reponse.data = {
            "code": code,
            "message": "Erreur de validation.",
            "erreurs": reponse.data,
        }

    return reponse
