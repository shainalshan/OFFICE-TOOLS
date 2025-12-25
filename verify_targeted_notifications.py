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
    print("--- Verifying Targeted Notification Logic ---")
    
    # 1. Setup Users
    # Creator
    u_creator, _ = User.objects.get_or_create(username='u_creator', email='creator@example.com')
    # Assignee
    u_assignee, _ = User.objects.get_or_create(username='u_assignee', email='assignee@example.com')
    # Bystander (Subscribed but not involved)
    u_bystander, _ = User.objects.get_or_create(username='u_bystander', email='bystander@example.com')
    
    print(f"Users: Creator={u_creator.email}, Assignee={u_assignee.email}, Bystander={u_bystander.email}")
    
    # 2. Setup Subscriptions (All Subscribed to ASSIGNED)
    setting, _ = NotificationEventSetting.objects.get_or_create(event_type='TICKET_ASSIGNED')
    setting.email_subscribers.clear()
    setting.email_subscribers.add(u_creator, u_assignee, u_bystander)
    print("All 3 users subscribed to TICKET_ASSIGNED.")
    
    # 3. Trigger Event: Ticket Assignment
    print("\n--- Triggering TICKET_ASSIGNED ---")
    try:
        t = Ticket.objects.create(user=u_creator, issue="Targeted Test", priority="P4")
        
        # Assign to Assignee
        t.assigned_to = u_assignee
        t.save()
        
        print("\nCHECK OUTPUT ABOVE:")
        print("Expected: Email sent to ['creator@example.com', 'assignee@example.com']")
        print("Expected: 'bystander@example.com' should NOT be in the list.")
        
    except Exception as e:
        print(f"Error: {e}")

    # Cleanup
    # t.delete()

if __name__ == "__main__":
    verify()
