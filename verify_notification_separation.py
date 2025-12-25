import os
import django
import sys
from django.conf import settings

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import NotificationEventSetting
from tickets.models import Ticket

def verify():
    print("--- Verifying Notification Separation Logic ---")

    # 1. Setup User
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("No admin user found.")
        return

    if not admin.email:
        admin.email = "test@example.com"
        admin.save()
    
    print(f"Using user: {admin.username} ({admin.email})")

    # 2. Setup Settings
    # Get or create TICKET_CREATED setting
    setting, _ = NotificationEventSetting.objects.get_or_create(event_type='TICKET_CREATED')
    
    # Clear both lists to ensure clean state
    setting.subscribers.clear()
    setting.email_subscribers.clear()
    print("Cleared all subscribers for TICKET_CREATED.")

    # 3. Test Internal Subscribers ONLY (Should NOT send email)
    print("\n--- Test 1: Internal Subscriber Only ---")
    setting.subscribers.add(admin)
    print("Added user to Internal 'subscribers'.")
    
    try:
        t1 = Ticket.objects.create(
            user=admin,
            issue="Test Ticket Internal Only",
            priority="P4"
        )
        print("Ticket Created.")
        # We rely on inspecting stdout for "Email sent to..." message.
        # If the logic is correct, NO email log should appear here.
    except Exception as e:
        print(f"Error: {e}")

    # 4. Test Email Subscribers (Should SEND email)
    print("\n--- Test 2: Email Subscriber ---")
    setting.email_subscribers.add(admin)
    print("Added user to 'email_subscribers'.")
    
    try:
        t2 = Ticket.objects.create(
            user=admin,
            issue="Test Ticket Email Subscriber",
            priority="P4"
        )
        print("Ticket Created.")
        # If logic is correct, "Email sent to..." log SHOULD appear here.
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify()
