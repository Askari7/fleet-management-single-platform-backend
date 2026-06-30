from rest_framework import serializers
from .models import Tyre, TyreHistory


class TyreHistorySerializer(serializers.ModelSerializer):
    km_gained = serializers.ReadOnlyField()
    vehicle_name = serializers.SerializerMethodField()

    class Meta:
        model = TyreHistory
        fields = [
            "id", "tyre", "vehicle", "vehicle_name", "position",
            "install_date", "install_odometer",
            "remove_date", "remove_odometer", "km_gained",
        ]
        read_only_fields = ["id", "km_gained"]

    def get_vehicle_name(self, obj):
        return str(obj.vehicle) if obj.vehicle else None


class TyreSerializer(serializers.ModelSerializer):
    history = TyreHistorySerializer(many=True, read_only=True)
    vehicle_name = serializers.SerializerMethodField()
    cost_per_km = serializers.SerializerMethodField()

    class Meta:
        model = Tyre
        fields = [
            "id", "serial_number", "brand", "model",
            "purchased_date", "cost",
            "current_vehicle", "vehicle_name",
            "current_position", "status",
            "total_km_run", "cost_per_km",
            "history",
        ]
        read_only_fields = ["id", "total_km_run"]

    def get_vehicle_name(self, obj):
        return str(obj.current_vehicle) if obj.current_vehicle else None

    def get_cost_per_km(self, obj):
        if obj.total_km_run and obj.total_km_run > 0:
            return round(float(obj.cost) / obj.total_km_run, 4)
        return None


class TyreListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view — no nested history."""
    vehicle_name = serializers.SerializerMethodField()
    cost_per_km = serializers.SerializerMethodField()

    class Meta:
        model = Tyre
        fields = [
            "id", "serial_number", "brand", "model",
            "purchased_date", "cost",
            "current_vehicle", "vehicle_name",
            "current_position", "status", "total_km_run", "cost_per_km",
        ]

    def get_vehicle_name(self, obj):
        return str(obj.current_vehicle) if obj.current_vehicle else None

    def get_cost_per_km(self, obj):
        if obj.total_km_run and obj.total_km_run > 0:
            return round(float(obj.cost) / obj.total_km_run, 4)
        return None
