from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import DeconnexionView, UtilisateurCourantView

urlpatterns = [
    path("connexion/", TokenObtainPairView.as_view(), name="connexion"),
    path("connexion/rafraichir/", TokenRefreshView.as_view(), name="connexion-rafraichir"),
    path("deconnexion/", DeconnexionView.as_view(), name="deconnexion"),
    path("utilisateur-courant/", UtilisateurCourantView.as_view(), name="utilisateur-courant"),
]