import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import NotificationEventSetting, SystemNotification
from assets.models import Asset

def test_notifications():
    print("--- Verifying Notification System ---")
    
    # 1. Setup Admin User & Subscription
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("FAIL: No admin user found")
        return

    print(f"Testing with User: {admin_user.username}")
    
    # Subscribe to ASSET_UPDATE
    setting, _ = NotificationEventSetting.objects.get_or_create(event_type='ASSET_UPDATE')
    setting.subscribers.add(admin_user)
    print("Subscribed admin to ASSET_UPDATE")

    # 2. Trigger Event (Create Asset)
    print("Creating Test Asset...")
    Asset.objects.create(
        brand="TestBrand",
        model_detail="TestModel",
        serial_number="TEST-12345",
        status="IN_STORE"
    )

    # 3. Verify Notification Exists
    notif = SystemNotification.objects.filter(
        recipient=admin_user, 
        title="Asset Added"
    ).order_by('-created_at').first()

    if notif:
        print("PASS: Notification created successfully!")
        print(f"Title: {notif.title}")
        print(f"Message: {notif.message}")
    else:
        print("FAIL: No notification found for Asset creation.")

    # Clean up
    Asset.objects.filter(serial_number="TEST-12345").delete()
    # keeping notification for UI check

if __name__ == '__main__':
    test_notifications()
