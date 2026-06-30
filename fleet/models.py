from django.db import models
from django.utils import timezone
from datetime import date
from accounts.models import User
from devices.models import Device
from drivers.models import Driver


class Vehicle(models.Model):
    STATUS_CHOICES = (
        ('AVAILABLE', 'Available'),
        ('ASSIGNED', 'Assigned'),
        ('MAINTENANCE', 'Maintenance'),
        ('OFF_ROAD', 'Off-Road'),
        ('DISPOSED', 'Disposed'),
    )
    device = models.OneToOneField(
        "devices.Device",
        to_field="uuid",
        db_column="device_id",
        on_delete=models.CASCADE,
        related_name="vehicles"
    )
    user_id = models.ForeignKey(
        User,
        to_field="id",
        db_column="user_id",
        on_delete=models.CASCADE,
        related_name="vehicles"
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    registration_number = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100, blank=True, null=True)
    model_year = models.IntegerField(blank=True, null=True)
    operational_warranty = models.IntegerField(blank=True, null=True)
    chassis_number = models.CharField(max_length=100, blank=True, null=True)
    engine_number = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=50,default="Bus", choices=[
        ('SUV','SUV'), ('Pickup','Pickup'), ('Bus','Bus'), ('Heavy Equipment','Heavy Equipment')
    ])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    number_of_tyres = models.PositiveIntegerField(default=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.registration_number})"

class VehicleLocation(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(auto_now_add=True)

class VehicleDeviceHistory(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(default=timezone.now)
    removed_at = models.DateTimeField(null=True, blank=True)

class VehicleValue(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="vehicle_values"
    )
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    current_value = models.DecimalField(max_digits=12, decimal_places=2)
    depreciation_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    depreciation_percentage = models.FloatField(blank=True, null=True)
    recorded_date = models.DateField(default=date.today)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vehicle.registration_number} - Value on {self.recorded_date}"
    
class VehicleOdometer(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='odometers')
    reading = models.DecimalField(max_digits=12, decimal_places=2)
    reading_date = models.DateField(auto_now_add=True)

class VehicleStatusHistory(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="status_history")
    status = models.CharField(max_length=20, choices=Vehicle.STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class VehicleDocument(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50, default="")
    file = models.FileField(upload_to="vehicle_docs/")
    expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

class FuelLog(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="fuel_logs"
    )
    date = models.DateField(default=date.today)
    odometer_reading = models.DecimalField(max_digits=10, decimal_places=2)  # in km
    fuel_filled = models.DecimalField(max_digits=8, decimal_places=2)  # in liters
    fuel_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # optional
    fuel_station = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vehicle.registration_number} - {self.date}"

    @property
    def fuel_average(self):
        """
        Calculates fuel efficiency (km per liter) compared to previous record.
        Assumes logs are entered in chronological order.
        """
        previous_log = FuelLog.objects.filter(
            vehicle=self.vehicle,
            date__lt=self.date
        ).order_by('-date').first()

        if previous_log:
            km_driven = self.odometer_reading - previous_log.odometer_reading
            if self.fuel_filled > 0:
                return round(km_driven / self.fuel_filled, 2)
        return None

class Insurance(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="insurances"
    )
    policy_number = models.CharField(max_length=100, unique=True)
    provider_name = models.CharField(max_length=255)
    insurance_type = models.CharField(
        max_length=50,
        choices=(
            ("THIRD_PARTY", "Third Party"),
            ("COMPREHENSIVE", "Comprehensive"),
        ),
        default="COMPREHENSIVE"
    )
    coverage_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    premium_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    start_date = models.DateField()
    expiry_date = models.DateField()
    document = models.FileField(upload_to="insurance_documents/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vehicle.registration_number} - {self.policy_number}"

class VehicleAssignment(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="assignments")
    driver = models.ForeignKey(
            Driver,
            to_field="id",            
            db_column="driver_id",      
            on_delete=models.CASCADE,
            related_name="driver_assignments"
        )
    assigned_on = models.DateTimeField(auto_now_add=True)
    released_on = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Driver {self.driver_id} assigned to Vehicle {self.vehicle_id}"
    
    def is_active(self):
        return self.released_on is None
class AssignmentHistory(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    start_odometer = models.IntegerField(default=0)
    end_odometer = models.IntegerField(null=True, blank=True, default=None)