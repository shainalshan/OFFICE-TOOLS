import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Tool

# Create Default Tools
tools_data = [
    {
        'name': 'Signature Generator',
        'slug': 'signature',
        'description': 'Create optimized HTML email signatures'
    },
    {
        'name': 'Clock Widget',
        'slug': 'clock',
        'description': 'Coming Soon',
        'is_active': False
    },
    {
        'name': 'PDF Converter',
        'slug': 'pdf',
        'description': 'Coming Soon',
        'is_active': False
    },
    {
        'name': 'Ticketing System',
        'slug': 'ticketing',
        'description': 'Report issues and track status',
        'is_active': True
    }
]

for tool_data in tools_data:
    tool, created = Tool.objects.get_or_create(
        slug=tool_data['slug'],
        defaults={
            'name': tool_data['name'],
            'description': tool_data['description'],
            'is_active': tool_data.get('is_active', True)
        }
    )
    if created:
        print(f"Created tool: {tool.name}")
    else:
        print(f"Tool already exists: {tool.name}")

# Create Superuser if not exists
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Created superuser: admin / admin123")
else:
    print("Superuser 'admin' already exists")
