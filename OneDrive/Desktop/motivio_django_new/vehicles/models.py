from django.db import models
from django.contrib.auth.models import User

class Vehicle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=100, blank=True)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    vin = models.CharField(max_length=17, blank=True)
    license_plate = models.CharField(max_length=15, blank=True)
    current_mileage = models.PositiveIntegerField()
    image = models.ImageField(upload_to='vehicle_images', blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.nickname})" if self.nickname else f"{self.year} {self.make} {self.model}"

    class Meta:
        ordering = ['-date_added']

class MileageRecord(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='mileage_records')
    mileage = models.PositiveIntegerField()
    date_recorded = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.vehicle} - {self.mileage} miles on {self.date_recorded}"

    class Meta:
        ordering = ['-date_recorded']
