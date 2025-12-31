
import os
import django
from django.contrib.auth import get_user_model
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from contacts.models import Contact
from backup_restore.models import BackupConfiguration

User = get_user_model()

def setup():
    # 1. Create Superuser 'testadmin'
    username = 'testadmin'
    password = 'password123'
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, 'test@example.com', password)
        print(f"Created superuser: {username}")
    else:
        u = User.objects.get(username=username)
        u.set_password(password)
        u.save()
        print(f"Updated superuser: {username}")

    # 2. Create Test Contact
    contact_name = "Backup Test Contact"
    # Ensure it doesn't exist to avoid duplicates
    Contact.objects.filter(name=contact_name).delete()
    Contact.objects.create(
        name=contact_name,
        phone_number="555-0199",
        email="test@backup.com",
        designation="Test Subject"
    )
    print(f"Created contact: {contact_name}")

    # 3. Print Backup Path
    config = BackupConfiguration.get_solitary()
    full_path = os.path.join(settings.BASE_DIR, config.backup_path)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    print(f"Backup Path: {full_path}")

if __name__ == '__main__':
    setup()
