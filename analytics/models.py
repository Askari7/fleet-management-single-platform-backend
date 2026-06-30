from django.db import models

# Create your models here.
class FleetKPI(models.Model):
    date = models.DateField(auto_now_add=True)

    total_vehicles = models.IntegerField(default=0)
    available = models.IntegerField(default=0)
    assigned = models.IntegerField(default=0)
    maintenance = models.IntegerField(default=0)
    offroad = models.IntegerField(default=0)

    utilization = models.FloatField(default=0.0)

    fuel_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    maintenance_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)