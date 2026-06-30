from rest_framework import serializers
from .models import Device
from fleet.models import Insurance, FuelLog
from fleet.models import Vehicle, VehicleDeviceHistory, VehicleValue
from fleet.models import Vehicle
from tyres.models import Tyre
from django.utils import timezone
from fleet.models import VehicleDeviceHistory
class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def validate_uuid(self, value):
        if Device.objects.filter(uuid=value).exists():
            raise serializers.ValidationError("Device with this UUID already exists.")
        return value

class TyreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tyre
        fields = ["id", "serial_number", "brand", "model", "current_position", "status", "total_km_run"]
        read_only_fields = ["id", "total_km_run"]


class VehicleSerializer(serializers.ModelSerializer):
    tyres = TyreSerializer(many=True, required=False)
    assigned_driver_id = serializers.SerializerMethodField()
    assigned_driver_name = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "device",
            "user_id",
            "name",
            "registration_number",
            "model_name",
            "model_year",
            "operational_warranty",
            "chassis_number",
            "engine_number",
            "color",
            "manufacturer",
            "type",
            "status",
            "number_of_tyres",
            "tyres",
            "assigned_driver_id",
            "assigned_driver_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_assigned_driver_id(self, obj):
        assignment = obj.assignments.filter(released_on__isnull=True).first()
        return assignment.driver_id if assignment else None

    def get_assigned_driver_name(self, obj):
        assignment = obj.assignments.filter(released_on__isnull=True).first()
        return assignment.driver.name if assignment else None

    def create(self, validated_data):
        tyres_data = validated_data.pop("tyres", [])
        device = validated_data.get("device")

        vehicle = Vehicle.objects.create(**validated_data)

        for tyre in tyres_data:
            Tyre.objects.create(current_vehicle=vehicle, **tyre)

        if device:
            VehicleDeviceHistory.objects.create(
                vehicle=vehicle,
                device=device,
                assigned_at=timezone.now()
            )

        return vehicle

    def update(self, instance, validated_data):
        old_device = instance.device
        new_device = validated_data.get("device", instance.device)

        instance = super().update(instance, validated_data)

        if old_device != new_device:
            VehicleDeviceHistory.objects.filter(
                vehicle=instance,
                removed_at__isnull=True
            ).update(removed_at=timezone.now())

            if new_device:
                VehicleDeviceHistory.objects.create(
                    vehicle=instance,
                    device=new_device,
                    assigned_at=timezone.now()
                )

        return instance

class VehicleDeviceHistorySerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    device = DeviceSerializer(read_only=True)

    class Meta:
        model = VehicleDeviceHistory
        fields = ['id', 'vehicle', 'device', 'assigned_at', 'removed_at']

# serializers.py
class InsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insurance
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class FuelLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelLog
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

from rest_framework import serializers
from .models import (
    Driver, Event, Heartbeat, 
)
from fleet.models import Vehicle, VehicleOdometer,VehicleDeviceHistory, VehicleValue, Insurance, FuelLog, VehicleStatusHistory, VehicleLocation, VehicleAssignment
from violations.models import Violation, ViolationAnnotation

class VehicleOdometerSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleOdometer
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

# ─── Vehicle Location ───────────────────────────────
class VehicleLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleLocation
        fields = "__all__"
        read_only_fields = ["id", "timestamp"]

# ─── Vehicle Status History ────────────────────────
class VehicleStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_user = serializers.StringRelatedField(source="changed_by", read_only=True)
    
    class Meta:
        model = VehicleStatusHistory
        fields = "__all__"
        read_only_fields = ["id", "changed_at"]

# ─── Vehicle Value ────────────────────────────────
class VehicleValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleValue
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

# ─── Driver ───────────────────────────────────────
class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

# serializers.py
from rest_framework import serializers
from fleet.models import VehicleAssignment

class VehicleAssignmentSerializer(serializers.ModelSerializer):
    assigned_to_id = serializers.IntegerField(source="driver.id")
    assigned_to_name = serializers.CharField(source="driver.name")
    from_date = serializers.DateTimeField(source="assigned_on")
    to_date = serializers.DateTimeField(source="released_on", allow_null=True)

    class Meta:
        model = VehicleAssignment
        fields = ["id", "assigned_to_id", "assigned_to_name", "from_date", "to_date", "created_at", "updated_at"]

# ─── Event ───────────────────────────────────────
class EventSerializer(serializers.ModelSerializer):
    device_name = serializers.StringRelatedField(source="device", read_only=True)
    
    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

# ─── Heartbeat ───────────────────────────────────
class HeartbeatSerializer(serializers.ModelSerializer):
    device_name = serializers.StringRelatedField(source="device", read_only=True)
    
    class Meta:
        model = Heartbeat
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

# ─── Violation ───────────────────────────────────
class ViolationSerializer(serializers.ModelSerializer):
    device_name = serializers.StringRelatedField(source="device", read_only=True)
    vehicle_name = serializers.StringRelatedField(source="vehicle", read_only=True)
    user_name = serializers.StringRelatedField(source="user", read_only=True)
    violation_type_name = serializers.StringRelatedField(source="violation_type_id", read_only=True)

    class Meta:
        model = Violation
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

# ─── Violation Annotation ────────────────────────
class ViolationAnnotationSerializer(serializers.ModelSerializer):
    annotated_by_user = serializers.StringRelatedField(source="annotated_by", read_only=True)
    violation_info = serializers.StringRelatedField(source="violation", read_only=True)
    
    class Meta:
        model = ViolationAnnotation
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]