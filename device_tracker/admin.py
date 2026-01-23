from django.contrib import admin
from .models import TrackedDevice, DeviceLog

admin.site.register(TrackedDevice)
admin.site.register(DeviceLog)
