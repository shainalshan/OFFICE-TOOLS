import os
import django
from django.urls import reverse
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

def test_theme_urls():
    print("Testing URL Reversal...")
    try:
        url = reverse('theme_changer')
        print(f"SUCCESS: 'theme_changer' resolves to: {url}")
    except Exception as e:
        print(f"FAILURE: Could not reverse 'theme_changer': {e}")
        return

    print("\nTesting Client Access...")
    client = Client()
    # Need to be logged in as superuser
    from django.contrib.auth.models import User
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            client.force_login(admin_user)
            print(f"Logged in as {admin_user.username}")
            
            response = client.get(url)
            print(f"GET {url} - Status: {response.status_code}")
            
            if response.status_code == 200:
                print("SUCCESS: View loaded correctly.")
            else:
                print(f"FAILURE: View returned {response.status_code}")
        else:
            print("WARNING: No superuser found to test login.")
    except Exception as e:
        print(f"Error during client test: {e}")

if __name__ == "__main__":
    test_theme_urls()
