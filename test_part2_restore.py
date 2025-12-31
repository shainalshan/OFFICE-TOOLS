
import os
import django
import subprocess
import shutil

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from backup_restore.models import BackupConfiguration

def run_part2():
    print("--- PART 2: TRIGGER RESTORE ---")
    
    # 1. Find Latest Backup
    config = BackupConfiguration.get_solitary()
    backup_dir = os.path.join(settings.BASE_DIR, config.backup_path)
    files = [f for f in os.listdir(backup_dir) if f.endswith('.zip')]
    if not files:
        print("No backup files found.")
        exit(1)
    
    files.sort(key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)))
    latest_backup = files[-1]
    latest_backup_path = os.path.join(backup_dir, latest_backup)
    print(f"Restoring from: {latest_backup_path}")

    # 2. Stage for Restore
    temp_path = os.path.join(settings.BASE_DIR, 'temp_restore.zip')
    shutil.copy(latest_backup_path, temp_path)
    print("Staged backup file.")

    # 3. Prepare Environment
    db_settings = settings.DATABASES['default']
    env = os.environ.copy()
    env['DB_USER'] = db_settings['USER']
    env['PGPASSWORD'] = db_settings['PASSWORD']
    env['DB_NAME'] = db_settings['NAME']
    env['DB_HOST'] = db_settings['HOST']
    env['DB_PORT'] = str(db_settings['PORT'])

    restore_script = os.path.join(settings.BASE_DIR, 'restore_system.bat')
    
    print("Launching restore_system.bat and DETACHING...")
    print("WARNING: This will kill all python processes, including this script.")
    
    # DETACHED_PROCESS = 0x00000008
    # CREATE_NEW_CONSOLE = 0x00000010
    subprocess.Popen(
        [restore_script, temp_path, str(settings.BASE_DIR)],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
        env=env,
        close_fds=True
    )
    print("Launched. Goodbye.")

if __name__ == "__main__":
    run_part2()
