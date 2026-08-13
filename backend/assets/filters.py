import django_filters

from .models import Batiment, Borne, SegmentRue


class BorneFiltre(django_filters.FilterSet):
    entretien_manquant = django_filters.BooleanFilter(
        field_name="date_entretien", lookup_expr="isnull"
    )
    pression_min = django_filters.NumberFilter(
        field_name="pression_dynamique", lookup_expr="gte"
    )
    pression_max = django_filters.NumberFilter(
        field_name="pression_dynamique", lookup_expr="lte"
    )

    class Meta:
        model = Borne
        fields = ["identifiant_source", "municipalite"]


class BatimentFiltre(django_filters.FilterSet):
    adresse = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Batiment
        fields = ["usage", "adresse"]


class SegmentRueFiltre(django_filters.FilterSet):
    nom = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = SegmentRue
        fields = ["nom", "limite_vitesse", "statut", "autobus_autorise"]