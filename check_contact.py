import os
import django
from django.db.models import Q

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from contacts.models import Contact
from core.models import User

def check_person():
    query = 'aswanth'
    print(f"Searching for '{query}'...")
    
    # Check Contacts
    contacts = Contact.objects.filter(name__icontains=query)
    if contacts.exists():
        print(f"Found in Contacts:")
        for c in contacts:
            print(f"- {c.name} ({c.email})")
    else:
        print("Not found in Contacts.")

    # Check Users
    users = User.objects.filter(username__icontains=query) | User.objects.filter(first_name__icontains=query)
    if users.exists():
        print(f"Found in Users:")
        for u in users:
            print(f"- {u.username} (Name: {u.first_name})")
    else:
        print("Not found in Users.")

if __name__ == '__main__':
    check_person()
