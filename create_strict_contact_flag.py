import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from waffle.models import Flag

flag_name = 'strict_contact_validation'
flag, created = Flag.objects.get_or_create(name=flag_name)

if created:
    print(f"Flag '{flag_name}' created.")
else:
    print(f"Flag '{flag_name}' already exists.")

# Ensure it's active for everyone for testing purposes initially, or leave as default (off)?
# User requested "Strict Safety Mode: ON", so I should probably enable it.
flag.everyone = True
flag.save()
print(f"Flag '{flag_name}' set to Active for Everyone.")
