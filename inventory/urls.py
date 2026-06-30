from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (
    VendorViewSet,
    SparePartViewSet,
    SparePartConsumptionViewSet,
    PurchaseHistoryViewSet,
)

router = DefaultRouter()

# Inventory APIs
router.register(r'vendors', VendorViewSet, basename='vendors')
router.register(r'spare-parts', SparePartViewSet, basename='spare-parts')
router.register(r'consumptions', SparePartConsumptionViewSet, basename='consumptions')
router.register(r'purchases', PurchaseHistoryViewSet, basename='purchases')

urlpatterns = [
    path('', include(router.urls)),
]