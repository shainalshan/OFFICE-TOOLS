import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
u, created = User.objects.get_or_create(username='admin')
u.email = 'shainaldof@gmail.com'
u.set_password('Heartland7sha$#')
u.is_superuser = True
u.is_staff = True
u.save()
print(f"User admin {'created' if created else 'updated'} with email shainaldof@gmail.com")
