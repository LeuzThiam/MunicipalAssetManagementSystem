import math

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.measure import D
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import BatimentFiltre, BorneFiltre, SegmentRueFiltre
from .models import Batiment, Borne, SegmentRue
from .permissions import PermissionBorne
from .serializers import (
    BatimentAvecDistanceSerializer,
    BatimentSerializer,
    BorneAvecDistanceSerializer,
    BorneSerializer,
    SegmentRueSerializer,
)


RAYON_MAX_METRES = 50_000


def convertir_nombre(parametres, nom, *, obligatoire=True, valeur_par_defaut=None):
    """Lit un nombre decimal dans les parametres de requete.

    Cette fonction centralise la validation afin que toutes les actions
    geospatiales retournent une erreur HTTP 400 coherente au lieu d'une
    erreur serveur lorsqu'un utilisateur envoie une valeur incorrecte.
    """
    valeur = parametres.get(nom, valeur_par_defaut)
    if valeur is None:
        if obligatoire:
            raise ValidationError({nom: "Ce parametre est requis."})
        return None

    try:
        nombre = float(valeur)
    except (TypeError, ValueError):
        raise ValidationError({nom: "Ce parametre doit etre un nombre."})

    if not math.isfinite(nombre):
        raise ValidationError({nom: "Ce parametre doit etre un nombre fini."})

    return nombre


def lire_point(parametres):
    """Construit un point WGS84 apres validation de lat et lng."""
    latitude = convertir_nombre(parametres, "lat")
    longitude = convertir_nombre(parametres, "lng")

    if not -90 <= latitude <= 90:
        raise ValidationError({"lat": "La latitude doit etre comprise entre -90 et 90."})
    if not -180 <= longitude <= 180:
        raise ValidationError({"lng": "La longitude doit etre comprise entre -180 et 180."})

    return Point(longitude, latitude, srid=4326)


def lire_rayon(parametres, valeur_par_defaut):
    """Valide un rayon positif et limite le cout de la requete spatiale."""
    rayon = convertir_nombre(
        parametres,
        "rayon",
        obligatoire=False,
        valeur_par_defaut=valeur_par_defaut,
    )
    if rayon <= 0:
        raise ValidationError({"rayon": "Le rayon doit etre superieur a zero."})
    if rayon > RAYON_MAX_METRES:
        raise ValidationError({
            "rayon": f"Le rayon ne peut pas depasser {RAYON_MAX_METRES} metres."
        })
    return rayon


def lire_bbox(parametres):
    """Valide une emprise WGS84 et retourne le polygone correspondant."""
    valeur = parametres.get("bbox")
    if not valeur:
        raise ValidationError({
            "bbox": "Ce parametre est requis au format minx,miny,maxx,maxy."
        })

    morceaux = valeur.split(",")
    if len(morceaux) != 4:
        raise ValidationError({
            "bbox": "Ce parametre doit contenir exactement quatre nombres."
        })

    try:
        minx, miny, maxx, maxy = (float(morceau) for morceau in morceaux)
    except ValueError:
        raise ValidationError({"bbox": "Ce parametre doit contenir quatre nombres."})

    if not all(math.isfinite(nombre) for nombre in (minx, miny, maxx, maxy)):
        raise ValidationError({"bbox": "Les quatre nombres doivent etre finis."})
    if not (-180 <= minx < maxx <= 180):
        raise ValidationError({
            "bbox": "Les longitudes doivent respecter -180 <= minx < maxx <= 180."
        })
    if not (-90 <= miny < maxy <= 90):
        raise ValidationError({
            "bbox": "Les latitudes doivent respecter -90 <= miny < maxy <= 90."
        })

    zone = Polygon.from_bbox((minx, miny, maxx, maxy))
    zone.srid = 4326
    return zone


class BorneViewSet(viewsets.ModelViewSet):
    queryset = Borne.objects.all()
    serializer_class = BorneSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]
    permission_classes = [IsAuthenticated, PermissionBorne]
    filterset_class = BorneFiltre
    search_fields = ["identifiant_source"]
    ordering_fields = ["pression_dynamique", "date_entretien"]

    @action(detail=False, methods=["get"])
    def carte(self, request):
        """GET /api/bornes/carte/?bbox=minx,miny,maxx,maxy"""
        zone = lire_bbox(request.query_params)

        queryset = self.filter_queryset(self.get_queryset().filter(geometrie__intersects=zone))
        if not queryset.ordered:
            queryset = queryset.order_by("pk")
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=["get"])
    def proches(self, request):
        """GET /api/bornes/proches/?lat=...&lng=...&rayon=500"""
        point = lire_point(request.query_params)
        rayon = lire_rayon(request.query_params, valeur_par_defaut=500)
        queryset = self.filter_queryset(
            self.get_queryset()
            .filter(geometrie__dwithin=(point, D(m=rayon)))
            .annotate(distance=Distance("geometrie", point))
            .order_by("distance")
        )
        page = self.paginate_queryset(queryset)
        serializer = BorneAvecDistanceSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["get"], url_path="batiments-proches")
    def batiments_proches(self, request, pk=None):
        """GET /api/bornes/{id}/batiments-proches/?rayon=200"""
        borne = self.get_object()
        rayon = lire_rayon(request.query_params, valeur_par_defaut=200)

        batiments = (
            Batiment.objects.filter(geometrie__dwithin=(borne.geometrie, D(m=rayon)))
            .annotate(distance=Distance("geometrie", borne.geometrie))
            .order_by("distance")
        )
        page = self.paginate_queryset(batiments)
        serializer = BatimentAvecDistanceSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["get"], url_path="rue-la-plus-proche")
    def rue_la_plus_proche(self, request, pk=None):
        """GET /api/bornes/{id}/rue-la-plus-proche/"""
        borne = self.get_object()

        segment = (
            SegmentRue.objects.annotate(distance=Distance("geometrie", borne.geometrie))
            .order_by("distance")
            .first()
        )

        if segment is None:
            raise NotFound("Aucun segment de rue trouve.")

        return Response({
            "rue": segment.nom,
            "distance_metres": segment.distance.m,
        })


class BatimentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Batiment.objects.all()
    serializer_class = BatimentSerializer
    filterset_class = BatimentFiltre
    search_fields = ["nom", "adresse"]
    ordering_fields = ["superficie", "nom"]


class SegmentRueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SegmentRue.objects.all()
    serializer_class = SegmentRueSerializer
    filterset_class = SegmentRueFiltre
    search_fields = ["nom"]
    ordering_fields = ["limite_vitesse", "nom"]
