from django.contrib import admin
from .models import Asset

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('mni', 'device_type', 'brand', 'model_detail', 'assigned_to', 'status')
    list_filter = ('device_type', 'status', 'os_type', 'brand')
    search_fields = ('serial_number', 'model_detail', 'assigned_to__username', 'assigned_to_email')
