from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal
from .models import EmployeeSettings, PunchLog, Timesheet, TimesheetDailyEntry
import datetime

from .services import get_or_create_timesheet, generate_timesheet_entries
from django.contrib.auth import get_user_model
from core.models import SystemNotification, NotificationEventSetting

User = get_user_model()

@login_required
def staff_portal(request):
    """
    Main dashboard for staff. Shows punch button and today's status.
    """
    # Ensure settings exist
    settings, _ = EmployeeSettings.objects.get_or_create(user=request.user)
    
    # Auto-generate timesheet data for display
    today = timezone.now().date()
    # Only generate if timesheet enabled
    if settings.timesheet_enabled:
        ts = get_or_create_timesheet(request.user, today)
        generate_timesheet_entries(ts)
    
    # Get today's punches
    todays_punches = PunchLog.objects.filter(
        user=request.user, 
        timestamp__date=today
    ).order_by('timestamp')
    
    # Determine current state
    is_punched_in = False
    last_punch = todays_punches.last()
    if last_punch and last_punch.type == 'IN':
        is_punched_in = True
        
    today_punches_list = list(todays_punches)
    first_punch_in = None
    for p in today_punches_list:
        if p.type == 'IN':
            first_punch_in = p.timestamp
            break

    context = {
        'is_punched_in': is_punched_in,
        'todays_punches': todays_punches,
        'settings': settings,
        'current_time': timezone.now(),
        'first_punch_in': first_punch_in,
    }
    return render(request, 'hr/staff_portal.html', context)

