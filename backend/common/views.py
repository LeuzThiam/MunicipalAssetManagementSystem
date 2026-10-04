from datetime import date

from django.db.models import Avg, Count, Q
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from assets.models import Batiment, Borne, SegmentRue
from inspections.models import Inspection
from interventions.models import Intervention


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})


def _premier_jour_mois_suivant(jour):
    if jour.month == 12:
        return date(jour.year + 1, 1, 1)
    return date(jour.year, jour.month + 1, 1)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def tableau_de_bord(request):
    aujourd_hui = timezone.localdate()
    debut_mois = aujourd_hui.replace(day=1)
    fin_mois = _premier_jour_mois_suivant(aujourd_hui)
    stats_bornes = Borne.objects.aggregate(
        total=Count("id"),
        sans_entretien=Count("id", filter=Q(date_entretien__isnull=True)),
        pression_moyenne=Avg("pression_dynamique"),
    )
    statuts_actifs = [
        Intervention.Statut.OUVERTE,
        Intervention.Statut.PLANIFIEE,
        Intervention.Statut.EN_COURS,
    ]

    return Response({
        "bornes_total": stats_bornes["total"],
        "batiments_total": Batiment.objects.count(),
        "segments_rue_total": SegmentRue.objects.count(),
        "bornes_sans_entretien": stats_bornes["sans_entretien"],
        "pression_moyenne": round(stats_bornes["pression_moyenne"], 1) if stats_bornes["pression_moyenne"] is not None else None,
        "interventions_ouvertes": Intervention.objects.filter(statut__in=statuts_actifs).count(),
        "inspections_ce_mois": Inspection.objects.filter(
            date_inspection__gte=debut_mois,
            date_inspection__lt=fin_mois,
        ).count(),
        "interventions_par_statut": list(
            Intervention.objects.values("statut").annotate(total=Count("id")).order_by("statut")
        ),
        "inspections_par_etat": list(
            Inspection.objects.values("etat").annotate(total=Count("id")).order_by("etat")
        ),
    })
