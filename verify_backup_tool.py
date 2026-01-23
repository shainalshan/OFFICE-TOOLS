import os
import django
from django.conf import settings
from django.test import RequestFactory, Client
from django.urls import reverse
import waffle

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def verify_backup_tool():
    print("--- Verifying Backup Tool Implementation ---")
    
    # 1. Check Feature Flag
    flag_name = 'new_backup_tool'
    if waffle.flag_is_active(None, flag_name): 
        # Pass None as request might be tricky for global check, but waffle usually handles it if configured
        # Better to check db directly or use a dummy request
        print(f"✅ Feature Flag '{flag_name}' is ACTIVE.")
    else:
        print(f"✅ Feature Flag '{flag_name}' is INACTIVE (or request context needed). Checking DB...")
        from waffle.models import Flag
        try:
            f = Flag.objects.get(name=flag_name)
            print(f"   - DB Record found. Everyone={f.everyone}")
        except Flag.DoesNotExist:
            print(f"   ❌ DB Record NOT found for '{flag_name}'")

    # 2. Check Admin Dashboard for Link
    client = Client()
    # Create superuser if needed for test, but assuming we can just check if login required
    # Actually, we need to be logged in as superuser to see the card
    from django.contrib.auth import get_user_model
    User = get_user_model()
    admin_user = User.objects.filter(is_superuser=True).first()
    if admin_user:
        client.force_login(admin_user)
        print(f"   - Logged in as: {admin_user.username}")
        
        response = client.get(reverse('admin_dashboard'))
        content = response.content.decode('utf-8')
        
        if 'Backup & Restore' in content:
            print("✅ Backup & Restore Card FOUND in Admin Dashboard.")
        else:
            print("❌ Backup & Restore Card NOT found in Admin Dashboard.")
            
        # 3. Check Backup View Access
        try:
            resp = client.get(reverse('backup_dashboard'))
            if resp.status_code == 200:
                print("✅ Backup Dashboard View returned 200 OK.")
            else:
                print(f"❌ Backup Dashboard View returned {resp.status_code}.")
        except Exception as e:
            print(f"❌ Error accessing Backup Dashboard: {e}")

    else:
        print("❌ No superuser found to test views.")

    # 4. Check PG Dump Path
    pg_dump_path = r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe"
    if os.path.exists(pg_dump_path):
        print(f"✅ pg_dump found at: {pg_dump_path}")
    else:
        print(f"❌ pg_dump NOT found at: {pg_dump_path}")

if __name__ == '__main__':
    verify_backup_tool()
