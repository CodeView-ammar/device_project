from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
import uuid


class DeviceType(models.Model):
    """Model representing a type of device (e.g., Printer, Computer, etc.)"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Device(models.Model):
    """Model representing a device in the inventory"""
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('repair', 'In Repair'),
        ('retired', 'Retired'),
    )

    name = models.CharField(max_length=100)
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE, related_name='devices')
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    barcode = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    acquisition_date = models.DateField(default=timezone.now)
    warranty_expiry = models.DateField(null=True, blank=True)
    additional_info = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_devices')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.serial_number})"

    def get_absolute_url(self):
        return reverse('inventory:device_detail', args=[str(self.id)])
    
    def get_barcode_url(self):
        return reverse('inventory:device_barcode', args=[str(self.id)])
    
    def get_maintenance_records(self):
        return self.maintenance_records.order_by('-maintenance_date')
    
    def get_next_maintenance_date(self):
        maintenance = self.maintenance_records.filter(
            next_maintenance_date__gt=timezone.now()
        ).order_by('next_maintenance_date').first()
        
        return maintenance.next_maintenance_date if maintenance else None
    
    class Meta:
        ordering = ['-updated_at']


class MaintenanceRecord(models.Model):
    """Model representing a maintenance record for a device"""
    MAINTENANCE_TYPE_CHOICES = (
        ('routine', 'Routine Check'),
        ('repair', 'Repair'),
        ('upgrade', 'Upgrade'),
        ('other', 'Other'),
    )

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_date = models.DateTimeField(default=timezone.now)
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    description = models.TextField()
    performed_by = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    next_maintenance_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.name} - {self.maintenance_date}"
    
    class Meta:
        ordering = ['-maintenance_date']
