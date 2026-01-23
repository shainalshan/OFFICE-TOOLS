
import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from contacts.models import Contact
from backup_restore.services import BackupService
from backup_restore.models import BackupConfiguration

def run_part1():
    print("--- PART 1: BACKUP AND DELETE ---")
    contact_name = "Backup Test Contact"
    
    # 1. Ensure Contact Exists
    contact, created = Contact.objects.get_or_create(
        name=contact_name,
        defaults={'phone_number': '12345', 'email': 'test@backup.com'}
    )
    print(f"Contact '{contact_name}' exists (ID: {contact.id}).")
    
    # 2. Trigger Backup
    print("Triggering Backup...")
    success, msg = BackupService.create_backup(backup_type='full')
    if not success:
        print(f"!!! Backup FAILED: {msg}")
        exit(1)
    print(f"Backup SUCCESS: {msg}")
    
    # 3. Verify Backup File
    config = BackupConfiguration.get_solitary()
    backup_dir = os.path.join(settings.BASE_DIR, config.backup_path)
    # Get latest zip
    files = [f for f in os.listdir(backup_dir) if f.endswith('.zip')]
    if not files:
        print("!!! No backup files found in directory.")
        exit(1)
    
    files.sort(key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)))
    latest_backup = files[-1]
    print(f"Latest backup verified: {latest_backup}")

    # 4. Delete Contact
    print(f"Deleting contact '{contact_name}'...")
    contact.delete()
    
    if not Contact.objects.filter(name=contact_name).exists():
        print(f"Contact '{contact_name}' successfully DELETED.")
    else:
        print("!!! Failed to delete contact.")
        exit(1)

    print("--- PART 1 COMPLETE ---")

if __name__ == "__main__":
    run_part1()
