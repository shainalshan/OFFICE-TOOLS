import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.template.loader import render_to_string
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
import waffle

factory = RequestFactory()
request = factory.get('/login/')
request.user = AnonymousUser()

# Add session/messages if needed for context processors
middleware = SessionMiddleware(lambda x: None)
middleware.process_request(request)
request.session.save()

# We simulate what the view does:
show_forgot_password = waffle.flag_is_active(request, 'profile')
print(f"Flag Active (View Logic): {show_forgot_password}")

output = render_to_string('core/login.html', {
    'form': None, 
    'show_forgot_password': show_forgot_password
}, request=request)

if "Forgot Password?" in output:
    print("SUCCESS: 'Forgot Password?' found in rendered HTML.")
else:
    print("FAILURE: 'Forgot Password?' NOT found in rendered HTML.")
    
# Check for waffle tag presence (it shouldn't be valid HTML if not processed)
if "{% flag" in output:
    print("ERROR: Waffle tag not processed.")

import waffle
print(f"Waffle Active: {waffle.flag_is_active(request, 'profile')}")
