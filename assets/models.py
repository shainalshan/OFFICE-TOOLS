from django.db import models
from django.contrib.auth.models import User

class Asset(models.Model):
    DEVICE_TYPES = [
        ('WINDOWS', 'Windows'),
        ('MAC', 'Mac'),
        ('IPHONE', 'iPhone'),
        ('DAMAGED', 'Damaged'),
        ('REPLACEMENT', 'Replacement'),
        ('RESIGNED', 'Resigned'),
        ('OTHER', 'Other'),
    ]

    OS_TYPES = [
        ('MAC', 'MacOS / iOS'),
        ('WINDOWS', 'Windows'),
        ('ANDROID', 'Android'),
        ('LINUX', 'Linux'),
        ('NONE', 'N/A'),
    ]

    STATUS_CHOICES = [
        ('IN_USE', 'Company Asset'),
        ('IN_STORE', 'In Store'),
        ('DAMAGED', 'Damaged'),
        ('REPAIR', 'Under Repair'),
        ('LOST', 'Lost/Stolen'),
    ]

    LOCATION_CHOICES = [
        ('DUBAI', 'Dubai'),
        ('INDIA', 'India'),
        ('PAKISTAN', 'Pakistan'),
    ]

    # Excel Columns Mapping
    mni = models.CharField(max_length=50, blank=True, help_text="Inventory ID")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets', help_text="Staff in Possession")
    assigned_to_email = models.EmailField(blank=True, null=True, help_text="Fallback if user not in system")
    
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES, default='LAPTOP')
    brand = models.CharField(max_length=50)
    model_detail = models.CharField(max_length=100, help_text="Detail/Specs")
    serial_number = models.CharField(max_length=100, unique=True, help_text="Serial Number/Device ID")
    
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default='DUBAI')
    is_signed = models.BooleanField(default=False, help_text="Signed For")
    
    os_type = models.CharField(max_length=10, choices=OS_TYPES, default='NONE', help_text="For statistics")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_STORE')
    remarks = models.TextField(blank=True, help_text="Status/Remarks")
    
    date_issued = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand} {self.model_detail} ({self.serial_number})"
