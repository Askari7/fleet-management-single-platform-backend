from rest_framework import serializers
from .models import Vendor, SparePart, SparePartConsumption, PurchaseHistory


# ---------------- Vendor ----------------
class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"


# ---------------- Spare Part ----------------
class SparePartSerializer(serializers.ModelSerializer):
    vendor_name = serializers.ReadOnlyField(source="vendor.name")
    is_below_threshold = serializers.SerializerMethodField()

    class Meta:
        model = SparePart
        fields = "__all__"

    def get_is_below_threshold(self, obj):
        return obj.is_below_threshold()


# ---------------- Spare Part Consumption ----------------
class SparePartConsumptionSerializer(serializers.ModelSerializer):
    spare_part_name = serializers.ReadOnlyField(source="spare_part.name")
    vehicle_name = serializers.ReadOnlyField(source="vehicle.name")

    class Meta:
        model = SparePartConsumption
        fields = "__all__"


# ---------------- Purchase History ----------------
class PurchaseHistorySerializer(serializers.ModelSerializer):
    spare_part_name = serializers.ReadOnlyField(source="spare_part.name")
    vendor_name = serializers.ReadOnlyField(source="vendor.name")

    class Meta:
        model = PurchaseHistory
        fields = "__all__"

class SparePartDetailSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer(read_only=True)
    consumption_history = SparePartConsumptionSerializer(
        source="sparepartconsumption_set", many=True, read_only=True
    )
    purchase_history = PurchaseHistorySerializer(
        source="purchasehistory_set", many=True, read_only=True
    )

    class Meta:
        model = SparePart
        fields = "__all__"