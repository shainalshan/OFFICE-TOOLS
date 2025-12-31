from django.db import models
import os

class BackupConfiguration(models.Model):
    FREQUENCY_CHOICES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('custom', 'Custom Days'),
    ]

    auto_backup = models.BooleanField(default=False)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='daily')
    custom_days = models.IntegerField(default=1, help_text="Number of days for custom frequency")
    retention_days = models.IntegerField(default=30, help_text="Number of days to keep backups")
    backup_path = models.CharField(max_length=500, default='backups', help_text="Relative to project root or absolute path")
    email_notifications = models.BooleanField(default=False)
    email_files_only = models.BooleanField(default=False, help_text="Send email only if files are backed up? Or maybe attach files? Assuming notification config.")
    last_backup_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Singleton pattern: ensure only one config exists
        if not self.pk and BackupConfiguration.objects.exists():
            # If you try to create a new one, update the existing one instead
            return
        return super(BackupConfiguration, self).save(*args, **kwargs)

    @classmethod
    def get_solitary(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Backup Configuration"

class BackupLog(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    file_path = models.CharField(max_length=500)
    file_size = models.CharField(max_length=50) # Human readable size
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success')
    backup_type = models.CharField(max_length=10, choices=[('full', 'Full System'), ('file', 'File Only')], default='full')
    error_message = models.TextField(blank=True, null=True)

    def filename(self):
        return os.path.basename(self.file_path)

    def __str__(self):
        return f"Backup {self.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {self.status}"
