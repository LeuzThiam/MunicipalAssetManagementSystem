from rest_framework import viewsets

from .models import Inspection
from .permissions import PermissionInspection
from .serializers import InspectionSerializer


class InspectionViewSet(viewsets.ModelViewSet):
    serializer_class = InspectionSerializer
    permission_classes = [PermissionInspection]
    http_method_names = ["get", "post", "patch", "head", "options"]
    filterset_fields = ["borne", "etat", "inspecteur"]
    ordering_fields = ["date_inspection", "date_creation"]

    def get_queryset(self):
        return Inspection.objects.select_related("borne", "inspecteur")

    def perform_create(self, serializer):
        serializer.save(inspecteur=self.request.user)
