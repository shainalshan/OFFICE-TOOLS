import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from contacts.models import Contact

contacts = Contact.objects.all()
print(f"Total Contacts: {contacts.count()}")
for c in contacts:
    print(f" - {c.name} ({c.phone_number})")