@login_required
def punch_in_out(request):
    """
    API to handle punching.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
    
    settings, _ = EmployeeSettings.objects.get_or_create(user=request.user)
    if not settings.timesheet_enabled:
         return JsonResponse({'status': 'error', 'message': 'Timesheet access disabled.'}, status=403)

    # Check last punch to prevent double punching
    last_punch = PunchLog.objects.filter(user=request.user).order_by('-timestamp').first()
    
    # Determine expected type
    new_type = 'IN'
    if last_punch and last_punch.type == 'IN':
        new_type = 'OUT'
    
    # Create log
    PunchLog.objects.create(
        user=request.user,
        type=new_type,
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    return JsonResponse({
        'status': 'success',
        'new_state': 'OUT' if new_type == 'IN' else 'IN', # Return what the button SHOULD show next? No, return current state.
        'message': f'Successfully punched {new_type}'
    })

@login_required
def punch_history(request):
    logs = PunchLog.objects.filter(user=request.user).order_by('-timestamp')[:50]
    return render(request, 'hr/punch_history.html', {'logs': logs})

# --- Timesheet Placeholders ---
@login_required
def current_timesheet(request):
    month_param = request.GET.get('month') # Format: YYYY-MM
    if month_param:
        try:
             target_date = datetime.datetime.strptime(month_param, '%Y-%m').date()
        except ValueError:
             target_date = timezone.now().date()
    else:
        target_date = timezone.now().date()
        
    timesheet = get_or_create_timesheet(request.user, target_date)
    
    # Refresh calculations
    generate_timesheet_entries(timesheet)
    
    # Get entries
    entries = timesheet.entries.all().order_by('date')
    
    # Calculate total hours (simple aggregation for display)
    total_period_hours = sum(e.total_hours for e in entries)
    
    context = {
        'timesheet': timesheet,
        'entries': entries,
        'total_period_hours': total_period_hours
    }
    return render(request, 'hr/timesheet_view.html', context)

@login_required
def update_timesheet_entry(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
        
    entry_id = request.POST.get('entry_id')
    new_status = request.POST.get('status')
    
    # New time fields
    first_in_str = request.POST.get('first_in')
    last_out_str = request.POST.get('last_out')
    
    if not entry_id or not new_status:
        return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)
        
    # Get entry and verify ownership
    entry = get_object_or_404(TimesheetDailyEntry, id=entry_id)
    if entry.timesheet.employee != request.user:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
        
    # Validation
    valid_statuses = [c[0] for c in TimesheetDailyEntry.STATUS_CHOICES]
    if new_status not in valid_statuses:
         return JsonResponse({'status': 'error', 'message': 'Invalid status'}, status=400)

    first_in_str = request.POST.get('first_in')
    last_out_str = request.POST.get('last_out')

    # Apply Status
    entry.status = new_status
    entry.is_manual_adjustment = True
    
    # Handle Manual Times
    if first_in_str:
        try:
             entry.first_punch_in = datetime.datetime.strptime(first_in_str, '%H:%M').time()
        except ValueError:
             pass # Invalid format, ignore or handle error
    
    if last_out_str:
        try:
             entry.last_punch_out = datetime.datetime.strptime(last_out_str, '%H:%M').time()
        except ValueError:
             pass

    # Recalculate Hours if we have both
    # Or if we have punches now set manually
    # Note: If status is ABSENT/LEAVE, we force 0 usually.
    # But if user is manually editing to PRESENT with times, we calculate.
    
    if new_status in ['ABSENT', 'HOLIDAY', 'SICK_LEAVE', 'ANNUAL_LEAVE', 'WEEK_OFF']:
        entry.total_hours = Decimal('0.00')
    else:
        # Try to calculate hours from manual punches
        if entry.first_punch_in and entry.last_punch_out:
             # Basic calc: out - in
             # Use dummy dates for subtraction
             dummy_date = datetime.date(2000, 1, 1)
             dt_in = datetime.datetime.combine(dummy_date, entry.first_punch_in)
             dt_out = datetime.datetime.combine(dummy_date, entry.last_punch_out)
             
             if dt_out > dt_in:
                 diff = dt_out - dt_in
                 hours = Decimal(diff.total_seconds() / 3600)
                 entry.total_hours = round(hours, 2)
             else:
                 # negative time? maybe across midnight (not handled simple here)
                 entry.total_hours = Decimal('0.00')
    
    entry.save()
    
    return JsonResponse({'status': 'success', 'message': 'Entry updated'})

@login_required
def submit_timesheet(request):
    if request.method == 'POST':
        # Get pending OR rejected timesheet for current month/user
        # Simplified: find the first PENDING or REJECTED timesheet or specific one if ID passed
        timesheet = Timesheet.objects.filter(employee=request.user, status__in=['PENDING', 'REJECTED']).first()
        if timesheet:
            timesheet.status = 'SUBMITTED'
            timesheet.submitted_at = timezone.now()
            timesheet.save()
            
            # Trigger Notification
            try:
                setting = NotificationEventSetting.objects.get(event_type='TIMESHEET_SUBMITTED')
                for sub in setting.subscribers.all():
                    SystemNotification.objects.create(
                        recipient=sub,
                        title='Timesheet Submitted',
                        message=f"{request.user.first_name} {request.user.last_name} submitted timesheet for {timesheet.period_start.strftime('%B %Y')}.",
                        link=f"/hr/timesheet/view/{timesheet.id}/"
                    )
            except Exception as e:
                print(f"Notification Error: {e}")

            messages.success(request, "Timesheet submitted for approval.")
        else:
            messages.error(request, "No pending timesheet found to submit.")
            
    return redirect('hr_staff_portal')

@login_required
def handle_timesheet_approval(request):
    """
    Handle Approve/Reject actions from HR Admin
    """
    if not (request.user.is_superuser or (hasattr(request.user, 'hr_settings') and request.user.hr_settings.is_hr_admin)):
        messages.error(request, "Permission denied.")
        return redirect('home')

    if request.method == 'POST':
        timesheet_id = request.POST.get('timesheet_id')
        action = request.POST.get('action') # 'approve' or 'reject'
        rejection_reason = request.POST.get('rejection_reason', '')
        
        timesheet = get_object_or_404(Timesheet, id=timesheet_id)
        
        if action == 'approve':
            timesheet.status = 'APPROVED'
            timesheet.reviewed_at = timezone.now()
            timesheet.reviewed_by = request.user
            timesheet.save()

            # Notification (Direct to Employee)
            try:
                SystemNotification.objects.create(
                    recipient=timesheet.employee,
                    title='Timesheet Approved',
                    message=f"Your timesheet for {timesheet.period_start.strftime('%B %Y')} has been approved by {request.user.first_name} {request.user.last_name}.",
                    link=f"/hr/timesheet/view/{timesheet.id}/"
                )
            except Exception as e:
                print(f"Notification Error: {e}")

            messages.success(request, f"Timesheet for {timesheet.employee.username} APPROVED.")
            
        elif action == 'reject':
            timesheet.status = 'REJECTED'
            timesheet.reviewed_at = timezone.now()
            timesheet.reviewed_by = request.user
            timesheet.rejection_reason = rejection_reason
            timesheet.save()

            # Notification (Direct to Employee)
            try:
                SystemNotification.objects.create(
                    recipient=timesheet.employee,
                    title='Timesheet Rejected',
                    message=f"Your timesheet for {timesheet.period_start.strftime('%B %Y')} was rejected. Reason: {rejection_reason}",
                    link=f"/hr/timesheet/view/{timesheet.id}/"
                )
            except Exception as e:
                print(f"Notification Error: {e}")

            messages.warning(request, f"Timesheet for {timesheet.employee.username} REJECTED.")
            
    return redirect('hr_admin_dashboard')

# --- Admin Views ---
from django.db.models import Q # Added for search

@login_required
def hr_admin_dashboard(request):
    # Check permission
    has_access = False
    if request.user.is_superuser:
        has_access = True
    elif hasattr(request.user, 'hr_settings') and request.user.hr_settings.is_hr_admin:
        has_access = True
        
    if not has_access:
        messages.error(request, "Access Denied: HR Admins only.")
        return redirect('home')
    
    # Handle Form Actions (Toggle Permissions)
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        
        if user_id:
            target_user = get_object_or_404(User, id=user_id)
            settings, _ = EmployeeSettings.objects.get_or_create(user=target_user)
            
            if action == 'toggle_timesheet':
                settings.timesheet_enabled = not settings.timesheet_enabled
                settings.save()
                messages.success(request, f"Timesheet access for {target_user.username} is now {'ENABLED' if settings.timesheet_enabled else 'DISABLED'}.")
            elif action == 'toggle_hr':
                settings.is_hr_admin = not settings.is_hr_admin
                settings.save()
                messages.success(request, f"HR Admin access for {target_user.username} is now {'GRANTED' if settings.is_hr_admin else 'REVOKED'}.")
                
        return redirect('hr_admin_dashboard')

    # Ensure all users have settings created so the template doesn't crash
    # ONLY fetch users for Superusers (Employee Access Management)
    user_list = []
    query = request.GET.get('q')

    if request.user.is_superuser:
        all_known_users = User.objects.all().order_by('username')
        
        if query:
            all_known_users = all_known_users.filter(
                Q(username__icontains=query) | 
                Q(first_name__icontains=query) | 
                Q(last_name__icontains=query)
            )
        
        for u in all_known_users:
            # get_or_create forces creation if missing, preventing RelatedObjectDoesNotExist
            s, _ = EmployeeSettings.objects.get_or_create(user=u)
            # Attach strictly for template usage (though u.hr_settings works now)
            u.cached_settings = s 
            user_list.append(u)
        
    # FETCH SUBMITTED TIMESHEETS FOR APPROVAL
    submitted_timesheets = Timesheet.objects.filter(status='SUBMITTED')
    
    # Search for Pending Approvals
    search_pending = request.GET.get('search_pending')
    if search_pending:
        submitted_timesheets = submitted_timesheets.filter(
            Q(employee__username__icontains=search_pending) |
            Q(employee__first_name__icontains=search_pending) |
            Q(employee__last_name__icontains=search_pending)
        )
        
    submitted_timesheets = submitted_timesheets.order_by('submitted_at')
    
    # FETCH APPROVED TIMESHEETS
    approved_timesheets = Timesheet.objects.filter(status='APPROVED')
    
    # Search for Approved
    search_approved = request.GET.get('search_approved')
    if search_approved:
        approved_timesheets = approved_timesheets.filter(
            Q(employee__username__icontains=search_approved) |
            Q(employee__first_name__icontains=search_approved) |
            Q(employee__last_name__icontains=search_approved)
        )
        
    # Date Filter for Approved (Month)
    date_approved = request.GET.get('date_approved') # Format YYYY-MM
    if date_approved:
        try:
            filter_date = datetime.datetime.strptime(date_approved, '%Y-%m').date()
            approved_timesheets = approved_timesheets.filter(
                period_start__year=filter_date.year,
                period_start__month=filter_date.month
            )
        except ValueError:
            pass
            
    approved_timesheets = approved_timesheets.order_by('-reviewed_at')
    
    context = {
        'users': user_list, 
        'search_query': query,
        'search_pending': search_pending,
        'search_approved': search_approved,
        'date_approved': date_approved,
        'submitted_timesheets': submitted_timesheets,
        'approved_timesheets': approved_timesheets
    }
    
    return render(request, 'hr/admin_dashboard.html', context)

@login_required
def admin_view_timesheet(request, timesheet_id):
    """
    Read-only view for Admins to inspect a specific timesheet.
    """
    # Permission check
    if not (request.user.is_superuser or (hasattr(request.user, 'hr_settings') and request.user.hr_settings.is_hr_admin)):
        messages.error(request, "Permission denied.")
        return redirect('home')
        
    timesheet = get_object_or_404(Timesheet, id=timesheet_id)
    entries = TimesheetDailyEntry.objects.filter(timesheet=timesheet).order_by('date')
    
    # Calculate period hours
    total_period_hours = Decimal('0.00')
    for e in entries:
        total_period_hours += e.total_hours
        
    context = {
        'timesheet': timesheet,
        'entries': entries,
        'total_period_hours': total_period_hours,
        'is_admin_view': True # Flag to hide edit buttons in template
    }
    return render(request, 'hr/timesheet_view.html', context)

@login_required
def export_timesheet_excel(request, timesheet_id):
    """
    Export specific timesheet as Excel (.xlsx) using openpyxl
    """
    # Permission check
    if not (request.user.is_superuser or (hasattr(request.user, 'hr_settings') and request.user.hr_settings.is_hr_admin)):
        messages.error(request, "Permission denied.")
        return redirect('home')
        
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill
    from django.http import HttpResponse
    
    timesheet = get_object_or_404(Timesheet, id=timesheet_id)
    entries = TimesheetDailyEntry.objects.filter(timesheet=timesheet).order_by('date')
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Timesheet {timesheet.period_start.strftime('%b %Y')}"
    
    # Header Info
    ws['A1'] = "Employee:"
    ws['B1'] = f"{timesheet.employee.first_name} {timesheet.employee.last_name} ({timesheet.employee.username})"
    ws['A2'] = "Period:"
    ws['B2'] = timesheet.period_start.strftime('%F %Y')
    ws['A3'] = "Status:"
    ws['B3'] = timesheet.get_status_display()
    
    ws['A1'].font = Font(bold=True)
    ws['A2'].font = Font(bold=True)
    ws['A3'].font = Font(bold=True)
    
    # Table Headers
    headers = ['Date', 'Day', 'Status', 'In Time', 'Out Time', 'Total Hours', 'Notes']
    row_num = 5
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=row_num, column=col_num)
        cell.value = header
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
        cell.alignment = Alignment(horizontal="center")
        
    # Data
    row_num = 6
    for entry in entries:
        ws.cell(row=row_num, column=1, value=entry.date.strftime('%Y-%m-%d'))
        ws.cell(row=row_num, column=2, value=entry.date.strftime('%A'))
        ws.cell(row=row_num, column=3, value=entry.get_status_display())
        
        in_time = entry.first_punch_in.strftime('%H:%M') if entry.first_punch_in else '--'
        out_time = entry.last_punch_out.strftime('%H:%M') if entry.last_punch_out else '--'
        
        ws.cell(row=row_num, column=4, value=in_time)
        ws.cell(row=row_num, column=5, value=out_time)
        ws.cell(row=row_num, column=6, value=entry.total_hours)
        ws.cell(row=row_num, column=7, value=entry.notes or '')
        
        # Highlight manual edits
        if entry.is_manual_adjustment:
             ws.cell(row=row_num, column=7).value = (entry.notes or '') + " [Manual Edit]"
        
        row_num += 1
        
    # Auto-adjust columns
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter # Get the column name
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"Timesheet_{timesheet.employee.username}_{timesheet.period_start.strftime('%Y_%m')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    wb.save(response)
    return response

@login_required
def hr_settings(request):
    return render(request, 'hr/settings.html')

@login_required
def admin_timesheet_list(request):
    return render(request, 'hr/admin_timesheet_list.html')

@login_required
def admin_timesheet_detail(request, id):
    return render(request, 'hr/admin_timesheet_detail.html')
