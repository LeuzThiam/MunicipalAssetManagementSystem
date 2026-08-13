from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import Batiment, Borne, SegmentRue


class BorneSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Borne
        geo_field = "geometrie"
        fields = "__all__"


class BatimentSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Batiment
        geo_field = "geometrie"
        fields = "__all__"


class SegmentRueSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = SegmentRue
        geo_field = "geometrie"
        fields = "__all__"