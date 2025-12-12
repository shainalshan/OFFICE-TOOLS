from django.db import models
from django.conf import settings
from django.utils import timezone
import datetime

class EmployeeSettings(models.Model):
    """
    Settings for an employee's HR portal access and behavior.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hr_settings')
    is_hr_admin = models.BooleanField(default=False, help_text="Can approve/reject timesheets and manage HR settings.")
    requires_timesheet = models.BooleanField(default=True, help_text="If True, this user must submit timesheets.")
    timesheet_enabled = models.BooleanField(default=False, help_text="If True, user can access the punch in/out system.")
    
    # Weekly Off Settings (Default Sat/Sun)
    # We can expand this later to be more flexible, but for now logic will handle it.
    
    def __str__(self):
        return f"HR Settings for {self.user.username}"

class PunchLog(models.Model):
    """
    Raw log of every punch in/out action.
    """
    PUNCH_TYPES = (
        ('IN', 'Punch In'),
        ('OUT', 'Punch Out'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='punches')
    timestamp = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=3, choices=PUNCH_TYPES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_manual_entry = models.BooleanField(default=False, help_text="True if added by HR manually.")
    note = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.user.username} - {self.type} at {self.timestamp}"

class Timesheet(models.Model):
    """
    Monthly timesheet container.
    """
    STATUS_CHOICES = (
        ('PENDING', 'Pending Submission'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='timesheets')
    period_start = models.DateField(help_text="First day of the month")
    period_end = models.DateField(help_text="Last day of the month")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_timesheets')
    rejection_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('employee', 'period_start')
        ordering = ['-period_start']
        
    def __str__(self):
        return f"Timesheet: {self.employee.username} ({self.period_start.strftime('%b %Y')})"

class TimesheetDailyEntry(models.Model):
    """
    Compiled daily line item for a timesheet.
    """
    STATUS_CHOICES = (
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('WEEK_OFF', 'Week Off'),
        ('HOLIDAY', 'Holiday'),
        ('SICK_LEAVE', 'Sick Leave'),
        ('ANNUAL_LEAVE', 'Annual Leave'),
        ('WFH', 'Work From Home'),
    )
    
    timesheet = models.ForeignKey(Timesheet, on_delete=models.CASCADE, related_name='entries')
    date = models.DateField()
    first_punch_in = models.TimeField(null=True, blank=True)
    last_punch_out = models.TimeField(null=True, blank=True)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABSENT')
    is_manual_adjustment = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('timesheet', 'date')
        ordering = ['date']
        
    def __str__(self):
        return f"{self.timesheet.employee.username} - {self.date} - {self.status}"
