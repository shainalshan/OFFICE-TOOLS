from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core import serializers
import json

from assets.models import Asset
from contacts.models import Contact
from .models import NotificationEventSetting, SystemNotification, AuditLog
from .middleware import get_current_user

# --- Helper to log actions ---
def create_audit_log(instance, action):
    # Skip logging AuditLog entries themselves to avoid loops
    if isinstance(instance, AuditLog):
        return
        
    try:
        # Serialize data
        data = serializers.serialize('json', [instance])
        data_json = json.loads(data)[0]['fields']
        # Add ID manually as it's often not in fields
        data_json['id'] = instance.id
        
        model_name = instance._meta.model_name
        object_repr = str(instance)
        
        user = get_current_user()
        if user and not user.is_authenticated:
            user = None
            
        AuditLog.objects.create(
            action=action,
            model_name=model_name,
            object_id=str(instance.id),
            object_repr=object_repr,
            data=data_json,
            user=user
        )
    except Exception as e:
        print(f"Error creating audit log: {e}")

# --- Signals ---

@receiver(post_save, sender=User)
@receiver(post_save, sender=Asset)
@receiver(post_save, sender=Contact)
def log_save(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'
    create_audit_log(instance, action)

@receiver(post_delete, sender=User)
@receiver(post_delete, sender=Asset)
@receiver(post_delete, sender=Contact)
def log_delete(sender, instance, **kwargs):
    create_audit_log(instance, 'DELETE')

# 1. New User Added (Legacy Notification)
@receiver(post_save, sender=User)
def notify_new_user(sender, instance, created, **kwargs):
    if created:
        try:
            setting = NotificationEventSetting.objects.get(event_type='USER_ADDED')
            subscribers = set(setting.subscribers.all())
        except NotificationEventSetting.DoesNotExist:
            subscribers = set()
            
        # Add all superusers by default
        superusers = set(User.objects.filter(is_superuser=True))
        recipients = subscribers | superusers
        
        for user in recipients:
            SystemNotification.objects.create(
                recipient=user,
                title="New User Joined",
                message=f"New user {instance.username} ({instance.email}) has been added to the system.",
                link=f"/dashboard/"
            )

# 2. Asset Added/Updated (Legacy Notification)
@receiver(post_save, sender=Asset)
def notify_asset_update(sender, instance, created, **kwargs):
    try:
        setting = NotificationEventSetting.objects.get(event_type='ASSET_UPDATE')
        subscribers = set(setting.subscribers.all())
    except NotificationEventSetting.DoesNotExist:
        subscribers = set()
        
    # Add all superusers by default
    superusers = set(User.objects.filter(is_superuser=True))
    recipients = subscribers | superusers
    
    action = "added" if created else "updated"
    
    for user in recipients:
        SystemNotification.objects.create(
            recipient=user,
            title=f"Asset {action.title()}",
            message=f"Asset '{instance.brand} {instance.model_detail}' ({instance.serial_number}) was {action}.",
            link=f"/assets/?tab={instance.location}"
        )
