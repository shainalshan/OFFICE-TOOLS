import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from core.views import search_users_notification

def diagnose_search():
    print("--- DIAGNOSING USER SEARCH API ---")
    
    # 1. Create Dummy Users for Search
    print("Creating test users...")
    u1, _ = User.objects.get_or_create(username="search_test_1", email="alice@test.com", first_name="Alice")
    u2, _ = User.objects.get_or_create(username="search_test_2", email="bob@test.com", first_name="Bob")

    factory = RequestFactory()
    
    # 2. Test Partial Match (Username)
    print("\nTest 1: Search by partial username 'search_test'")
    req = factory.get('/api/notifications/search-users/', {'q': 'search_test'})
    req.user = u1 # Mock login
    resp = search_users_notification(req)
    data = json.loads(resp.content)
    print(f"Result count: {len(data['users'])}")
    if len(data['users']) >= 2:
        print("[PASS] Found created users.")
    else:
        print(f"[FAIL] Expected at least 2, got {len(data['users'])}")

    # 3. Test Partial Match (Email)
    print("\nTest 2: Search by partial email 'alice'")
    req = factory.get('/api/notifications/search-users/', {'q': 'alice'})
    req.user = u1
    resp = search_users_notification(req)
    data = json.loads(resp.content)
    print(f"Result count: {len(data['users'])}")
    if len(data['users']) >= 1 and data['users'][0]['username'] == 'search_test_1':
        print("[PASS] Found Alice by email.")
    else:
        print(f"[FAIL] Could not find Alice by email.")

    # 4. Test Empty Query
    print("\nTest 3: Empty Query")
    req = factory.get('/api/notifications/search-users/', {'q': ''})
    req.user = u1
    resp = search_users_notification(req)
    data = json.loads(resp.content)
    print(f"Result count: {len(data['users'])}")
    if len(data['users']) == 0:
         print("[PASS] correctly returned empty list.")
    else:
         print("[FAIL] Should return empty list for empty query.")

    print("\n--- DIAGNOSIS COMPLETE ---")

if __name__ == '__main__':
    diagnose_search()
