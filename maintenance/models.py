from django.db import models
from django.utils import timezone
from vehicles.models import Vehicle
from django.db.models.signals import post_save
from django.dispatch import receiver

class MaintenanceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    suggested_interval_miles = models.PositiveIntegerField(blank=True, null=True)
    suggested_interval_months = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Maintenance Categories"

class MaintenanceRecord(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_records')
    category = models.ForeignKey(MaintenanceCategory, on_delete=models.CASCADE)
    service_date = models.DateField()
    mileage_at_service = models.PositiveIntegerField()
    service_provider = models.CharField(max_length=255, blank=True)
    service_details = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    receipt_image = models.ImageField(upload_to='maintenance_receipts', blank=True, null=True)
    notes = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vehicle} - {self.category} at {self.mileage_at_service} miles"

    class Meta:
        ordering = ['-service_date']

class MaintenanceReminder(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('due_soon', 'Due Soon'),
        ('overdue', 'Overdue'),
        ('completed', 'Completed'),
    )

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_reminders')
    category = models.ForeignKey(MaintenanceCategory, on_delete=models.CASCADE)
    due_date = models.DateField(blank=True, null=True)
    due_mileage = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    last_service_date = models.DateField(blank=True, null=True)
    last_service_mileage = models.PositiveIntegerField(blank=True, null=True)
    suggested_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.vehicle} - {self.category} reminder"

class CostEstimate(models.Model):
    category = models.ForeignKey(MaintenanceCategory, on_delete=models.CASCADE)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100, blank=True)
    year_start = models.PositiveIntegerField(blank=True, null=True)
    year_end = models.PositiveIntegerField(blank=True, null=True)
    min_cost = models.DecimalField(max_digits=10, decimal_places=2)
    max_cost = models.DecimalField(max_digits=10, decimal_places=2)
    average_cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.category} cost for {self.make} {self.model} ({self.year_start}-{self.year_end})"

@receiver(post_save, sender=MaintenanceRecord)
def update_vehicle_mileage(sender, instance, created, **kwargs):
    """Update vehicle mileage if the maintenance record has a higher mileage"""
    if instance.mileage_at_service > instance.vehicle.current_mileage:
        instance.vehicle.current_mileage = instance.mileage_at_service
        instance.vehicle.save()

    # Check for any pending reminders for this category and mark them as completed
    reminders = MaintenanceReminder.objects.filter(
        vehicle=instance.vehicle,
        category=instance.category,
        status__in=['pending', 'due_soon', 'overdue']
    )

    for reminder in reminders:
        reminder.status = 'completed'
        reminder.last_service_date = instance.service_date
        reminder.last_service_mileage = instance.mileage_at_service
        reminder.save()
