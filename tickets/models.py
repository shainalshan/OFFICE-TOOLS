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

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            # 1. Check for recycled ID (deleted within last 3 days)
            three_days_ago = timezone.now() - timedelta(days=3)
            recycled = DeletedTicketLog.objects.filter(deleted_at__gte=three_days_ago).order_by('deleted_at').first()

            if recycled:
                self.ticket_id = recycled.ticket_id
                recycled.delete() # Consume the ID so it's not used again
            else:
                # 2. Generate new ID: PIXL00001
                last_ticket = Ticket.objects.order_by('-id').first()
                if last_ticket:
                    last_id = int(last_ticket.id)
                    new_id = last_id + 1
                else:
                    new_id = 1
                self.ticket_id = f'PIXL{new_id:05d}'
        
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
