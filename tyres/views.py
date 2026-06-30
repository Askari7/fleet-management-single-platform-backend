import csv
import io
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone

from .models import Tyre, TyreHistory
from .serializers import TyreSerializer, TyreListSerializer, TyreHistorySerializer


class TyreViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Tyre.objects.select_related("current_vehicle").all()
        status_filter = self.request.query_params.get("status")
        brand = self.request.query_params.get("brand")
        vehicle_id = self.request.query_params.get("vehicle_id")
        if status_filter:
            qs = qs.filter(status=status_filter)
        if brand:
            qs = qs.filter(brand__icontains=brand)
        if vehicle_id:
            qs = qs.filter(current_vehicle_id=vehicle_id)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return TyreListSerializer
        return TyreSerializer

    @action(detail=True, methods=["post"], url_path="install")
    def install(self, request, pk=None):
        """Mount a tyre onto a vehicle at a position."""
        tyre = self.get_object()
        if tyre.status == "SCRAPPED":
            return Response({"detail": "Cannot install a scrapped tyre."}, status=400)
        if tyre.status == "MOUNTED":
            return Response({"detail": "Tyre is already mounted."}, status=400)

        vehicle_id = request.data.get("vehicle_id")
        position = request.data.get("position")
        install_odometer = request.data.get("install_odometer", 0)
        install_date = request.data.get("install_date", timezone.now().date())

        if not vehicle_id or not position:
            return Response({"detail": "vehicle_id and position are required."}, status=400)

        with transaction.atomic():
            TyreHistory.objects.create(
                tyre=tyre,
                vehicle_id=vehicle_id,
                position=position,
                install_date=install_date,
                install_odometer=install_odometer,
            )
            tyre.current_vehicle_id = vehicle_id
            tyre.current_position = position
            tyre.status = "MOUNTED"
            tyre.save()

        return Response(TyreSerializer(tyre).data)

    @action(detail=True, methods=["post"], url_path="remove")
    def remove(self, request, pk=None):
        """Remove a tyre from its current vehicle."""
        tyre = self.get_object()
        if tyre.status != "MOUNTED":
            return Response({"detail": "Tyre is not currently mounted."}, status=400)

        remove_odometer = request.data.get("remove_odometer", 0)
        remove_date = request.data.get("remove_date", timezone.now().date())
        scrap = request.data.get("scrap", False)

        with transaction.atomic():
            active_history = tyre.history.filter(remove_date__isnull=True).last()
            if active_history:
                active_history.remove_date = remove_date
                active_history.remove_odometer = remove_odometer
                active_history.save()
                km = active_history.km_gained
                tyre.total_km_run += km

            tyre.current_vehicle = None
            tyre.current_position = "STORE"
            tyre.status = "SCRAPPED" if scrap else "STOCK"
            tyre.save()

        return Response(TyreSerializer(tyre).data)

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        qs = Tyre.objects.all()
        return Response({
            "total": qs.count(),
            "mounted": qs.filter(status="MOUNTED").count(),
            "in_stock": qs.filter(status="STOCK").count(),
            "scrapped": qs.filter(status="SCRAPPED").count(),
        })

    @action(detail=False, methods=["post"], url_path="bulk-upload")
    def bulk_upload(self, request):
        """
        POST /tyres/api/tyre/bulk-upload/
        Upload a CSV to create tyres in bulk.
        Required columns: serial_number, brand, model, purchased_date, cost
        Optional: vehicle_registration (resolved to current_vehicle PK),
                  current_position, status
        """
        from fleet.models import Vehicle

        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded = file.read().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(decoded))
        except Exception as e:
            return Response({"detail": f"Could not parse file: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        created_count = 0
        errors = []

        for i, row in enumerate(reader, start=2):
            row = {k.strip(): v.strip() for k, v in row.items() if k}

            # Resolve vehicle_registration → current_vehicle PK
            registration = row.pop("vehicle_registration", None)
            if registration:
                try:
                    vehicle = Vehicle.objects.get(registration_number=registration)
                    row["current_vehicle"] = vehicle.pk
                except Vehicle.DoesNotExist:
                    errors.append({"row": i, "errors": {"vehicle_registration": [f"Vehicle '{registration}' not found."]}})
                    continue
            else:
                row.pop("current_vehicle", None)

            serializer = TyreSerializer(data=row)
            if serializer.is_valid():
                serializer.save()
                created_count += 1
            else:
                errors.append({"row": i, "errors": serializer.errors})

        return Response({"created": created_count, "errors": errors}, status=status.HTTP_200_OK)


class TyreHistoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TyreHistorySerializer

    def get_queryset(self):
        tyre_id = self.kwargs.get("tyre_pk")
        if tyre_id:
            return TyreHistory.objects.filter(tyre_id=tyre_id).select_related("vehicle")
        return TyreHistory.objects.select_related("tyre", "vehicle").all()
