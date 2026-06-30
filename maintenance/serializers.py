from rest_framework import serializers
from fleet.models import Vehicle
from journeys.models import PrimaryExpense
from .models import Maintenance, VehicleIssue, WorkOrder

class WorkOrderSerializer(serializers.ModelSerializer):
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = WorkOrder
        fields = [
            'id',
            'vendor',
            'start_date',
            'completion_date',
            'labor_cost',
            'parts_cost',
            'tax',
            'status',
            'total_cost'
        ]
class VehicleIssueSerializer(serializers.ModelSerializer):
    resolution_work_order = WorkOrderSerializer(read_only=True)
    resolution_work_order_id = serializers.PrimaryKeyRelatedField(
        source='resolution_work_order', queryset=WorkOrder.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = VehicleIssue
        fields = ['id', 'title', 'description', 'priority', 'created_at', 'resolution_work_order', 'resolution_work_order_id']


class MaintenanceSerializer(serializers.ModelSerializer):
    issues = VehicleIssueSerializer(many=True, required=False)
    work_orders = WorkOrderSerializer(many=True, required=False)
    vehicle_id = serializers.PrimaryKeyRelatedField(source='vehicle', queryset=Vehicle.objects.all())
    primary_expense_id = serializers.PrimaryKeyRelatedField(
        source='primary_expense', queryset=PrimaryExpense.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Maintenance
        fields = [
            'id', 'vehicle_id', 'primary_expense_id', 'expected_completion', 'status', 'notes', 
            'created_at', 'updated_at', 'issues', 'work_orders'
        ]

    def create(self, validated_data):
        issues_data = validated_data.pop('issues', [])
        work_orders_data = validated_data.pop('work_orders', [])

        maintenance = Maintenance.objects.create(**validated_data)

        # Create WorkOrders first
        for wo_data in work_orders_data:
            WorkOrder.objects.create(**wo_data, maintenance=maintenance)

        # Create VehicleIssues
        for issue_data in issues_data:
            resolution_wo = issue_data.pop('resolution_work_order', None)
            if resolution_wo:
                issue_data['resolution_work_order'] = resolution_wo
            VehicleIssue.objects.create(**issue_data, maintenance=maintenance)

        return maintenance