from rest_framework import viewsets
from .models import Maintenance
from .serializers import MaintenanceSerializer

class MaintenanceViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD for Maintenance with nested VehicleIssues and WorkOrders.
    """
    queryset = Maintenance.objects.all().order_by('-created_at')
    serializer_class = MaintenanceSerializer