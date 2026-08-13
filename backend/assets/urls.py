from rest_framework.routers import DefaultRouter

from .views import BatimentViewSet, BorneViewSet, SegmentRueViewSet

router = DefaultRouter()
router.register("bornes", BorneViewSet, basename="borne")
router.register("batiments", BatimentViewSet, basename="batiment")
router.register("segments-rue", SegmentRueViewSet, basename="segmentrue")

urlpatterns = router.urls