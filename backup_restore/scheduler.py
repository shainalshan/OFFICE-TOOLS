import time
import threading
from django.utils import timezone
from .models import BackupConfiguration
from .services import BackupService
import traceback

def job():
    try:
        # Re-fetch config each time to get latest settings
        # Note: We need to handle database connection in threads carefully in Django
        # Usually Django handles it if we access DB, but for long running threads, 
        # connections might time out. 
        # But since we are inside a job function called periodically, standard ORM usage is usually fine 
        # if the total execution time is short.
        
        # However, for a daemon thread, we should manually close old connections to avoid "server has gone away"
        from django.db import connections
        for conn in connections.all():
            conn.close_if_unusable_or_obsolete()
            
        config = BackupConfiguration.get_solitary()
        if not config.auto_backup:
            return

        last_run = config.last_backup_at
        should_run = False
        
        if not last_run:
            should_run = True
        else:
            delta = timezone.now() - last_run
            days_diff = delta.total_seconds() / 86400.0 # days as float
            
            if config.frequency == 'hourly' and delta.total_seconds() >= 3600:
                should_run = True
            elif config.frequency == 'daily' and days_diff >= 1:
                should_run = True
            elif config.frequency == 'weekly' and days_diff >= 7:
                should_run = True
            elif config.frequency == 'custom' and days_diff >= config.custom_days:
                should_run = True
        
        if should_run:
            print("Running automated backup...")
            BackupService.create_backup(is_auto=True)
            
    except Exception as e:
        print(f"Error in backup scheduler: {e}")
        traceback.print_exc()

def start_scheduler():
    # Loop indefinitely
    while True:
        try:
            job()
        except Exception as e:
            print(f"Scheduler loop error: {e}")
        
        # Sleep for 1 hour (3600 seconds)
        # Checking every hour is sufficient for daily/weekly backups.
        time.sleep(3600)
