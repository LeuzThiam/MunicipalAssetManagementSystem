from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health, name="health"),
    path("tableau-de-bord/", views.tableau_de_bord, name="tableau-de-bord"),
]
