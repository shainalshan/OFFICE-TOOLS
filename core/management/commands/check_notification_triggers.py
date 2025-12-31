from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from tickets.models import Ticket
from core.notifications import send_event_notification
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Checks for system events like SLA breaches and triggers notifications'

    def handle(self, *args, **options):
        self.stdout.write("Checking notification triggers...")
        now = timezone.now()
        
        # --- 1. Ticket SLA Warnings (< 1 hour left) ---
        # Find tickets where deadline is in the future but less than 1 hour away
        warning_threshold = now + timedelta(hours=1)
        
        # Tickets that are OPEN, have a deadline, are NOT breached/warned, and deadline is within window
        tickets_to_warn = Ticket.objects.filter(
            status__in=['PENDING', 'IN_PROGRESS'],
            deadline__isnull=False,
            # deadline__gt=now, # Still in future
            # deadline__lte=warning_threshold, # But closing in
            sla_status='NORMAL' # Only if not already warned
        )
        
        # Precise filtering in python or DB? DB is better.
        # We want deadline in range [now, now+1h]
        tickets_to_warn = tickets_to_warn.filter(deadline__range=(now, warning_threshold))
        
        for ticket in tickets_to_warn:
            self.stdout.write(f"Sending warning for Ticket {ticket.ticket_id}")
            ticket.sla_status = 'WARNING'
            ticket.save()
            
            # Recipients: Owner + Assignee + Admins (Subscribers)
            recipients = []
            if ticket.assigned_to: recipients.append(ticket.assigned_to)
            # send_event_notification handles merging with subscribers
            send_event_notification('TICKET_BREACH_WARNING', {'ticket': ticket}, functional_recipients=recipients)

        # --- 2. Ticket SLA Breaches (Deadline Passed) ---
        tickets_breached = Ticket.objects.filter(
            status__in=['PENDING', 'IN_PROGRESS'],
            deadline__isnull=False,
            deadline__lt=now, # Passed
            sla_status__in=['NORMAL', 'WARNING'] # Not yet marked triggered
        )
        
        for ticket in tickets_breached:
            self.stdout.write(f"BREACH DETECTED: Ticket {ticket.ticket_id}")
            ticket.sla_status = 'BREACHED'
            ticket.save()
            
            recipients = []
            if ticket.assigned_to: recipients.append(ticket.assigned_to)
             # Owner usually wants to know if they wait too long? Maybe. 
             # Breach is mostly for Admins/Assignees to panic.
            
            send_event_notification('TICKET_BREACHED', {'ticket': ticket}, functional_recipients=recipients)

        # --- 3. System Load Check ---
        # Simulating "Active Users" by checking active session count or just total Active users for now.
        # Real "Concurrent" check requires session engine. 
        # Using a simple "Users with recent login" heuristic if `last_login` was reliable.
        # Or just 'is_active' count for the requirement ">500 users".
        # Requirement says: "Active > 500".
        user_count = User.objects.filter(is_active=True).count()
        if user_count > 500:
            # We don't want to spam every minute.
            # We need a state store. Waffle flag or Cache?
            # Or just send it. If cron runs every 5 min, 1 email every 5 min is annoying but acceptable for critical load.
            self.stdout.write(f"High System Load: {user_count} users.")
            # Only trigger if configured
            send_event_notification('SYSTEM_HIGH_LOAD', {'count': user_count})

        self.stdout.write(self.style.SUCCESS('Notification check completed.'))
