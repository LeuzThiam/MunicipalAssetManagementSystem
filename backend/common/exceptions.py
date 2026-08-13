from rest_framework.views import exception_handler


def gestionnaire_exceptions(exc, context):
    """Normalise le format des erreurs renvoyees par l'API DRF au format
    {"code": ..., "message": ...} (avec "erreurs" en plus pour le detail
    champ par champ des erreurs de validation).
    """
    reponse = exception_handler(exc, context)

    if reponse is None:
        return reponse

    code = exc.__class__.__name__

    if isinstance(reponse.data, dict) and "detail" in reponse.data:
        reponse.data = {
            "code": code,
            "message": str(reponse.data["detail"]),
        }
    else:
        reponse.data = {
            "code": code,
            "message": "Erreur de validation.",
            "erreurs": reponse.data,
        }

    return reponse