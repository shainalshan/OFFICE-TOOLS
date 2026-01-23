
import os
import zipfile
import subprocess
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from backup_restore.models import BackupConfiguration

def manual_restore():
    print("--- DEBUG: MANUAL DB RESTORE (STDIN) ---")
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
    print(f"Restoring from: {latest}")

    # CLOSE CONNECTIONS
    django.db.connections.close_all()
    print("Closed Django connections.")

    # Extract dump
    dump_path = os.path.join(settings.BASE_DIR, 'temp_db_dump.sql')
    with zipfile.ZipFile(latest_path, 'r') as zipf:
        with zipf.open('db_dump.sql') as src, open(dump_path, 'wb') as dst:
            dst.write(src.read())
    
    # Run PSQL
    db_settings = settings.DATABASES['default']
    env = os.environ.copy()
    env['PGPASSWORD'] = db_settings['PASSWORD']
    

    

    
    psql_path = r"C:\Program Files\PostgreSQL\16\bin\psql.exe"
    
    # 0. KILL CONNECTIONS
    print("Killing active connections...")
    kill_sql = f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_settings['NAME']}' AND pid <> pg_backend_pid();"
    kill_cmd = [
        psql_path,
        '-U', db_settings['USER'],
        '-h', db_settings['HOST'],
        '-p', str(db_settings['PORT']),
        db_settings['NAME'],
        '-c', kill_sql
    ]
    try:
        subprocess.run(kill_cmd, env=env, capture_output=True, text=True)
        print("Connections killed.")
    except Exception as e:
        print(f"Kill connections failed: {e}")

     # 1. DROP SCHEMA
    print("Dropping schema...")
    drop_cmd = [
        psql_path,
        '-U', db_settings['USER'],
        '-h', db_settings['HOST'],
        '-p', str(db_settings['PORT']),
        db_settings['NAME'],
        '-c', "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
    ]
    try:
        res_drop = subprocess.run(drop_cmd, env=env, capture_output=True, text=True)
        print("DROP STDOUT:", res_drop.stdout)
        print("DROP STDERR:", res_drop.stderr)
    except Exception as e:
        print(f"Drop schema failed: {e}")

    # 2. RESTORE
    cmd = [
        psql_path,
        '-U', db_settings['USER'],
        '-h', db_settings['HOST'],
        '-p', str(db_settings['PORT']),
        db_settings['NAME']
    ]
    
    print(f"Running PSQL with stdin from {dump_path}...")
    
    try:
        with open(dump_path, 'r') as f:
            result = subprocess.run(
                cmd,
                env=env,
                stdin=f,
                capture_output=True, 
                text=True,
                timeout=60
            )
        
        print("--- STDOUT ---")
        print(result.stdout[-1000:] if result.stdout else "None")
        print("--- STDERR ---")
        print(result.stderr[-1000:] if result.stderr else "None")
        
        if result.returncode == 0:
            print("Restore command finished successfully.")
        else:
            print(f"Restore command failed with code {result.returncode}")
            
    except subprocess.TimeoutExpired:
        print("PSQL Timed out!")
    except Exception as e:
        print(f"Exception running psql: {e}")

    # Cleanup
    if os.path.exists(dump_path):
        os.remove(dump_path)

if __name__ == "__main__":
    manual_restore()
