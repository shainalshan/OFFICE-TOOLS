import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import SystemNotification

User = get_user_model()
u, created = User.objects.get_or_create(username='tester')
u.set_password('TestPass123')
u.email = 'test@example.com'
u.save()

# Create a few notifications
SystemNotification.objects.create(recipient=u, title='Test 1', message='Delete me please')
SystemNotification.objects.create(recipient=u, title='Test 2', message='Delete me too')

print("Setup complete. User: tester/TestPass123")
