
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Tool

tool, created = Tool.objects.get_or_create(
    slug='monitor',
    defaults={
        'name': 'Server Monitor',
        'description': 'Live System Metrics & Logs',
        'is_active': True
    }
)

if created:
    print("Monitor tool created.")
else:
    tool.name = 'Server Monitor'
    tool.description = 'Live System Metrics & Logs'
    tool.is_active = True
    tool.save()
    print("Monitor tool updated.")
