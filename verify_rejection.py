
import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from core.views import admin_dashboard
from django.contrib.messages.storage.fallback import FallbackStorage

User = get_user_model()

def test_reject_user():
    # 1. Create a pending user
    username = "test_reject_user_001"
    email = "test001@example.com"
    if User.objects.filter(username=username).exists():
        User.objects.filter(username=username).delete()
        
    user = User.objects.create_user(username=username, email=email, password="password123")
    user.is_active = False
    user.save()
    print(f"Created pending user: {username} (ID: {user.id})")

    # 2. Simulate POST request to admin_dashboard with action='reject'
    factory = RequestFactory()
    data = {'action': 'reject', 'user_id': user.id}
    request = factory.post('/dashboard/', data)
    
    # Needs a superuser to access admin_dashboard
    superuser = User.objects.filter(is_superuser=True).first()
    if not superuser:
        print("Error: No superuser found to run the test.")
        return
        
    request.user = superuser
    
    # Fix for messages middleware
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)

    print("Sending Reject Request...")
    response = admin_dashboard(request)
    
    # 3. Verify user is deleted
    if not User.objects.filter(username=username).exists():
        print("SUCCESS: User was deleted.")
    else:
        print("FAILURE: User still exists.")
        
test_reject_user()
