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
from tickets.models import Ticket, TicketComment

def verify():
    print("--- Verifying Extended Notification Events ---")

    # 1. Setup User
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("No admin user found.")
        return
    
    if not admin.email:
        admin.email = "test@example.com"
        admin.save()
        
    print(f"Using user: {admin.username} ({admin.email})")

    # 2. Setup Subscriptions
    events = ['TICKET_CANCELLED', 'TICKET_COMPLETED', 'TICKET_COMMENTED']
    for evt in events:
        setting, _ = NotificationEventSetting.objects.get_or_create(event_type=evt)
        setting.email_subscribers.clear()
        setting.email_subscribers.add(admin)
        print(f"Subscribed to {evt}")

    # Ensure STATUS_CHANGED is NOT subscribed to verify separation
    setting_status, _ = NotificationEventSetting.objects.get_or_create(event_type='TICKET_STATUS_CHANGED')
    setting_status.email_subscribers.clear()
    print("Cleared TICKET_STATUS_CHANGED subscriptions (to ensure no overlap)")

    # 3. Test Comment
    print("\n--- Test 1: Comment Notification ---")
    try:
        t1 = Ticket.objects.create(user=admin, issue="Comment Test Ticket", priority="P4")
        
        TicketComment.objects.create(
            ticket=t1,
            user=admin,
            text="This is a test comment."
        )
        print("Comment added. (Expected: Email sent for TICKET_COMMENTED)")
    except Exception as e:
        print(f"Error: {e}")

    # 4. Test Cancellation
    print("\n--- Test 2: Cancellation Notification ---")
    try:
        t1.status = 'CANCELLED'
        t1.save()
        print("Ticket Cancelled. (Expected: Email sent for TICKET_CANCELLED)")
        print("(If logic is correct, NO TICKET_STATUS_CHANGED email should appear)")
    except Exception as e:
        print(f"Error: {e}")

    # 5. Test Completion
    print("\n--- Test 3: Completion Notification ---")
    try:
        t2 = Ticket.objects.create(user=admin, issue="Completion Test Ticket", priority="P4")
        t2.status = 'COMPLETED'
        t2.save()
        print("Ticket Completed. (Expected: Email sent for TICKET_COMPLETED)")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify()
