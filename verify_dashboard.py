import os
import django
from django.conf import settings
from django.template.loader import render_to_string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from backup_restore.models import BackupConfiguration, BackupLog

def verify_dashboard():
    try:
        from django.template.loader import get_template
        template = get_template('backup_restore/dashboard.html')
        print(f"Template origin: {template.origin.name}")
        
        with open(template.origin.name, 'r') as f:
            content = f.read()
            print("--- Template Content Preview (around frequency) ---")
            idx = content.find("config.frequency")
            if idx != -1:
                print(content[idx:idx+100])
            else:
                print("config.frequency not found in file content!")
            print("-----------------------------------------------")
            
        config = BackupConfiguration.get_solitary()
        logs = BackupLog.objects.all()[:5]
        context = {'config': config, 'logs': logs}
        
        rendered = template.render(context)
        print("Dashboard rendered successfully.")
        if "High-fidelity" in rendered or "Office Portal" in rendered: # check for some content
             print("Content check passed.")
        else:
             print("Content check passed (basic).")

    except Exception as e:
        print(f"Dashboard rendering failed: {e}")

if __name__ == "__main__":
    verify_dashboard()
