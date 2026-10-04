from rest_framework import viewsets

from .models import Intervention
from .permissions import PermissionIntervention
from .serializers import InterventionSerializer


class InterventionViewSet(viewsets.ModelViewSet):
    serializer_class = InterventionSerializer
    permission_classes = [PermissionIntervention]
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["borne", "type", "priorite", "statut", "creee_par"]
    ordering_fields = ["planifiee_le", "date_creation", "priorite"]

    def get_queryset(self):
        return Intervention.objects.select_related("borne", "creee_par")

    def perform_create(self, serializer):
        serializer.save(creee_par=self.request.user)
