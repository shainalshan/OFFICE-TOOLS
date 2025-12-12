from django.utils import timezone
from django.db import transaction
from .models import PunchLog, Timesheet, TimesheetDailyEntry, EmployeeSettings
import datetime
from decimal import Decimal

def get_or_create_timesheet(user, month_date):
    """
    Get or create a timesheet container for the given month.
    month_date: A date object (any day in the target month)
    """
    # Calculate start and end of month
    start_date = month_date.replace(day=1)
    # Get last day of month
    next_month = start_date.replace(day=28) + datetime.timedelta(days=4)
    end_date = next_month - datetime.timedelta(days=next_month.day)
    
    timesheet, created = Timesheet.objects.get_or_create(
        employee=user,
        period_start=start_date,
        defaults={
            'period_end': end_date
        }
    )
    return timesheet

def calculate_daily_hours(punches):
    """
    Calculate total hours from a list of sorted PunchLog objects for a single day.
    Logic: Strictly First IN to Last OUT (Gross Hours), ignoring breaks.
    """
    if not punches:
        return Decimal('0.00')

    # Find First IN
    first_in = None
    for p in punches:
        if p.type == 'IN':
            first_in = p.timestamp
            break
            
    # Find Last OUT
    last_out = None
    # Iterate backwards
    for p in reversed(punches):
        if p.type == 'OUT':
            last_out = p.timestamp
            break
            
    if first_in and last_out and last_out > first_in:
        diff = last_out - first_in
        return Decimal(diff.total_seconds() / 3600).quantize(Decimal('0.01'))
    
    return Decimal('0.00')

def generate_timesheet_entries(timesheet):
    """
    Populate or update TimesheetDailyEntry records for the timesheet period.
    """
    # Get all logs for the period
    all_logs = PunchLog.objects.filter(
        user=timesheet.employee,
        timestamp__date__gte=timesheet.period_start,
        timestamp__date__lte=timesheet.period_end
    ).order_by('timestamp')
    
    # Group by date
    logs_by_date = {}
    for log in all_logs:
        d = log.timestamp.date()
        if d not in logs_by_date:
            logs_by_date[d] = []
        logs_by_date[d].append(log)
        
    # Iterate through every day in the month
    current_date = timesheet.period_start
    today = timezone.now().date()
    
    while current_date <= timesheet.period_end:
        # Skip future dates
        if current_date > today:
            current_date += datetime.timedelta(days=1)
            continue
            
        day_logs = logs_by_date.get(current_date, [])
        
        # Check for existing manual entry
        existing_entry = TimesheetDailyEntry.objects.filter(timesheet=timesheet, date=current_date).first()
        
        if existing_entry and existing_entry.is_manual_adjustment:
            # If manually adjusted, DO NOT overwrite status or hours with punch logs.
            # We respect the manual override fully.
            current_date += datetime.timedelta(days=1)
            continue
            


        # Determine status
        is_weekend = current_date.weekday() >= 5 # 5=Sat, 6=Sun
        status = 'ABSENT'
        hours = Decimal('0.00')
        first_in = None
        last_out = None
        
        if day_logs:
            status = 'PRESENT'
            hours = calculate_daily_hours(day_logs)
            
            # Find First In / Last Out for display
            ins = [p for p in day_logs if p.type == 'IN']
            outs = [p for p in day_logs if p.type == 'OUT']
            
            if ins:
                first_in = ins[0].timestamp.time()
            if outs:
                last_out = outs[-1].timestamp.time()
        elif is_weekend:
            status = 'WEEK_OFF'
        
        # Update or Create Entry
        entry, _ = TimesheetDailyEntry.objects.update_or_create(
            timesheet=timesheet,
            date=current_date,
            defaults={
                'first_punch_in': first_in,
                'last_punch_out': last_out,
                'total_hours': hours,
                'status': status
            }
        )
        
        current_date += datetime.timedelta(days=1)
