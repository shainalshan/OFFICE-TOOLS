import os
import django
from django.conf import settings
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from hr.models import Timesheet

User = get_user_model()
try:
    u = User.objects.get(username='admin')
    ts = Timesheet.objects.filter(employee=u, period_start__month=timezone.now().month).first()
    if ts:
        print(f"User: {u.username}")
        print(f"Timesheet ID: {ts.id}")
        print(f"Period: {ts.period_start}")
        print(f"Status: '{ts.status}'")
        print(f"Rejection Reason: '{ts.rejection_reason}'")
    else:
        print("No timesheet found for admin this month.")
except User.DoesNotExist:
    print("User admin not found.")
