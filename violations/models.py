from django.db import models
from devices.models import Device
from fleet.models import Vehicle

class ViolationCategory(models.Model):
    violation_category_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.violation_category_name

class ViolationType(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        ViolationCategory,
        on_delete=models.CASCADE,
        related_name='violations'
    )
    is_annotatable = models.BooleanField(default=False)
    severity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.category.violation_category_name})"
    
class Violation(models.Model):
    device = models.ForeignKey(
        Device,
        to_field="uuid",            
        db_column="device_id",      
        on_delete=models.CASCADE,
        related_name="violations"
    )
    vehicle= models.ForeignKey( 
        Vehicle, 
        to_field="id",            
        db_column="vehicle_id",   
        on_delete=models.CASCADE,
        related_name="violations",blank=True, null=True
    ) 
    user= models.ForeignKey( 
        'accounts.User', 
        to_field="id",            
        db_column="user_id",       
        on_delete=models.CASCADE,
        related_name="violations",blank=True, null=True 
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    logged_at = models.DateTimeField(help_text="Event time from device (original source)")
    created_at = models.DateTimeField(auto_now_add=True)
    violation_type_id=models.ForeignKey(
        ViolationType,
        to_field="id",            # 👈 use the uuid field instead of PK id
        db_column="violation_id",      
        on_delete=models.CASCADE,
        related_name="violations"
    )
    front_camera_video_file_name = models.CharField(max_length=255, null=True, blank=True)
    rear_camera_video_file_name = models.CharField(max_length=255, null=True, blank=True)
    left_camera_video_file_name = models.CharField(max_length=255, null=True, blank=True)
    right_camera_video_file_name = models.CharField(max_length=255, null=True, blank=True)
    cabin_camera_video_file_name = models.CharField(max_length=255, null=True, blank=True)
    driver_id = models.CharField(max_length=100, null=True, blank=True)
    meta=models.CharField(max_length=100, null=True, blank=True)
    status=models.CharField(max_length=100, default="unevaluated")
    class Meta:
        db_table = "device_violations"
        indexes = [
            models.Index(fields=["logged_at"]), models.Index(fields=["status"]), models.Index(fields=["user"]), models.Index(fields=["vehicle"]), models.Index(fields=["violation_type_id"]),
            models.Index(fields=["device", "logged_at", "violation_type_id"]),
        ]
    def __str__(self):
        return f"Violations for {self.device_id} at {self.logged_at}"

class ViolationAnnotation(models.Model):
    violation = models.ForeignKey(
        Violation,
        to_field="id",            
        db_column="violation_id",      
        on_delete=models.CASCADE,
        related_name="annotations"
    )
    annotated_by = models.ForeignKey(
        'accounts.User',
        to_field="id",            
        db_column="annotated_by",      
        on_delete=models.CASCADE,
        related_name="violation_annotations"
    )
    status = models.CharField(max_length=100)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "violation_annotations"
        indexes = [
            models.Index(fields=["violation", "annotated_by", "status", "created_at"]),
        ]
    def __str__(self):
        return f"Annotation for Violation {self.violation_id} by User {self.annotated_by_id}"



