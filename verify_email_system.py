import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import NotificationEventSetting
from tickets.models import Ticket

def verify():
    print("--- Verifying Email Notification System ---")

    # 1. Setup Subscriber
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("No admin user found.")
        return

    # Ensure admin has an email
    if not admin.email:
        admin.email = "shainalshan@gmail.com" # Fallback/Test email if empty, or use the sender itself for loopback
        admin.save()
        print(f"Set admin email to {admin.email}")
    
    print(f"Using subscriber: {admin.username} ({admin.email})")

    # Subscribe to TICKET_CREATED
    setting, _ = NotificationEventSetting.objects.get_or_create(event_type='TICKET_CREATED')
    setting.subscribers.add(admin)
    print("Subscribed admin to TICKET_CREATED")

    # 2. Trigger Event: Create Ticket
    print("Creating test ticket...")
    try:
        from tickets.models import DeletedTicketLog # Ensure signal handlers loaded if not already
        import tickets.signals # Force load signals
        
        ticket = Ticket.objects.create(
            user=admin,
            issue="Test Ticket for Email Notification from Verify Script",
            priority="P4"
        )
        print(f"Ticket {ticket.ticket_id} created.")
        
    except Exception as e:
        print(f"Error creating ticket: {e}")

    # 3. Trigger Event: Assign Ticket
    print("\nAssigning ticket...")
    try:
        # Subscribe to TICKET_ASSIGNED
        setting_assign, _ = NotificationEventSetting.objects.get_or_create(event_type='TICKET_ASSIGNED')
        setting_assign.subscribers.add(admin)

        ticket.assigned_to = admin
        ticket.save()
        print(f"Ticket {ticket.ticket_id} assigned to {admin.username}.")
        
    except Exception as e:
        print(f"Error assigning ticket: {e}")

    # Cleaning up test ticket
    # ticket.delete()
    # print("Test ticket deleted.")

if __name__ == "__main__":
    verify()
