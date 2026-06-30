from django.db import models
from django.utils import timezone
class Driver(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        to_field="id",
        db_column="user_id",
        on_delete=models.CASCADE,
        related_name="drivers"
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    cnic_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    rfid_tag = models.CharField(max_length=100, unique=True, null=True, blank=True)
    dob = models.DateField(blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    license_type = models.CharField(max_length=20, blank=True, null=True)
    license_expiry = models.DateField(blank=True, null=True)
    is_available = models.BooleanField(default=True)  # current availability
    STATUS_CHOICES = [
        ("active", "Active"),
        ("off-duty", "Off Duty"),
        ("on-break", "On Break"),
        ("unavailable", "Unavailable"),
        ("on-journey", "On Journey"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
        help_text="Current driver status"
    )
    performance_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    medical_record = models.FileField(upload_to='driver_medical/', blank=True, null=True)
    training_certificate = models.FileField(upload_to='driver_training/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.email})"

    def license_expired(self):
        if self.license_expiry:
            return self.license_expiry < timezone.now().date()
        return False
    
class DriverViolation(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="violations")
    violation_type = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)
    remarks = models.TextField(blank=True, null=True)
    penalty_points = models.IntegerField(default=0)
    incident = models.ForeignKey("journeys.Incident", on_delete=models.CASCADE,null=True, blank=True, related_name="driver_violations")
    def __str__(self):
        return f"{self.driver.name} - {self.violation_type} ({self.date})"