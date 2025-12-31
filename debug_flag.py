import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
import waffle
from waffle.models import Flag

# Ensure flag exists and is set to everyone
flag, created = Flag.objects.get_or_create(name='profile')
print(f"Flag 'profile': everyone={flag.everyone}, superusers={flag.superusers}, staff={flag.staff}, authenticated={flag.authenticated}, active={flag.is_active}")

# Test with AnonymousUser
factory = RequestFactory()
request = factory.get('/login/')
request.user = AnonymousUser()
request.session = {}

# Waffle usually needs middleware to set request.waffle_flags object if checking via tag?
# But checking via `flag_is_active` directly:
is_active = waffle.flag_is_active(request, 'profile')
print(f"waffle.flag_is_active(AnonymousUser, 'profile') = {is_active}")
