# drivers/views.py

import csv
import io
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drivers.models import Driver
from .serializers import DriverSerializer


class DriverViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Drivers. Supports list, retrieve, create, update, delete.
    """
    queryset = Driver.objects.all().order_by("-created_at")
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset

    @action(detail=False, methods=["post"], url_path="bulk-upload")
    def bulk_upload(self, request):
        """
        POST /drivers/api/driver/bulk-upload/
        Upload a CSV file to create drivers in bulk.
        Required columns: username (driver user account), email
        Optional: name, phone_number, address, cnic_number, rfid_tag, dob,
                  license_number, license_type, license_expiry, is_available, status, performance_score
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

            # Resolve contractor_username → user PK
            contractor_username = row.pop("contractor_username", None)
            if contractor_username:
                try:
                    user = UserModel.objects.get(username=contractor_username, role="contractor")
                    row["user"] = user.pk
                except UserModel.DoesNotExist:
                    errors.append({"row": i, "errors": {"contractor_username": [f"Contractor '{contractor_username}' not found."]}})
                    continue

            serializer = DriverSerializer(data=row)
            if serializer.is_valid():
                serializer.save()
                created_count += 1
            else:
                errors.append({"row": i, "errors": serializer.errors})

        return Response({"created": created_count, "errors": errors}, status=status.HTTP_200_OK)