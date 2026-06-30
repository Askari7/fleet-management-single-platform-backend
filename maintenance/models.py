from django.db import models
from fleet.models import Vehicle
from journeys.models import PrimaryExpense
from inventory.models import Vendor, SparePart, SparePartConsumption
class Maintenance(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="maintenances")
    primary_expense = models.ForeignKey(PrimaryExpense, on_delete=models.SET_NULL, null=True, blank=True, related_name="maintenances")
    expected_completion = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Maintenance #{self.id} for {self.vehicle.name} - {self.status}"


class WorkOrder(models.Model):
    """
    A job card that can fix multiple issues + standard preventative maintenance.
    """
    maintenance = models.ForeignKey(Maintenance, on_delete=models.CASCADE, related_name="work_orders")
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    parts_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=[('OPEN', 'Open'), ('COMPLETED', 'Completed')], default='OPEN')

    @property
    def total_cost(self):
        return self.labor_cost + self.parts_cost + self.tax

    def __str__(self):
        return f"WorkOrder #{self.id} - {self.status}"


class VehicleIssue(models.Model):
    """
    Issues reported by drivers or inspections. They are NOT work orders yet.
    """
    maintenance = models.ForeignKey(Maintenance, on_delete=models.CASCADE, related_name="issues", null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=[('LOW', 'Low'), ('NORMAL', 'Normal'), ('CRITICAL', 'Critical')], default='NORMAL')
    created_at = models.DateTimeField(auto_now_add=True)
    resolution_work_order = models.ForeignKey(WorkOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_issues')

    def __str__(self):
        return f"Issue #{self.id} - {self.title} ({self.priority})"


class MaintenanceSchedule(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    km_interval = models.PositiveIntegerField(null=True, blank=True)
    time_interval_days = models.PositiveIntegerField(null=True, blank=True)
    last_service_date = models.DateField(null=True, blank=True)
    last_service_km = models.PositiveIntegerField(default=0)
    next_service_date = models.DateField(null=True, blank=True)
    next_service_km = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.vehicle.registration_number} Maintenance Schedule"


class MaintenanceJobCard(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    spare_parts_used = models.ManyToManyField(SparePartConsumption, blank=True)
    service_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"JobCard: {self.vehicle.registration_number} on {self.date}"


# Optional KPI fields for reporting
class MaintenanceKPI(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE)
    mtbf_hours = models.FloatField(default=0)  # Mean Time Between Failures
    downtime_hours = models.FloatField(default=0)
    maintenance_cost_per_km = models.FloatField(default=0)

    def __str__(self):
        return f"KPI for {self.vehicle.registration_number}"