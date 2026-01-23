import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from waffle.models import Flag

try:
    flag, created = Flag.objects.get_or_create(name='animated_login')
    if created:
        flag.is_active = True
        flag.save()
        print("created")
    else:
        # ensuring it's on for testing
        flag.is_active = True 
        flag.save()
        print("updated")
except Exception as e:
    print(f"error: {e}")
