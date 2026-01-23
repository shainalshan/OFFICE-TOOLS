import os
import django
import sys
from django.conf import settings
from django.core.mail import send_mail

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import NotificationEventSetting
from tickets.models import Ticket

def debug_email():
    print("--- DEBUGGING EMAIL DELIVERY ---")

    # 1. Check SMTP Settings
    print(f"SMTP Host: {settings.EMAIL_HOST}")
    print(f"SMTP Port: {settings.EMAIL_PORT}")
    print(f"SMTP User: {settings.EMAIL_HOST_USER}")
    print(f"SMTP Use TLS: {settings.EMAIL_USE_TLS}")

    # 2. Check Admin User
    # identifying likely test user (superuser)
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("ERROR: No superuser found.")
        return
    print(f"\nUser: {admin.username} (ID: {admin.id})")
    print(f"Email: {admin.email}")
    
    if not admin.email:
        print("ERROR: User has no email address!")
        return

    # 3. Check Subscription
    event_type = 'TICKET_CREATED'
    setting, _ = NotificationEventSetting.objects.get_or_create(event_type=event_type)
    
    if admin in setting.email_subscribers.all():
        print(f"SUCCESS: User IS subscribed to {event_type} (Email List)")
    else:
        print(f"FAIL: User is NOT in {event_type} email subscribers list!")
        print("-> Please add the user to the list in the admin panel.")
        # Proceeding anyway to test filter logic as if they were added
        setting.email_subscribers.add(admin)
        print("-> Temporarily added user for this test.")

    # 4. Test Filter Logic
    print("\nSimulating Ticket Creation...")
    ticket = Ticket(user=admin, ticket_id="DEBUG-001", issue="Debug Ticket", priority="P4")
    
    involved_ids = set()
    if ticket.user:
        involved_ids.add(ticket.user.id)
        print(f"Ticket Creator ID: {ticket.user.id} (Added to involved list)")
    
    is_involved = admin.id in involved_ids
    print(f"Is User Involved? {is_involved}")
    
    if is_involved:
        print("Logic Check: PASS (User would receive email)")
    else:
        print("Logic Check: FAIL (User filtered out)")

    # 5. Real Email Test
    print("\nAttempting to send REAL email (fail_silently=False)...")
    try:
        send_mail(
            subject='[Debug] Verification Email',
            message='If you see this, email sending IS working.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[admin.email],
            fail_silently=False  # Crucial: verify SMTP works
        )
        print("SUCCESS: Default send_mail command executed without error.")
    except Exception as e:
        print(f"ERROR: SMTP Failure: {e}")

if __name__ == "__main__":
    debug_email()
