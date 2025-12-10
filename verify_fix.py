import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def check_structure():
    c = Client()
    # Login
    login = c.login(username='admin', password='admin123')
    print(f"Login successful: {login}")
    
    try:
        response = c.get('/tickets/admin-panel/')
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            print("Error Content:")
            # Print first 5 lines of content to see error
            print(response.content.decode()[:500])
        else:
            print("Page loaded successfully.")
            if "Pending" in response.content.decode():
                print("Found content 'Pending'.")
    except Exception as e:
        print(f"Exception during request: {e}")

if __name__ == '__main__':
    check_structure()
