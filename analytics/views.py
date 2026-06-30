from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
from datetime import timedelta

from fleet.models import Vehicle, FuelLog, Insurance
from drivers.models import Driver
from maintenance.models import MaintenanceSchedule
from journeys.models import PrimaryExpense


class AnalyticViewSet(ViewSet):

    # ----------------------------------
    # ✅ BASIC ANALYTICS (LIST)
    # ----------------------------------
    def list(self, request):
        total_vehicle_count = Vehicle.objects.count()
        total_driver_count = Driver.objects.count()

        status_counts = dict(
            Vehicle.objects.values("status").annotate(count=Count("id"))
            .values_list("status", "count")
        )

        return Response({
            "vehicle_count": total_vehicle_count,
            "driver_count": total_driver_count,
            "status_counts": status_counts
        })

    # ----------------------------------
    # 🚀 DASHBOARD (ADVANCED KPIs)
    # ----------------------------------
    @action(detail=False, methods=["get"], url_path="dashboard")
    def dashboard(self, request):

        # -------------------------------
        # 🔍 Filters
        # -------------------------------
        vehicle_type = request.GET.get("type")
        location = request.GET.get("location")
        department = request.GET.get("department")

        vehicles = Vehicle.objects.all()

        if vehicle_type:
            vehicles = vehicles.filter(type=vehicle_type)

        if location:
            vehicles = vehicles.filter(location__name=location)

        if department:
            vehicles = vehicles.filter(department__name=department)

        # -------------------------------
        # 🚗 Vehicle KPIs
        # -------------------------------
        total_vehicles = vehicles.count()

        status_counts = vehicles.values("status").annotate(count=Count("id"))
        status_map = {item["status"]: item["count"] for item in status_counts}

        available = status_map.get("AVAILABLE", 0)
        assigned = status_map.get("ASSIGNED", 0)
        maintenance = status_map.get("MAINTENANCE", 0)
        offroad = status_map.get("OFF_ROAD", 0)

        utilization = (assigned / total_vehicles * 100) if total_vehicles else 0

        # -------------------------------
        # ⛽ Fuel Cost Trend
        # -------------------------------
        fuel_trend = list(
            FuelLog.objects.annotate(
                month=TruncMonth("date")
            ).values("month").annotate(
                total_cost=Sum("fuel_cost")
            ).order_by("month")
        )

        # -------------------------------
        # 🔧 Maintenance Cost Trend
        # -------------------------------
        maintenance_trend = list(
            PrimaryExpense.objects.filter(type="maintenance")
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(total_cost=Sum("cost"))
            .order_by("month")
        )

        # -------------------------------
        # ⏰ Overdue Services
        # -------------------------------
        overdue_services = MaintenanceSchedule.objects.filter(
            next_service_date__lt=now().date()
        ).count()

        # -------------------------------
        # 📄 Expiring Documents
        # -------------------------------
        today = now().date()
        threshold = today + timedelta(days=30)

        expiring_insurance = Insurance.objects.filter(
            expiry_date__lte=threshold
        ).count()

        # -------------------------------
        # 📊 Final Response
        # -------------------------------
        return Response({
            "vehicles": {
                "total": total_vehicles,
                "available": available,
                "assigned": assigned,
                "maintenance": maintenance,
                "offroad": offroad,
                "utilization_percentage": round(utilization, 2),
            },
            "fuel_trend": fuel_trend,
            "maintenance_trend": maintenance_trend,
            "alerts": {
                "overdue_services": overdue_services,
                "expiring_insurance": expiring_insurance,
            }
        })