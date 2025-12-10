import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Tool, UserToolAccess

def fix_permissions():
    print("Fixing permissions...")
    ticketing = Tool.objects.filter(slug='ticketing').first()
    
    if not ticketing:
        print("Ticketing tool not found!")
        return

    users = User.objects.filter(is_active=True, is_superuser=False)
    for user in users:
        access, _ = UserToolAccess.objects.get_or_create(user=user)
        if ticketing not in access.tools.all():
            access.tools.add(ticketing)
            print(f"Granted Ticketing access to: {user.username}")
        else:
            print(f"User already has access: {user.username}")

    print("Done.")

if __name__ == '__main__':
    fix_permissions()
