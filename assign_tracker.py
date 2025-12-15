import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Tool
from django.contrib.auth.models import User

def fix_permissions():
    # 1. Ensure Tool Exists
    tool, created = Tool.objects.get_or_create(
        slug='device-tracker',
        defaults={
            'name': 'Device Monitor',
            'description': 'Real-time CPU, RAM & Location tracking.'
        }
    )
    if created:
        print("Created 'Device Monitor' tool.")
    else:
        print("'Device Monitor' tool already exists.")

    # 2. Assign to Superuser
    admin = User.objects.filter(is_superuser=True).first()
    if admin:
        admin.profile.tools.add(tool)
        print(f"Assigned to {admin.username}")
    else:
        print("No superuser found.")

if __name__ == '__main__':
    fix_permissions()
