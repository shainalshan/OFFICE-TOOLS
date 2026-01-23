import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import NotificationEventSetting

def check_and_fix():
    print("--- Checking Notification Settings ---")
    
    # 1. Check EVENT_TYPES definitions
    print(f"Defined EVENT_TYPES in model: {len(NotificationEventSetting.EVENT_TYPES)}")
    for code, label in NotificationEventSetting.EVENT_TYPES:
        print(f"  - {code}: {label}")

    # 2. Check DB Objects
    print("\n--- Objects in Database ---")
    existing = NotificationEventSetting.objects.all()
    existing_codes = [e.event_type for e in existing]
    for e in existing:
        print(f"  - {e.event_type} (Subscribers: {e.subscribers.count()})")

    # 3. Create missing
    print("\n--- Creating Missing ---")
    created_count = 0
    for code, label in NotificationEventSetting.EVENT_TYPES:
        if code not in existing_codes:
            NotificationEventSetting.objects.create(event_type=code)
            print(f"  + Created {code}")
            created_count += 1
    
    if created_count == 0:
        print("All settings already exist.")
    else:
        print(f"Created {created_count} new settings.")

if __name__ == "__main__":
    check_and_fix()
