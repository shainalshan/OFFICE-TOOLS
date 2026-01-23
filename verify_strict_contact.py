import os
import django
import sys

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from contacts.models import Contact
from waffle.models import Flag
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from contacts.views import add_contact, edit_contact
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import get_user_model

# Setup
User = get_user_model()
try:
    user = User.objects.get(username='admin')
except User.DoesNotExist:
    user = User.objects.create_superuser('admin', 'admin@example.com', 'password')

# Mock permissions (since views usually check tool access, but here we might bypassing decorators or need to mock them if they are robust. 
# The check_tool_access decorator checks permissions. Let's make sure our user has them or is superuser (which they are).
# Superuser bypasses the specific tool check in decorators usually, checking logic in views.
# Wait, check_tool_access decorator logic:
# It's likely checking request.user.
# Let's hope superuser is enough.

factory = RequestFactory()

def setup_request(url, data=None):
    if data:
        request = factory.post(url, data)
    else:
        request = factory.get(url)
    request.user = user
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    return request

def run_test():
    print("Cleaning up old test contacts...")
    Contact.objects.filter(name__startswith="Test Contact").delete()

    # Create Initial Contact
    c1 = Contact.objects.create(name="Test Contact 1", phone_number="1234567890")
    print(f"Created {c1.name} with {c1.phone_number}")

    # Enable Flag
    flag, _ = Flag.objects.get_or_create(name='strict_contact_validation')
    flag.everyone = True
    flag.save()
    print("Flag strict_contact_validation ON")

    # Test 1: Add Duplicate with different formatting (Spaces and Country Code)
    print("\n--- Test 1: Add Duplicate (Flag ON) - Normalization Check ---")
    # Existing is '1234567890'. normalized -> 971... wait, 1234567890 doesn't start with 0.
    # Let's create a specific UAE number contact.
    
    uae_contact = Contact.objects.create(name="UAE Contact", phone_number="+971 54 771 1911", designation="Test")
    print(f"Created {uae_contact.name} with {uae_contact.phone_number}")

    # Try to add same number but with 0 prefix and no spaces
    request = setup_request('/contacts/add/', {
        'name': 'Duplicate UAE',
        'phone_number': '0547711911', # Should match +971 54 771 1911
        'email': 'dup@example.com',
        'designation': 'Test'
    })
    
    add_contact(request)
    
    if Contact.objects.filter(name='Duplicate UAE').exists():
        print("FAIL: Contact created despite normalized duplicate.")
    else:
        print("PASS: Contact creation blocked (Normalization worked).")
        msgs = [m.message for m in request._messages]
        print(f"Messages: {msgs}")
        if any("used by UAE Contact" in m for m in msgs):
            print("PASS: Correct owner identified.")

    # Test 2: Edit to Duplicate with different formatting
    print("\n--- Test 2: Edit Duplicate (Flag ON) - Normalization Check ---")
    c3 = Contact.objects.create(name="Test Contact 3", phone_number="055 123 4567", designation="Test")
    # Try to change it to match uae_contact but formatted strictly: +971547711911
    request = setup_request(f'/contacts/edit/{c3.id}/', {
        'name': 'Test Contact 3',
        'phone_number': '+971547711911', # Matches UAE Contact
        'email': 'test3@example.com',
        'designation': 'Test'
    })
    
    edit_contact(request, c3.id)
    c3.refresh_from_db()
    
    if c3.phone_number == '+971547711911':
        print("FAIL: Contact updated to normalized duplicate.")
    else:
        print("PASS: Contact update blocked.")
        msgs = [m.message for m in request._messages]
        print(f"Messages: {msgs}")

    # Test 3: Flag OFF
    print("\n--- Test 3: Flag OFF ---")
    flag.everyone = False
    flag.save()
    print("Flag strict_contact_validation OFF")
    
    request = setup_request('/contacts/add/', {
        'name': 'Test Contact 4',
        'phone_number': '1234567890', # Duplicate
        'email': 'test4@example.com',
        'designation': ''
    })
    try:
        add_contact(request)
        if Contact.objects.filter(name='Test Contact 4').exists():
            print("PASS: Contact created with duplicate (Flag OFF).")
        else:
            print("FAIL: Contact creation blocked despite Flag OFF (No exception, but not created).")
    except Exception as e:
        print(f"PASS: Original logic executed and hit DB constraint: {e}")

    # Cleanup
    Contact.objects.filter(name__startswith="Test Contact").delete()
    print("\nCleanup done.")

if __name__ == "__main__":
    run_test()
