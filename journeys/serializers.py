from rest_framework import serializers
from .models import Journey, PrimaryExpense, SecondaryExpense
from accounts.serializers import UserSerializer
from accounts.models import User
class PrimaryExpenseSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = PrimaryExpense
        fields = [
            "id",
            "vehicle",
            "cost",
            "type",
            "description",
            "date",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "date", "created_by", "created_at", "updated_at"]

from rest_framework import serializers
from .models import Journey, SecondaryExpense
from accounts.models import User
from fleet.models import Vehicle

# -----------------------------
# SecondaryExpense Serializer
# -----------------------------
class SecondaryExpenseSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SecondaryExpense
        fields = [
            "id",
            "type",
            "cost",
            "description",
            "date",
            "created_by",
        ]

# -----------------------------
# Journey Serializer
# -----------------------------
class JourneySerializer(serializers.ModelSerializer):
    driver = serializers.StringRelatedField()  # returns username/email
    expenses = SecondaryExpenseSerializer(many=True, read_only=True)  # nested

    class Meta:
        model = Journey
        fields = [
            "id",
            "destination",
            "driver",
            "vehicle",
            "status",
            "lat",
            "lng",
            "suggested_route",
            "actual_route",
            "estimated_time",
            "actual_time",
            "estimated_fuel",
            "actual_fuel",
            "start_at",
            "created_at",
            "updated_at",
            "expenses",  # include related expenses
        ]