from django.db import models
from accounts.models import User
from django.db import models
from drivers.models import Driver
class Device(models.Model):
    uuid = models.CharField(max_length=255, unique=True)   
    name = models.CharField(max_length=255,blank=True, null=True)
    type = models.CharField(max_length=100, default="GPS")
    rear_camera_url = models.URLField(max_length=500, blank=True, null=True)
    front_camera_url = models.URLField(max_length=500, blank=True, null=True)
    features = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.uuid})"



class Event(models.Model):
    device = models.ForeignKey(
        Device,
        to_field="uuid",            
        db_column="device_id",      
        on_delete=models.CASCADE,
        related_name="events"
    )

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    logged_at = models.DateTimeField(help_text="Event time from device (original source)")
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=100, default="")
    value = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "device_events"
        indexes = [
            models.Index(fields=["device", "logged_at"]),
            models.Index(fields=["type"]),
        ]

    def __str__(self):
        return f"Event {self.type} for {self.device_id} at {self.logged_at}"
    
class Heartbeat(models.Model):
    device = models.ForeignKey(
        Device,
        to_field="uuid",           
        db_column="device_id",     
        on_delete=models.CASCADE,
        related_name="heartbeats"
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    bearing = models.FloatField(null=True, blank=True)
    logged_at = models.DateTimeField(help_text="Event time from device (original source)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "device_heartbeats"
        indexes = [
            models.Index(fields=["device", "logged_at"]),
        ]

    def __str__(self):
        return f"Heartbeat for {self.device_id} at {self.logged_at}"


    
