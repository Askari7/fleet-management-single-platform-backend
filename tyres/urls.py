from rest_framework_nested import routers
from django.urls import path, include
from .views import TyreViewSet, TyreHistoryViewSet

router = routers.DefaultRouter()
router.register(r"tyre", TyreViewSet, basename="tyre")

tyre_router = routers.NestedDefaultRouter(router, r"tyre", lookup="tyre")
tyre_router.register(r"history", TyreHistoryViewSet, basename="tyre-history")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(tyre_router.urls)),
]
