import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.views import profile_view
import waffle
from waffle.models import Flag

User = get_user_model()
factory = RequestFactory()

# Setup User and Flag
user, _ = User.objects.get_or_create(username='test_profile_user', email='test@example.com')
# Ensure no superuser powers interfere
user.is_superuser = False
user.is_staff = False
user.save()

flag, _ = Flag.objects.get_or_create(name='profile')

def test_access(flag_active):
    # Waffle Flag Logic: To turn ON, everyone=True. To turn OFF, everyone=False (or None if no other rules).
    flag.everyone = True if flag_active else False
    flag.save()
    
    # Reload from DB to be sure
    flag.refresh_from_db()
    
    state_str = 'ON' if flag_active else 'OFF'
    print(f"\n--- Testing with Flag [{state_str}] (everyone={flag.everyone}) ---")
    
    request = factory.get('/profile/') # Use direct path to avoid reverse issues if any remained
    request.user = user
    from django.contrib.sessions.middleware import SessionMiddleware
    from django.contrib.messages.storage.fallback import FallbackStorage
    
    # Add session
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()
    
    # Add messages manually
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    
    # Waffle often caches on the request object. Since we create a new request, it should be clean.
    # However, let's explicit check waffle first.
    is_active = waffle.flag_is_active(request, 'profile')
    print(f"waffle.flag_is_active('profile') returned: {is_active}")
    
    response = profile_view(request)
    print(f"View Status Code: {response.status_code}")
    
    if flag_active and response.status_code == 200:
         print("SUCCESS: Access granted.")
    elif not flag_active and response.status_code == 302:
         print("SUCCESS: Access denied (redirected).")
    else:
         print("FAILURE: Unexpected behavior.")

# Test OFF
test_access(False)

# Test ON
test_access(True)

print("\n--- Verifying Model Fields ---")
from core.models import UserProfile
profile, _ = UserProfile.objects.get_or_create(user=user)
if hasattr(profile, 'birth_date'):
    print("SUCCESS: UserProfile has 'birth_date' field.")
else:
    print("FAILURE: UserProfile missing 'birth_date' field.")
