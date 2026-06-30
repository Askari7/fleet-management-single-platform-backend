from rest_framework import viewsets
from .models import Vendor, SparePart, SparePartConsumption, PurchaseHistory
from .serializers import (
    VendorSerializer,
    SparePartSerializer,
    SparePartDetailSerializer,
    SparePartConsumptionSerializer,
    PurchaseHistorySerializer
)


# ---------------- Vendor ----------------
class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer


# ---------------- Spare Part ----------------
class SparePartViewSet(viewsets.ModelViewSet):
    queryset = SparePart.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SparePartDetailSerializer  # detailed view
        return SparePartSerializer


# ---------------- Spare Part Consumption ----------------
class SparePartConsumptionViewSet(viewsets.ModelViewSet):
    queryset = SparePartConsumption.objects.all().order_by("-date_used")
    serializer_class = SparePartConsumptionSerializer


# ---------------- Purchase History ----------------
class PurchaseHistoryViewSet(viewsets.ModelViewSet):
    queryset = PurchaseHistory.objects.all().order_by("-purchase_date")
    serializer_class = PurchaseHistorySerializer