import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = 'admin_test'
password = 'AdminPass123!'
email = 'admin@test.com'

if User.objects.filter(username=username).exists():
    u = User.objects.get(username=username)
    u.set_password(password)
    u.is_superuser = True
    u.is_staff = True
    u.is_active = True
    u.save()
    print(f"Updated existing admin: {username}")
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Created new admin: {username}")
