from django.apps import AppConfig
import threading
import sys
import os

class BackupRestoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backup_restore'

    def ready(self):
        # Prevent running in separate threads/processes like reloaders multiple times
        # verification logic: run only in the main server process
        if 'runserver' not in sys.argv:
            return
            
        # Avoid starting scheduler during migration or other management commands
        # This is a basic check; dependent on how the server is run.
        if os.environ.get('RUN_MAIN') != 'true':
            # This is the reloader process, or the main process before reload
            # We want the inner process to run it
            return

        from .scheduler import start_scheduler
        thread = threading.Thread(target=start_scheduler, daemon=True)
        thread.start()
