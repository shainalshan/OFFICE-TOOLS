
import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from contacts.models import Contact

def run_part3():
    print("--- PART 3: VERIFY RESTORE ---")
    contact_name = "Backup Test Contact"
    
    # Check for contact
    if Contact.objects.filter(name=contact_name).exists():
        print(f"SUCCESS: Contact '{contact_name}' was restored!")
    else:
        print(f"FAILURE: Contact '{contact_name}' was NOT found.")
        print("Possible reasons: Restore failed, DB not updated, or wrong backup file.")
        
    print("--- PART 3 COMPLETE ---")

if __name__ == "__main__":
    run_part3()
