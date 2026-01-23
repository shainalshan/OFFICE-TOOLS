import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Tool, User, UserToolAccess

def fix():
    # 1. Create Tool
    tool, created = Tool.objects.get_or_create(
        slug='3d-view',
        defaults={
            'name': '3D Map View',
            'description': 'Upload and view 3D models on a globe.',
            'is_active': True
        }
    )
    if created:
        print(f"Created tool: {tool.name}")
    else:
        tool.is_active = True
        tool.name = '3D Map View'
        tool.save()
        print(f"Updated tool: {tool.name}")

    # 2. Assign to ALL users (for dev simplicity)
    users = User.objects.all()
    for user in users:
        access, _ = UserToolAccess.objects.get_or_create(user=user)
        if tool not in access.tools.all():
            access.tools.add(tool)
            print(f"Assigned to {user.username}")
        else:
            print(f"Already assigned to {user.username}")

if __name__ == '__main__':
    fix()
