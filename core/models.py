from django.db import models
from django.contrib.auth.models import User

class Tool(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class UserToolAccess(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tool_access')
    tools = models.ManyToManyField(Tool, blank=True)

    def __str__(self):
        return f"Access for {self.user.username}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    mobile_number = models.CharField(max_length=20, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    theme_preference = models.CharField(max_length=50, blank=True, null=True, help_text="User-specific theme")

    def __str__(self):
        return f"Profile for {self.user.username}"

class ThemeConfiguration(models.Model):
    global_theme = models.CharField(max_length=50, default='theme-default', help_text="Global default theme")
    
    def __str__(self):
        return f"Global Theme: {self.global_theme}"

    class Meta:
        verbose_name = "Theme Configuration"
        verbose_name_plural = "Theme Configuration"

class NotificationEventSetting(models.Model):
    EVENT_TYPES = [
        ('USER_ADDED', 'New User Added'),
        ('ASSET_UPDATE', 'Asset Added/Updated'),
        ('SIG_CREATED', 'Email Signature Created'),
        
        # HR / Timesheet Events
        ('TIMESHEET_SUBMITTED', 'Timesheet Submitted'),
        ('TIMESHEET_REJECTED', 'Timesheet Rejected'),
        ('TIMESHEET_APPROVED', 'Timesheet Approved'),
        
        # Ticket Events
        ('TICKET_CREATED', 'Ticket Created'),
        ('TICKET_ASSIGNED', 'Ticket Assigned'),
        ('TICKET_STATUS_CHANGED', 'Ticket Status Changed'),
        ('TICKET_COMMENTED', 'Ticket Commented'),
        ('TICKET_BREACHED', 'Ticket SLA Breached'),
        ('TICKET_BREACH_WARNING', 'Ticket Breach Warning (1h Before)'),
        
        # User Account Events
        ('USER_APPROVED', 'User Account Approved'),
        ('USER_REJECTED', 'User Account Rejected'),
        ('USER_TOOL_ACCESS', 'User Tool Permission Granted'),
        
        # System Health Events
        ('SYSTEM_HIGH_LOAD', 'High System Load (>500 Users)'),
        ('SYSTEM_ERROR_SPIKE', 'System Error Spike'),
        ('SYSTEM_DOWNTIME', 'System App Issue/Downtime'),
    ]
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, unique=True)
    subscribers = models.ManyToManyField(User, related_name='notification_subscriptions', blank=True)

    def __str__(self):
        return self.get_event_type_display()

class SystemNotification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To {self.recipient.username}: {self.title}"

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
    ]

    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50)
    object_id = models.CharField(max_length=50, null=True, blank=True)
    object_repr = models.CharField(max_length=200) # Text representation e.g. "User: john_doe"
    data = models.JSONField(null=True, blank=True) # Snapshot for restore
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # Who did it
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} {self.model_name} - {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']

class FeatureFlag(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Unique key for the feature flag")
    is_active = models.BooleanField(default=False, help_text="Global switch for this feature")
    description = models.TextField(blank=True, help_text="What does this feature do?")

    def __str__(self):
        return f"{self.name} ({'ON' if self.is_active else 'OFF'})"

class EmailConfiguration(models.Model):
    email_host = models.CharField(max_length=100, default='smtp.gmail.com')
    email_port = models.IntegerField(default=587)
    email_host_user = models.CharField(max_length=255, help_text="Email ID")
    email_host_password = models.CharField(max_length=255, help_text="App Password")
    email_use_tls = models.BooleanField(default=True)
    default_from_email = models.CharField(max_length=255, blank=True, null=True)
    
    # Singleton pattern enforcement logic can be done in save() or just assumed by always fetching .first()
    
    def __str__(self):
        return f"Email Config: {self.email_host_user}"

    class Meta:
        verbose_name = "Email Configuration"
        verbose_name_plural = "Email Configuration"
