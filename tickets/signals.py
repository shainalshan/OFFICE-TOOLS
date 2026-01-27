from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Ticket, TicketComment
from core.models import NotificationEventSetting

import threading

def send_ticket_notification(event_type, ticket, affected_user=None, extra_context=None):
    """
    Sends email notification to subscribers who are relevant to the ticket.
    Relevant = Creator or Assignee.
    Run asynchronously to prevent UI blocking.
    """
    def _send_email_thread():
        try:
            # Re-fetch settings/subs inside thread or pass them? passing is better if data is loaded.
            # But query inside thread is safer if objects might be stale, though here specific event type is static.
            # However, DB connections in threads can be tricky in Django without proper management if not careful.
            # BUT: Simple select is usually okay if connection is valid. 
            # Safer: do the logic that needs DB *before* thread if possible, OR ensure connection allowed.
            # Best for simple: Do queries in thread, Django closes per-thread connections usually.
            
            # Let's do the easy way: Pass strictly data if possible, or careful with DB.
            # Actually, queries are fine in threads in Django.
            
            notification_setting = NotificationEventSetting.objects.get(event_type=event_type)
            subscribers = notification_setting.subscribers.all()

            if not subscribers.exists():
                return

            subject_map = {
                'TICKET_CREATED': f'New Ticket: {ticket.ticket_id} - {ticket.issue[:30]}...',
                'TICKET_ASSIGNED': f'Ticket Assigned: {ticket.ticket_id}',
                'TICKET_STATUS_CHANGED': f'Ticket Status Update: {ticket.ticket_id} ({ticket.get_status_display()})',
                'TICKET_COMMENTED': f'New Comment on Ticket: {ticket.ticket_id}',
            }

            subject = subject_map.get(event_type, f'Ticket Notification: {ticket.ticket_id}')
            
            # Construct Message
            message = f"""
            Event: {notification_setting.get_event_type_display()}
            Ticket ID: {ticket.ticket_id}
            Status: {ticket.get_status_display()}
            Priority: {ticket.get_priority_display()}
            Creator: {ticket.user.username}
            Assigned To: {ticket.assigned_to.username if ticket.assigned_to else 'Unassigned'}
            
            Issue:
            {ticket.issue}
            """
            
            if extra_context:
                message += f"\n\n{extra_context}"
                
            message += "\n\nLogin to the dashboard to view more details."

            recipients = []
            
            for sub in subscribers:
                is_relevant = (sub == ticket.user) or (sub == ticket.assigned_to)
                
                if is_relevant and sub.email:
                    recipients.append(sub.email)

            if recipients:
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        recipients,
                        fail_silently=True
                    )
                    print(f"Email sent to {recipients} for {event_type}")
                except Exception as e:
                    print(f"Error sending email: {e}")
        except Exception as e:
            print(f"Thread Error: {e}")

    # Start independent thread
    threading.Thread(target=_send_email_thread).start()

@receiver(post_save, sender=Ticket)
def ticket_lifecycle_notification(sender, instance, created, **kwargs):
    # DISABLED: Redundant. Views now handle notifications via core.notifications
    pass

@receiver(post_save, sender=TicketComment)
def ticket_comment_notification(sender, instance, created, **kwargs):
    # DISABLED: Redundant. Views now handle notifications via core.notifications
    pass
