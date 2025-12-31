
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def fix_seq():
    with connection.cursor() as cursor:
        print("Fixing BackupLog sequence...")
        # Check current max
        cursor.execute("SELECT MAX(id) FROM backup_restore_backuplog")
        row = cursor.fetchone()
        max_id = row[0] if row[0] is not None else 0
        print(f"Max ID is: {max_id}")
        
        # Reset sequence
        seq_name = "backup_restore_backuplog_id_seq"
        new_val = max_id + 1
        sql = f"SELECT setval('{seq_name}', {new_val}, false)"
        cursor.execute(sql)
        print(f"Sequence {seq_name} reset to {new_val}")

if __name__ == '__main__':
    fix_seq()
