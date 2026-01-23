
import os
import subprocess
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_psql():
    print("Testing PSQL Connection...")
    db = settings.DATABASES['default']
    env = os.environ.copy()
    env['PGPASSWORD'] = db['PASSWORD']
    
    psql = r"C:\Program Files\PostgreSQL\16\bin\psql.exe"
    
    cmd = [psql, '-U', db['USER'], '-h', db['HOST'], '-p', str(db['PORT']), '-d', db['NAME'], '-c', 'SELECT 1 as connected;']
    
    try:
        res = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=10)
        print("STDOUT:", res.stdout)
        print("STDERR:", res.stderr)
        print("Return Code:", res.returncode)
    except subprocess.TimeoutExpired:
        print("Timed out connecting to DB.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_psql()
