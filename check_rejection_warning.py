import os
import django
from django.conf import settings
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from hr.models import Timesheet

User = get_user_model()
u = User.objects.get(username='admin')
ts = Timesheet.objects.filter(employee=u, period_start__month=timezone.now().month).first()

if not ts:
    print("Creating timesheet...")
    from hr.services import get_or_create_timesheet
    ts = get_or_create_timesheet(u, timezone.now().date())

ts.status = 'REJECTED'
ts.rejection_reason = "Final Verification Rejection Reason"
ts.save()

c = Client()
c.force_login(u)
response = c.get('/hr/timesheet/current/')
content = response.content.decode()

if "❌ Timesheet Rejected" in content:
    print("SUCCESS: Warning header found.")
else:
    print("FAILED: Warning header NOT found.")
    print("Partial Content around expected area:")
    start = content.find("<!-- Actions -->")
    print(content[start:start+500])

if "Final Verification Rejection Reason" in content:
    print("SUCCESS: Rejection reason found.")
else:
    print("FAILED: Rejection reason NOT found.")
    idx = content.find("Reason:")
    if idx != -1:
        print(f"Content after Reason: '{content[idx:idx+100]}'")
    else:
        print("Reason label not found")
