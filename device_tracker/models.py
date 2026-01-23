from django.db import models
from django.utils import timezone

class TrackedDevice(models.Model):
    hostname = models.CharField(max_length=100)
    os_info = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    last_seen = models.DateTimeField(auto_now=True)
    
    # Status derived from last_seen (e.g. < 2 mins ago = Online)
    
    def __str__(self):
        return f"{self.hostname} ({self.serial_number})"

class DeviceLog(models.Model):
    device = models.ForeignKey(TrackedDevice, on_delete=models.CASCADE, related_name='logs')
    cpu_percent = models.FloatField()
    memory_percent = models.FloatField()
    battery_percent = models.FloatField(null=True, blank=True)
    is_charging = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
    
    # We can also store IP or Location here if needed
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
