import os
import django
from django.conf import settings
from django.urls import reverse, resolve
from django.test import RequestFactory
from pixl_core import views

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_pixl_url():
    print("--- Checking Pixl configuration ---")
    
    # 1. Check App Config
    if 'pixl_core' in settings.INSTALLED_APPS:
        print("[PASS] pixl_core is in INSTALLED_APPS")
    else:
        print("[FAIL] pixl_core is NOT in INSTALLED_APPS")

    # 2. Check URL Resolution
    try:
        url = reverse('knowledge_list')
        print(f"[PASS] URL 'knowledge_list' resolves to: {url}")
    except Exception as e:
        print(f"[FAIL] Could not reverse 'knowledge_list': {e}")
        return

    # 3. Check URL Match
    try:
        match = resolve(url)
        print(f"[PASS] URL matches view: {match.func_name}")
    except Exception as e:
        print(f"[FAIL] Could not resolve URL path: {e}")

    # 4. Simulate Request
    print("--- Simulating Request ---")
    factory = RequestFactory()
    request = factory.get(url)
    
    # We need to simulate a logged-in user for @login_required
    from django.contrib.auth.models import User
    user = User.objects.first()
    if user:
        request.user = user
        print(f"Using user: {user.username}")
        
        try:
            response = views.knowledge_list(request)
            print(f"[PASS] View returned status code: {response.status_code}")
            if response.status_code != 200:
                print(f"Response Content: {response.content.decode()[:200]}...")
        except Exception as e:
            print(f"[FAIL] View raised exception: {e}")
    else:
        print("[WARN] No users found to test login_required view.")

if __name__ == "__main__":
    test_pixl_url()
