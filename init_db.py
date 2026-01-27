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
        'name': 'Ticketing System',
        'slug': 'ticketing',
        'description': 'Report issues and track status',
        'is_active': True
    },
    {
        'name': 'Office News',
        'slug': 'news',
        'description': 'Latest company updates',
        'is_active': True
    },

    {
        'name': 'Asset Management',
        'slug': 'assets',
        'description': 'Track company devices and inventory',
        'is_active': True
    },
    {
        'name': 'Image Compressor',
        'slug': 'image-compressor',
        'description': 'Compress images to 30-50KB allowed size',
        'is_active': True
    },
    {
        'name': 'Server Monitor',
        'slug': 'monitor',
        'description': 'Live server performance and logs',
        'is_active': True
    },
    {
        'name': 'Contacts',
        'slug': 'contacts',
        'description': 'Manage employee and business contacts',
        'is_active': True
    },
    {
        'name': 'Timesheet',
        'slug': 'timesheet',
        'description': 'Timesheets and HR management',
        'is_active': True
    },
    {
        'name': 'Group Chat',
        'slug': 'chat',
        'description': 'Team communication',
        'is_active': True
    },
    {
        'name': 'PDF to Word',
        'slug': 'pdf-to-word',
        'description': 'Convert PDF documents to editable Word files',
        'is_active': True
    }
]


for tool_data in tools_data:
    tool, created = Tool.objects.update_or_create(
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
        print(f"Updated tool: {tool.name}")

# Create Superuser if not exists
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'shainaldof@gmail.com', 'Heartland7sha$#')
    print("Created superuser: admin / Heartland7sha$#")
else:
    print("Superuser 'admin' already exists")
