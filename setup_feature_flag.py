import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from waffle.models import Flag

flag_name = 'manage_approvers'
flag, created = Flag.objects.get_or_create(name=flag_name)

if created:
    print(f"Flag '{flag_name}' created.")
else:
    print(f"Flag '{flag_name}' already exists.")

# Ensure it is initially inactive (safe mode)
flag.everyone = False
flag.save()
print(f"Flag '{flag_name}' is currently {'ACTIVE' if flag.everyone else 'INACTIVE'}.")
