from django.db import models
from fleet.models import Vehicle
class Vendor(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class SparePart(models.Model):
    name = models.CharField(max_length=100)
    part_number = models.CharField(max_length=50, unique=True)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    minimum_threshold = models.PositiveIntegerField(default=1)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.part_number})"

    def is_below_threshold(self):
        return self.quantity_in_stock <= self.minimum_threshold


class SparePartConsumption(models.Model):
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    quantity_used = models.PositiveIntegerField(default=1)
    date_used = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity_used} x {self.spare_part.name}"
    
class PurchaseHistory(models.Model):
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    quantity_purchased = models.PositiveIntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity_purchased} x {self.spare_part.name} from {self.vendor}"