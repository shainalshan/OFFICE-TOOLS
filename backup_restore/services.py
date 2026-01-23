import os
import shutil
import zipfile
import subprocess
import datetime
from django.conf import settings
from django.utils import timezone
from .models import BackupConfiguration, BackupLog

class BackupService:
    @staticmethod
    def get_backup_path():
        config = BackupConfiguration.get_solitary()
        path = config.backup_path
        if not os.path.isabs(path):
            path = os.path.join(settings.BASE_DIR, path)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @staticmethod
    def create_backup(is_auto=False, backup_type='full'):
        backup_dir = BackupService.get_backup_path()
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"backup_{timestamp}.zip"
        zip_path = os.path.join(backup_dir, filename)
        
        log = BackupLog.objects.create(
            file_path=zip_path,
            status='running',
            backup_type=backup_type
        )

        try:
            dump_file = None
            # 1. Dump Database (Only if full backup)
            if backup_type == 'full':
                db_settings = settings.DATABASES['default']
                db_name = db_settings['NAME']
                db_user = db_settings['USER']
                db_password = db_settings['PASSWORD']
                db_host = db_settings['HOST']
                db_port = db_settings['PORT']

                dump_file = os.path.join(settings.BASE_DIR, 'db_dump.sql')
                
                # Set PGPASSWORD environment variable for pg_dump
                env = os.environ.copy()
                env['PGPASSWORD'] = str(db_password)

                # Construct pg_dump command
                with open(dump_file, 'w') as f:
                    # Use absolute path for pg_dump
                    pg_dump_path = r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe"
                    subprocess.run(
                        [pg_dump_path, '-U', db_user, '-h', db_host, '-p', str(db_port), db_name],
                        env=env,
                        stdout=f,
                        check=True
                    )

            # 2. Zip Everything
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add DB Dump if exists
                if dump_file and os.path.exists(dump_file):
                    zipf.write(dump_file, 'db_dump.sql')
                
                # Add Project Files
                for root, dirs, files in os.walk(settings.BASE_DIR):
                    # Filter directories
                    dirs[:] = [d for d in dirs if d not in ['venv', '.git', '__pycache__', 'backups', 'staticfiles', '.gemini']]
                    
                    for file in files:
                        if file == 'db_dump.sql': continue # Already added
                        if file.endswith('.pyc'): continue
                        if file == 'db.sqlite3': continue # Skip sqlite if we are using postgres, or maybe keep it just in case
                        
                        abs_path = os.path.join(root, file)
                        rel_path = os.path.relpath(abs_path, settings.BASE_DIR)
                        zipf.write(abs_path, rel_path)

            # Cleanup dump file
            if dump_file and os.path.exists(dump_file):
                os.remove(dump_file)

            # Update Log
            log.status = 'success'
            log.file_size = f"{os.path.getsize(zip_path) / (1024*1024):.2f} MB"
            log.save()
            
            # Update Config last_backup_at
            config = BackupConfiguration.get_solitary()
            config.last_backup_at = timezone.now()
            config.save()
            
            return True, "Backup created successfully"

        except Exception as e:
            log.status = 'failed'
            log.error_message = str(e)
            log.save()
            return False, str(e)

def format_size(size):
    # Helper to format bytes
    # Already doing simple MB calculation above, but could be improved
    pass
