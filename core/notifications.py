import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from .models import NotificationEventSetting, SystemNotification, EmailConfiguration
from .email_utils import send_dynamic_email
import waffle

logger = logging.getLogger(__name__)

def send_event_notification(event_type, context, functional_recipients=None):
    """
    Centralized function to handle event notifications.
    
    Args:
        event_type (str): The code from NotificationEventSetting (e.g., 'TICKET_CREATED')
        context (dict): Data to be used in the email/notification message (e.g., {'ticket': t, 'actor': user})
        functional_recipients (list, optional): Users who *must* receive this (e.g., ticket owner).
    """
    if functional_recipients is None:
        functional_recipients = []
        
    # 1. Get Notification Setting
    try:
        setting = NotificationEventSetting.objects.get(event_type=event_type)
        subscribers = list(setting.subscribers.all())
    except NotificationEventSetting.DoesNotExist:
        subscribers = []
        # We continue even if setting doesn't exist, to support functional_recipients
        logger.warning(f"Notification Setting {event_type} not found. Only sending to functional recipients.")

    # 2. Merge Recipients (Avoid duplicates)
    # Using a dictionary by ID to ensure uniqueness
    recipient_map = {u.id: u for u in functional_recipients if u.email}
    for sub in subscribers:
        if sub.email:
            recipient_map[sub.id] = sub
            
    all_recipients = list(recipient_map.values())
    
    if not all_recipients:
        return

    # 3. Generate Content
    subject, message, in_app_message, link = generate_content(event_type, context)
    
    # 4. Send Emails
    recipient_emails = [u.email for u in all_recipients]
    
    # -- Dynamic Email Config Check --
    # We fetch request from context if available, or just check flag globally? 
    # Waffle request-flag check usually needs request object. 
    # For now, we'll try-catch or assume static if no request.
    # Actually, we can check if EmailConfiguration exists.
    
    try:
        if EmailConfiguration.objects.exists():
             # Use dynamic sender
             send_dynamic_email(subject, message, recipient_emails)
        else:
            # Fallback to Django settings
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_emails,
                fail_silently=True
            )
        logger.info(f"Sent {event_type} notification to {len(recipient_emails)} recipients.")
    except Exception as e:
        logger.error(f"Failed to send email for {event_type}: {e}")

    # 5. Create System Notifications (In-App)
    # Different logic: Subscribers might want in-app? Functional users definitely want in-app.
    # Let's send to all for now.
    for user in all_recipients:
        SystemNotification.objects.create(
            recipient=user,
            title=subject, # Or a shorter title?
            message=in_app_message,
            link=link
        )

