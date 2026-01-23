from django.contrib.auth import get_user_model
User = get_user_model()
u, created = User.objects.get_or_create(username='admin')
u.set_password('admin')
u.is_superuser = True
u.is_staff = True
u.save()
print(f"User admin {'created' if created else 'updated'}")
