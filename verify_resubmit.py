import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from hr.models import Timesheet
from django.utils import timezone

User = get_user_model()
u = User.objects.get(username='admin')

c = Client()
c.force_login(u)

print("--- Testing Page Load (Syntax Check) ---")
response = c.get('/hr/timesheet/current/')
print(f"Status Code: {response.status_code}")
if response.status_code != 200:
    print("FAILED: Page did not load. Syntax error likely persists.")
    print(response.content.decode()[:500])
    exit(1)
else:
    print("SUCCESS: Page loaded (Syntax Error functionality fixed).")

print("\n--- Testing Rejection Display ---")
# Get the timesheet
ts = Timesheet.objects.filter(employee=u, period_start__month=timezone.now().month).first()
if not ts:
    print("Creating timesheet...")
    # Trigger creation via view or manually
    from hr.services import get_or_create_timesheet
    ts = get_or_create_timesheet(u, timezone.now().date())

ts.status = 'REJECTED'
ts.rejection_reason = "Integration Test Rejection"
ts.save()

response = c.get('/hr/timesheet/current/')
content = response.content.decode()

if "Timesheet Rejected" in content and "Integration Test Rejection" in content:
    print("SUCCESS: Rejection warning visible.")
else:
    print("FAILED: Rejection warning NOT found.")
    
if "Resubmit" in content:
    print("SUCCESS: Resubmit button visible.")
else:
    print("FAILED: Resubmit button NOT found.")

print("\n--- Testing Resubmission Logic ---")
response = c.post('/hr/timesheet/submit/')
ts.refresh_from_db()
print(f"Post Status: {response.status_code}")
print(f"New Status: {ts.status}")

if ts.status == 'SUBMITTED':
    print("SUCCESS: Timesheet resubmitted successfully.")
else:
    print(f"FAILED: Timesheet status is {ts.status}")
