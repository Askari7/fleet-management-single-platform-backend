from django.db import models
from fleet.models import Vehicle

class Tyre(models.Model):
    POSITION_CHOICES = (
        ('FL', 'Front Left'), ('FR', 'Front Right'),
        ('RL', 'Rear Left'), ('RR', 'Rear Right'),
        ('SPARE', 'Spare'), ('STORE', 'In Store'),
    )
    serial_number = models.CharField(max_length=50, unique=True)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    purchased_date = models.DateField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    current_vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name="tyres")
    current_position = models.CharField(max_length=10, choices=POSITION_CHOICES, default='STORE')
    status = models.CharField(max_length=20, choices=[('MOUNTED', 'Mounted'), ('STOCK', 'In Stock'), ('SCRAPPED', 'Scrapped')], default='STOCK')
    total_km_run = models.IntegerField(default=0, help_text="Aggregated from history")
    def __str__(self):
        return f"{self.brand} ({self.serial_number})"

class TyreHistory(models.Model):
    """
    The Golden Record: Tracks a tyre's life across multiple vehicles.
    """
    tyre = models.ForeignKey(Tyre, on_delete=models.CASCADE, related_name='history')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    position = models.CharField(max_length=10, choices=Tyre.POSITION_CHOICES)    
    install_date = models.DateField()
    install_odometer = models.IntegerField()
    remove_date = models.DateField(null=True, blank=True)
    remove_odometer = models.IntegerField(null=True, blank=True)
    
    @property
    def km_gained(self):
        if self.remove_odometer:
            return self.remove_odometer - self.install_odometer
        return 0