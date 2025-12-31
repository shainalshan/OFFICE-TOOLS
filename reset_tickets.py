
import os
import django
import sys

# Setup Django environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
print(f"DEBUG: BASE_DIR={BASE_DIR}")
print(f"DEBUG: sys.path={sys.path}")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from tickets.models import Ticket
from django.db import connection

def reset_tickets():
    print("Deleting all tickets...")
    Ticket.objects.all().delete()
    print("All tickets deleted.")

    print("Resetting auto-increment sequence...")
    with connection.cursor() as cursor:
        if connection.vendor == 'sqlite':
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='tickets_ticket';")
        elif connection.vendor == 'postgresql':
            cursor.execute("ALTER SEQUENCE tickets_ticket_id_seq RESTART WITH 1;")
        else:
            print(f"Warning: Database vendor {connection.vendor} not explicitly handled for sequence reset.")
            # Trying generic approach might differ, but this project uses SQLite/Postgres mostly.
    
    print("Sequence reset complete.")
    
    # Verification
    print("Creating verification ticket...")
    try:
        from django.contrib.auth.models import User
        user = User.objects.first()
        if not user:
            print("No user found to create ticket. Skipping create check.")
        else:
            t = Ticket.objects.create(user=user, issue="Sequence Check", priority='P4')
            print(f"Created ticket: {t.ticket_id}")
            if t.ticket_id == 'PIXL0000001':
                print("SUCCESS: Ticket ID is correct.")
            else:
                print(f"FAILURE: Expected PIXL0000001, got {t.ticket_id}")
            
            # Clean up test ticket
            t.delete()
            # Reset sequence again after test
            with connection.cursor() as cursor:
                if connection.vendor == 'sqlite':
                    cursor.execute("DELETE FROM sqlite_sequence WHERE name='tickets_ticket';")
                elif connection.vendor == 'postgresql':
                    cursor.execute("ALTER SEQUENCE tickets_ticket_id_seq RESTART WITH 1;")
            print("Cleaned up verification ticket and reset sequence again.")

    except Exception as e:
        print(f"Verification failed: {e}")

if __name__ == '__main__':
    reset_tickets()
