
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User, Group
from tickets.forms import TicketForm

def verify_assignee_queryset():
    print("--- Verifying TicketForm Assignee Queryset ---")

    # 1. Setup Groups
    admin_group, _ = Group.objects.get_or_create(name='Ticket Admin')
    support_group, _ = Group.objects.get_or_create(name='Ticket Support')

    # 2. Setup Users
    # Admin User
    admin_user, _ = User.objects.get_or_create(username='test_admin_user')
    admin_user.groups.add(admin_group)
    admin_user.save()

    # Support User
    support_user, _ = User.objects.get_or_create(username='test_support_user')
    support_user.groups.add(support_group)
    support_user.save()

    # Regular User (should not be in list)
    regular_user, _ = User.objects.get_or_create(username='test_regular_user')
    regular_user.groups.remove(admin_group) 
    regular_user.groups.remove(support_group)
    regular_user.save()

    # 3. Init Form
    form = TicketForm()
    
    # 4. Check Queryset
    queryset = form.fields['assigned_to'].queryset
    users_in_qs = list(queryset)
    usernames = [u.username for u in users_in_qs]
    
    print(f"Assignee Options: {usernames}")

    # 5. Assertions
    if admin_user in users_in_qs:
        print("PASS: Ticket Admin is in options.")
    else:
        print("FAIL: Ticket Admin missing.")
        
    if support_user in users_in_qs:
        print("PASS: Ticket Support is in options.")
    else:
        print("FAIL: Ticket Support missing.")
        
    if regular_user not in users_in_qs:
        print("PASS: Regular user is NOT in options.")
    else:
        print("FAIL: Regular user IS in options (should not be).")

if __name__ == '__main__':
    verify_assignee_queryset()