def generate_content(event_type, context):
    """
    Returns (subject, email_message, in_app_message, link) based on event type.
    """
    subject = "Notification"
    message = "You have a new notification."
    in_app_message = message
    link = "/dashboard/"
    
    # --- TICKET EVENTS ---
    if event_type == 'TICKET_CREATED':
        ticket = context.get('ticket')
        subject = f"[Ticket #{ticket.ticket_id}] Created: {ticket.issue[:50]}..."
        message = f"""
        A new ticket has been created.
        
        ID: {ticket.ticket_id}
        Created By: {ticket.user.username}
        Priority: {ticket.get_priority_display()}
        
        Issue:
        {ticket.issue}
        """
        in_app_message = f"New Ticket {ticket.ticket_id} by {ticket.user.username}: {ticket.issue[:30]}..."
        link = f"/tickets/detail/{ticket.ticket_id}/"

    elif event_type == 'TICKET_ASSIGNED':
        ticket = context.get('ticket')
        assignee_name = ticket.assigned_to.username if ticket.assigned_to else "Unassigned"
        subject = f"[Ticket #{ticket.ticket_id}] Assigned to {assignee_name}"
        message = f"Ticket {ticket.ticket_id} has been assigned to {assignee_name}."
        in_app_message = f"Ticket {ticket.ticket_id} assigned to {assignee_name}."
        link = f"/tickets/detail/{ticket.ticket_id}/"

    elif event_type == 'TICKET_STATUS_CHANGED':
        ticket = context.get('ticket')
        subject = f"[Ticket #{ticket.ticket_id}] Status Updated: {ticket.get_status_display()}"
        message = f"Ticket {ticket.ticket_id} status changed to {ticket.get_status_display()}."
        in_app_message = f"Ticket {ticket.ticket_id} is now {ticket.get_status_display()}."
        link = f"/tickets/detail/{ticket.ticket_id}/"

    elif event_type == 'TICKET_COMMENTED':
        ticket = context.get('ticket')
        comment_user = context.get('actor')
        subject = f"[Ticket #{ticket.ticket_id}] New Comment by {comment_user.username}"
        message = f"{comment_user.username} commented on Ticket {ticket.ticket_id}."
        in_app_message = f"New comment on {ticket.ticket_id} by {comment_user.username}."
        link = f"/tickets/detail/{ticket.ticket_id}/"
        
    elif event_type == 'TICKET_BREACHED':
        ticket = context.get('ticket')
        subject = f"[SLA BREACH] Ticket #{ticket.ticket_id} has breached deadline!"
        message = f"URGENT: Ticket {ticket.ticket_id} missed its deadline of {ticket.deadline}."
        in_app_message = f"Background Alert: Ticket {ticket.ticket_id} breached SLA!"
        link = f"/tickets/detail/{ticket.ticket_id}/"

    elif event_type == 'TICKET_BREACH_WARNING':
        ticket = context.get('ticket')
        subject = f"[SLA WARNING] Ticket #{ticket.ticket_id} breaching in <1 hour"
        message = f"Warning: Ticket {ticket.ticket_id} is approaching its deadline ({ticket.deadline})."
        in_app_message = f"Warning: Ticket {ticket.ticket_id} deadline near."
        link = f"/tickets/detail/{ticket.ticket_id}/"

    # --- HR EVENTS ---
    elif event_type == 'TIMESHEET_SUBMITTED':
        timesheet = context.get('timesheet')
        user = timesheet.employee
        subject = f"Timesheet Submitted: {user.username} - {timesheet.period_start.strftime('%B %Y')}"
        message = f"{user.first_name} has submitted their timesheet for {timesheet.period_start.strftime('%B %Y')}."
        in_app_message = message
        link = f"/hr/timesheet/view/{timesheet.id}/"

    elif event_type == 'TIMESHEET_APPROVED':
        timesheet = context.get('timesheet')
        subject = f"Timesheet Approved: {timesheet.period_start.strftime('%B %Y')}"
        message = f"Your timesheet for {timesheet.period_start.strftime('%B %Y')} has been approved."
        in_app_message = message
        link = f"/hr/timesheet/view/{timesheet.id}/"
        
    elif event_type == 'TIMESHEET_REJECTED':
        timesheet = context.get('timesheet')
        subject = f"Timesheet Rejected: {timesheet.period_start.strftime('%B %Y')}"
        message = f"Your timesheet for {timesheet.period_start.strftime('%B %Y')} was rejected. Reason: {timesheet.rejection_reason}"
        in_app_message = message
        link = f"/hr/timesheet/view/{timesheet.id}/"

    # --- USER EVENTS ---
    elif event_type == 'USER_APPROVED':
        user = context.get('user')
        subject = "Account Approved - Office Portal"
        message = f"Hello {user.username},\n\nYour account has been approved. You can now login."
        in_app_message = "Your active account is now active." # Redundant for valid user but good log
        link = "/dashboard/"
        
    elif event_type == 'USER_REJECTED':
        # Provide username as string since user object might be deleted
        username = context.get('username') 
        subject = "Account Application Rejected"
        message = f"Hello {username},\n\nYour account application was rejected. Please contact admin."
        in_app_message = "Rejected user."
        link = "#"

    # --- SYSTEM ---
    elif event_type == 'SYSTEM_HIGH_LOAD':
        count = context.get('count')
        subject = f"[ALERT] High System Load: {count} Users"
        message = f"Warning: Active user count has reached {count}."
        in_app_message = message
        link = "/dashboard/"

    return subject, message, in_app_message, link
