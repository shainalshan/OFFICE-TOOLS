
import os
import zipfile
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from backup_restore.models import BackupConfiguration

def inspect_backup():
    print("--- DEBUG: INSPECT BACKUP ---")
    config = BackupConfiguration.get_solitary()
    backup_dir = os.path.join(settings.BASE_DIR, config.backup_path)
    
    # Get latest
    files = [f for f in os.listdir(backup_dir) if f.endswith('.zip')]
    if not files:
        print("No backups found.")
        return
    files.sort(key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)))
    latest = files[-1]
    latest_path = os.path.join(backup_dir, latest)
    print(f"Inspecting: {latest}")

    with zipfile.ZipFile(latest_path, 'r') as zipf:
        names = zipf.namelist()
        if 'db_dump.sql' not in names:
            print("!!! db_dump.sql NOT FOUND in zip.")
            return
        
        print("db_dump.sql found. Reading content...")
        with zipf.open('db_dump.sql') as f:
            content = f.read().decode('utf-8', errors='ignore')
            if "Backup Test Contact" in content:
                print("SUCCESS: 'Backup Test Contact' found in SQL dump.")
            else:
                print("FAILURE: 'Backup Test Contact' NOT found in SQL dump.")
                print("Snippet of Dump (first 500 chars):")
                print(content[:500])

if __name__ == "__main__":
    inspect_backup()
