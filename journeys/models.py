from django.db import models
from accounts.models import User 
    
class Journey(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    destination = models.CharField(max_length=255)
    driver = models.ForeignKey("drivers.Driver", on_delete=models.SET_NULL, null=True, blank=True, related_name='journeys')
    vehicle = models.ForeignKey("fleet.Vehicle", on_delete=models.SET_NULL, null=True, blank=True)    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    lat = models.DecimalField(max_digits=9, decimal_places=6, default=0.0, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, default=0.0, null=True, blank=True)
    suggested_route = models.TextField(blank=True, null=True)  # Could store JSON or a simple string of waypoints
    actual_route = models.TextField(blank=True, null=True)  # Could store JSON or a simple string of waypoints
    estimated_time = models.DurationField(blank=True, null=True)  # Estimated travel time
    actual_time = models.DurationField(blank=True, null=True)  # Estimated travel time
    estimated_fuel = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)  # Fuel in liters
    actual_fuel = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)  # Fuel in liters
    start_at = models.DateTimeField(blank=True, null=True)  # Journey start time
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.destination} ({self.driver} - {self.vehicle})"


class PrimaryExpense(models.Model):
    EXPENSE_TYPES = [
        ("insurance", "Insurance"),
        ("fuel", "Fuel"),
        ("maintenance", "Maintenance"),
        ("other", "Other"),
    ]

    vehicle = models.ForeignKey("fleet.Vehicle", on_delete=models.CASCADE, related_name="expenses")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(max_length=50, choices=EXPENSE_TYPES, default="other")
    description = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vehicle.registration_number} - {self.type} - {self.cost}"
class SecondaryExpense(models.Model):
    EXPENSE_TYPES = [
        ("toll", "Toll"),
        ("operational", "Operational"),
        ("challan", "Challan"),
        ("other", "Other"),
    ]

    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, related_name="expenses")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(max_length=50, choices=EXPENSE_TYPES, default="other")
    description = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.journey.name} - {self.type} - {self.cost}"
    


class Incident(models.Model):
    INCIDENT_TYPES = [
        ('ACCIDENT', 'Accident'),
        ('SPEED_VIOLATION', 'Speed Violation'),
        ('VIOLATION', 'Driver Violation'),
        ('OTHER', 'Other'),
    ]
    
    vehicle = models.ForeignKey("fleet.Vehicle", on_delete=models.CASCADE)
    driver = models.ForeignKey("drivers.Driver", on_delete=models.SET_NULL, null=True, blank=True)
    incident_type = models.CharField(max_length=20, choices=INCIDENT_TYPES, default="OTHER")
    description = models.TextField(default="")
    date_occurred = models.DateTimeField()
    repair_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    root_cause = models.TextField(blank=True, null=True)
    gps_speed = models.FloatField(blank=True, null=True)  # optional GPS speed integration

    def __str__(self):
        return f"{self.incident_type} - {self.vehicle.registration_number} on {self.date_occurred}"
