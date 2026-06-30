import csv
import io
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from fleet.models import Vehicle,Insurance,FuelLog
from devices.serializers import VehicleSerializer,InsuranceSerializer,FuelLogSerializer
from devices.models import (
   Driver,
    Event, Heartbeat, 
)
from fleet.models import Vehicle, VehicleOdometer,VehicleDeviceHistory, VehicleValue, Insurance, FuelLog, VehicleStatusHistory, VehicleLocation, VehicleAssignment, AssignmentHistory
from violations.models import Violation, ViolationAnnotation
from devices.serializers import (
    VehicleSerializer, InsuranceSerializer, FuelLogSerializer,
    VehicleOdometerSerializer, VehicleLocationSerializer,
    VehicleStatusHistorySerializer, VehicleValueSerializer,
    DriverSerializer, VehicleAssignmentSerializer,
    EventSerializer, HeartbeatSerializer, ViolationSerializer,
    ViolationAnnotationSerializer
)
from rest_framework.decorators import action

# views.py
class InsuranceViewSet(viewsets.ModelViewSet):
    serializer_class = InsuranceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        vehicle_id = self.kwargs.get("vehicle_pk")
        if vehicle_id:
            return Insurance.objects.filter(vehicle_id=vehicle_id)
        return Insurance.objects.all()

    def perform_create(self, serializer):
        vehicle_id = self.kwargs.get("vehicle_pk")
        vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
        serializer.save(vehicle=vehicle)


class FuelLogViewSet(viewsets.ModelViewSet):
    serializer_class = FuelLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        vehicle_id = self.kwargs.get("vehicle_pk")
        if vehicle_id:
            return FuelLog.objects.filter(vehicle_id=vehicle_id)
        return FuelLog.objects.all()

    def perform_create(self, serializer):
        vehicle_id = self.kwargs.get("vehicle_pk")
        vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
        serializer.save(vehicle=vehicle)

# ─── Vehicle Odometer ──────────────────────────────
class VehicleOdometerViewSet(viewsets.ModelViewSet):
    queryset = VehicleOdometer.objects.all().order_by("-reading_date")
    serializer_class = VehicleOdometerSerializer
    permission_classes = [IsAuthenticated]

# ─── Vehicle Location ──────────────────────────────
class VehicleLocationViewSet(viewsets.ModelViewSet):
    queryset = VehicleLocation.objects.all().order_by("-timestamp")
    serializer_class = VehicleLocationSerializer
    permission_classes = [IsAuthenticated]

# ─── Vehicle Status History ────────────────────────
class VehicleStatusHistoryViewSet(viewsets.ModelViewSet):
    queryset = VehicleStatusHistory.objects.all().order_by("-changed_at")
    serializer_class = VehicleStatusHistorySerializer
    permission_classes = [IsAuthenticated]

# ─── Vehicle Value ─────────────────────────────────
class VehicleValueViewSet(viewsets.ModelViewSet):
    queryset = VehicleValue.objects.all().order_by("-recorded_date")
    serializer_class = VehicleValueSerializer
    permission_classes = [IsAuthenticated]

