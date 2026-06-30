from rest_framework.routers import DefaultRouter
from .views import AnalyticViewSet

router = DefaultRouter()
router.register(r"analytic", AnalyticViewSet, basename="analytic")

urlpatterns = router.urls