import os
import django
import urllib.request
import urllib.parse
import http.cookiejar
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import SystemNotification

# Setup User
User = get_user_model()
u, _ = User.objects.get_or_create(username='tester')
u.set_password('TestPass123')
u.email = 'test@example.com'
u.save()

# Create Notification
SystemNotification.objects.create(recipient=u, title='API Test', message='Testing deletion')

# Setup Opener with Cookies
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
urllib.request.install_opener(opener)

# Login
login_url = 'http://127.0.0.1:8000/login/'
# Get CSRF cookie first
opener.open(login_url)
csrftoken = ''
for cookie in cj:
    if cookie.name == 'csrftoken':
        csrftoken = cookie.value

print(f"Login CSRF: {csrftoken}")

login_data = urllib.parse.urlencode({
    'username': 'tester', 
    'password': 'TestPass123', 
    'csrfmiddlewaretoken': csrftoken
}).encode('utf-8')

req = urllib.request.Request(login_url, data=login_data, headers={'Referer': login_url})
opener.open(req)
print("Logged in.")

# Clear All
clear_url = 'http://127.0.0.1:8000/api/notifications/clear-all/'

# Get updated CSRF if changed
for cookie in cj:
    if cookie.name == 'csrftoken':
        csrftoken = cookie.value

print(f"API CSRF: {csrftoken}")

req = urllib.request.Request(clear_url, method='POST')
req.add_header('X-CSRFToken', csrftoken)
req.add_header('Content-Type', 'application/json')
# Django expects Referer for CSRF checks usually
req.add_header('Referer', clear_url)

try:
    resp = opener.open(req)
    print(f"Clear All Status: {resp.getcode()}")
    print(f"Response: {resp.read().decode('utf-8')}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")

# Verify
count = SystemNotification.objects.filter(recipient=u).count()
print(f"Notifications after: {count}")

if count == 0:
    print("SUCCESS")
else:
    print("FAILURE")