# ─── Driver ───────────────────────────────────────
class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all().order_by("name")
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"], url_path="change-status")
    def change_status(self, request, pk=None):
        """
        Custom endpoint to manually change a driver's status.
        POST /<driver_id>/change-status/
        Body: { "status": "<new_status>" }
        """
        driver = self.get_object()
        new_status = request.data.get("status")

        if not new_status:
            return Response({"error": "status is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate status
        valid_statuses = [choice[0] for choice in Driver.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Must be one of {valid_statuses}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update driver status and availability
        driver.status = new_status
        driver.is_available = True if new_status == "active" else False
        driver.save()

        return Response(
            {"message": f"Driver status updated to '{new_status}' successfully."},
            status=status.HTTP_200_OK
        )

# ─── Vehicle Assignment ───────────────────────────
class VehicleAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        vehicle_id = self.kwargs.get("vehicle_pk")
        if vehicle_id:
            return VehicleAssignment.objects.filter(vehicle_id=vehicle_id).order_by("-assigned_on")
        return VehicleAssignment.objects.all().order_by("-assigned_on")

# ─── Event ────────────────────────────────────────
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by("-logged_at")
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

# ─── Heartbeat ───────────────────────────────────
class HeartbeatViewSet(viewsets.ModelViewSet):
    queryset = Heartbeat.objects.all().order_by("-logged_at")
    serializer_class = HeartbeatSerializer
    permission_classes = [IsAuthenticated]

# ─── Violation ───────────────────────────────────
class ViolationViewSet(viewsets.ModelViewSet):
    queryset = Violation.objects.all().order_by("-logged_at")
    serializer_class = ViolationSerializer
    permission_classes = [IsAuthenticated]

# ─── Violation Annotation ────────────────────────
class ViolationAnnotationViewSet(viewsets.ModelViewSet):
    queryset = ViolationAnnotation.objects.all().order_by("-created_at")
    serializer_class = ViolationAnnotationSerializer
    permission_classes = [IsAuthenticated]

from rest_framework.response import Response
from rest_framework import status

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all().order_by("-created_at")
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)

    @action(detail=True, methods=["post"], url_path="assign-driver")
    def assign_driver(self, request, pk=None):
        """
        POST /vehicle/<vehicle_id>/assign-driver/
        Body: { "driver_id": <driver_id> }
        """
        from django.utils import timezone as tz

        vehicle = self.get_object()
        driver_id = request.data.get("driver_id")

        if not driver_id:
            return Response({"error": "driver_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            driver = Driver.objects.get(pk=driver_id)
        except Driver.DoesNotExist:
            return Response({"error": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)

        if not driver.is_available or driver.status != "active":
            return Response({"error": "Driver is not available for assignment."}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent duplicate: vehicle already has an active assignment
        if VehicleAssignment.objects.filter(vehicle=vehicle, released_on__isnull=True).exists():
            return Response({"error": "Vehicle already has an active driver assignment."}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent duplicate: driver is already assigned to another vehicle
        if VehicleAssignment.objects.filter(driver=driver, released_on__isnull=True).exists():
            return Response({"error": "Driver is already assigned to another vehicle."}, status=status.HTTP_400_BAD_REQUEST)

        assignment = VehicleAssignment.objects.create(vehicle=vehicle, driver=driver)

        # Mirror to AssignmentHistory
        AssignmentHistory.objects.create(vehicle=vehicle, driver=driver)

        driver.is_available = False
        driver.save()

        serializer = VehicleAssignmentSerializer(assignment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="release-driver")
    def release_driver(self, request, pk=None):
        """
        POST /vehicle/<vehicle_id>/release-driver/
        Closes the active assignment and marks the driver available again.
        """
        from django.utils import timezone as tz

        vehicle = self.get_object()

        assignment = VehicleAssignment.objects.filter(vehicle=vehicle, released_on__isnull=True).first()
        if not assignment:
            return Response({"error": "No active driver assignment for this vehicle."}, status=status.HTTP_400_BAD_REQUEST)

        now = tz.now()
        assignment.released_on = now
        assignment.save()

        # Close the matching AssignmentHistory entry
        AssignmentHistory.objects.filter(
            vehicle=vehicle, driver=assignment.driver, end_time__isnull=True
        ).update(end_time=now)

        # Mark driver available
        assignment.driver.is_available = True
        assignment.driver.save()

        serializer = VehicleAssignmentSerializer(assignment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="bulk-upload")
    def bulk_upload(self, request):
        """
        POST /vehicles/api/vehicle/bulk-upload/
        Upload a CSV to create vehicles in bulk.
        Required columns: device, registration_number, username (contractor username)
        Optional: name, model_name, model_year, chassis_number, engine_number,
                  color, manufacturer, type, number_of_tyres
        """
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()

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

            # Resolve username → user_id (numeric PK)
            username = row.pop("username", None)
            if username:
                try:
                    user = UserModel.objects.get(username=username)
                    row["user_id"] = user.pk
                except UserModel.DoesNotExist:
                    errors.append({"row": i, "errors": {"username": [f"User '{username}' not found."]}})
                    continue
            elif "user_id" not in row:
                row["user_id"] = request.user.pk

            serializer = VehicleSerializer(data=row)
            if serializer.is_valid():
                serializer.save()
                created_count += 1
            else:
                errors.append({"row": i, "errors": serializer.errors})

        return Response({"created": created_count, "errors": errors}, status=status.HTTP_200_OK)