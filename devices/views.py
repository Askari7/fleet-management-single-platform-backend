import csv
import io
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from .models import Device
from fleet.models import VehicleDeviceHistory
from .serializers import DeviceSerializer, VehicleDeviceHistorySerializer
from rest_framework.viewsets import ReadOnlyModelViewSet


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all().order_by("-created_at")
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            return Response(
                {
                    "message": "Device created successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        except ValidationError as e:
            return Response(
                {
                    "message": "Validation failed",
                    "errors": e.detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        

    @action(detail=False, methods=["post"], url_path="bulk-upload")
    def bulk_upload(self, request):
        """
        POST /devices/api/device/bulk-upload/
        Upload a CSV to create devices in bulk.
        Required columns: uuid, type
        Optional: name, front_camera_url, rear_camera_url
        """
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
            serializer = DeviceSerializer(data=row)
            if serializer.is_valid():
                serializer.save()
                created_count += 1
            else:
                errors.append({"row": i, "errors": serializer.errors})

        return Response({"created": created_count, "errors": errors}, status=status.HTTP_200_OK)


class VehicleDeviceHistoryViewSet(ReadOnlyModelViewSet):
    queryset = VehicleDeviceHistory.objects.all().select_related('vehicle', 'device')
    serializer_class = VehicleDeviceHistorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        vehicle_id = self.request.query_params.get('vehicle_id')
        device_id = self.request.query_params.get('device_id')

        if vehicle_id:
            queryset = queryset.filter(vehicle_id=vehicle_id)

        if device_id:
            queryset = queryset.filter(device_id=device_id)

        return queryset.order_by('-assigned_at')