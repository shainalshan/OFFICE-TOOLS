import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from core.models import NotificationEventSetting, SystemNotification
from core.views import list_notifications
from assets.models import Asset

def run_diagnostics():
    print("--- DIAGNOSTIC START ---")
    
    # 1. Setup Data
    username = "diag_user"
    email = "diag@example.com"
    user, created = User.objects.get_or_create(username=username, email=email)
    if created:
        print(f"[OK] Created diagnostic user: {username}")
    else:
        print(f"[OK] Found diagnostic user: {username}")

    # 2. Test Subscription Logic (Admin View Logic)
    print("\n--- Testing Subscription ---")
    event_type = 'ASSET_UPDATE'
    setting, _ = NotificationEventSetting.objects.get_or_create(event_type=event_type)
    
    # Ensure clean slate
    setting.subscribers.remove(user)
    if user not in setting.subscribers.all():
        print(f"[OK] User removed from {event_type} subscribers.")
    
    # Add subscriber
    setting.subscribers.add(user)
    if user in setting.subscribers.all():
        print(f"[OK] User successfully subscribed to {event_type}.")
    else:
        print(f"[FAIL] Could not subscribe user to {event_type}!")
        return

    # 3. Test Signal Trigger (Event Logic)
    print("\n--- Testing Signal Trigger ---")
    # Clear old notifs
    SystemNotification.objects.filter(recipient=user).delete()
    
    # Create Asset
    try:
        Asset.objects.create(
            brand="DiagBrand",
            model_detail="DiagModel",
            serial_number="DIAG-999",
            status="IN_STORE"
        )
        print("[OK] Asset created.")
    except Exception as e:
        print(f"[FAIL] Error creating asset: {e}")
        return

    # Check for notification
    notif = SystemNotification.objects.filter(recipient=user).first()
    if notif:
        print(f"[OK] Notification created: '{notif.title}' - '{notif.message}'")
    else:
        print(f"[FAIL] Signal did NOT create a notification!")
        
        # Check if signal is connected? Hard to do programmatically, but we can verify via manual call
        from core.signals import notify_asset_update
        print("[INFO] Manually checking signal import...")
    
    # 4. Test API Response (View Logic)
    print("\n--- Testing API Response ---")
    factory = RequestFactory()
    request = factory.get('/api/notifications/list/')
    request.user = user # Mock login
    
    try:
        response = list_notifications(request)
        content = json.loads(response.content)
        
        if 'notifications' in content and len(content['notifications']) > 0:
            api_notif = content['notifications'][0]
            print(f"[OK] API returned {len(content['notifications'])} notifications.")
            print(f"     Title: {api_notif['title']}")
            if api_notif['is_read'] == True: # View marks as read
                 print(f"[OK] API marked notification as read.")
        else:
            print(f"[FAIL] API returned empty list or invalid format: {content}")
            
    except Exception as e:
        print(f"[FAIL] Error in list_notifications view: {e}")

    # Cleanup
    Asset.objects.filter(serial_number="DIAG-999").delete()
    print("\n--- DIAGNOSTIC COMPLETE ---")

if __name__ == '__main__':
    run_diagnostics()
