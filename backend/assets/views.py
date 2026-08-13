from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .filters import BatimentFiltre, BorneFiltre, SegmentRueFiltre
from .models import Batiment, Borne, SegmentRue
from .permissions import PermissionBorne
from .serializers import BatimentSerializer, BorneSerializer, SegmentRueSerializer


class BorneViewSet(viewsets.ModelViewSet):
    queryset = Borne.objects.all()
    serializer_class = BorneSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]
    permission_classes = [IsAuthenticated, PermissionBorne]
    filterset_class = BorneFiltre
    search_fields = ["identifiant_source"]
    ordering_fields = ["pression_dynamique", "date_entretien"]


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