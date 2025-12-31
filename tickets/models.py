from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class DeletedTicketLog(models.Model):
    ticket_id = models.CharField(max_length=20)
    deleted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticket_id} (Deleted {self.deleted_at})"

class Ticket(models.Model):
    PRIORITY_CHOICES = [
        ('P1', 'P1 - Critical'),
        ('P2', 'P2 - High'),
        ('P3', 'P3 - Medium'),
        ('P4', 'P4 - Low'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    ticket_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    issue = models.TextField()
    priority = models.CharField(max_length=2, choices=PRIORITY_CHOICES, default='P3')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    resolution = models.TextField(blank=True, null=True, help_text="Admin resolution notes")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    deadline = models.DateTimeField(null=True, blank=True, help_text="Deadline for the ticket")
    
    SLA_STATUS_CHOICES = [
        ('NORMAL', 'Normal'),
        ('WARNING', 'Warning Sent'),
        ('BREACHED', 'Breach Notified'),
    ]
    sla_status = models.CharField(max_length=20, choices=SLA_STATUS_CHOICES, default='NORMAL')

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            # First save to get the DB-assigned ID (AutoIncrement)
            super().save(*args, **kwargs)
            # Generate ID based on the primary key: PIXL00001
            self.ticket_id = f'PIXL{self.id:05d}'
            # Save again to update the ticket_id
            kwargs['force_insert'] = False # Ensure we update, don't insert again
            return super().save(*args, **kwargs)
        
        # Handle completion timestamp
        if self.status == 'COMPLETED' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'COMPLETED':
            self.completed_at = None
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_id} - {self.user.username}"

    @property
    def is_pending(self):
        return self.status == 'PENDING'

    @property
    def is_in_progress(self):
        return self.status == 'IN_PROGRESS'

    @property
    def is_completed(self):
        return self.status == 'COMPLETED'

    @property
    def is_cancelled(self):
        return self.status == 'CANCELLED'


class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.ticket.ticket_id}"

class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    # Comment is optional: If null, it's a direct ticket attachment (e.g. at creation)
    comment = models.ForeignKey(TicketComment, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)
    file = models.FileField(upload_to='attachments/%Y/%m/%d/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.ticket.ticket_id} by {self.uploaded_by.username}"
