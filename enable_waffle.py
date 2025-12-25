
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from waffle.models import Flag

try:
    f, created = Flag.objects.get_or_create(name='admin_waffle_manager')
    # Enable for superusers explicitly
    f.superusers = True
    # Ensure it's not disabled for everyone (if it was set to False specifically)
    if f.everyone is False:
        f.everyone = None 
    f.save()
    print(f"SUCCESS: Flag '{f.name}' has been enabled for Admins (Superusers).")
except Exception as e:
    print(f"ERROR: {e}")
