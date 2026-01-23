
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from waffle.models import Flag

try:
    f, created = Flag.objects.get_or_create(name='admin_waffle_manager')
    # FORCE GLOBAL ENABLE
    f.everyone = True
    f.superusers = True
    f.save()
    print(f"SUCCESS: Flag '{f.name}' is now ON for EVERYONE.")
except Exception as e:
    print(f"ERROR: {e}")
