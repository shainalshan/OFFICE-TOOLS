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
import waffle
import json
import numpy as np
from django.views.decorators.http import require_POST
from .models import EmployeeSettings, PunchLog, Timesheet, TimesheetDailyEntry, EmployeeFaceData

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

    # Check Face Enrollment
    is_face_enrolled = False
    if hasattr(request.user, 'face_data'):
        is_face_enrolled = True

    context = {
        'is_punched_in': is_punched_in,
        'todays_punches': todays_punches,
        'settings': settings,
        'current_time': timezone.now(),
        'first_punch_in': first_punch_in,
        'is_face_enrolled': is_face_enrolled,
    }
    return render(request, 'hr/staff_portal.html', context)

@login_required
def attendance_report(request):
    """
    Advanced Attendance Reporting View.
    Guarded by 'hr_attendance_report' flag.
    """
    # Permission Check
    if not (request.user.is_superuser or (hasattr(request.user, 'hr_settings') and request.user.hr_settings.is_hr_admin)):
        messages.error(request, "Permission denied.")
        return redirect('home')
        
    # Feature Flag Check
    if not waffle.flag_is_active(request, 'hr_attendance_report'):
        messages.error(request, "Attendance Report feature is currently disabled.")
        return redirect('hr_admin_dashboard')
        
    # Defaults
    today = timezone.now().date()
    target_date_str = request.GET.get('date', str(today))
    
    try:
        target_date = datetime.datetime.strptime(target_date_str, '%Y-%m-%d').date()
    except ValueError:
        target_date = today
        
    # Thresholds (Hardcoded for now as per requirements)
    SHIFT_START = datetime.time(9, 30)
    SHIFT_END = datetime.time(18, 30)
    
    # 1. Ensure Data exists for target date (Trigger generation for all active users)
    # This might be slow if many users, but ensures report is accurate for 'Absent' people who haven't logged in.
    # Optimization: Only generate if not exists.
    active_users = User.objects.filter(is_active=True)
    # We won't call generate_timesheet_entries for everyone on every page load. 
    # Instead, we just query existing entries. 
    # Users who haven't logged in might not have 'Absent' entries explicitly created yet depending on system logic.
    # But let's assume the daily cron or user login creates them. 
    # For a robust report, we should really JOIN with Users.
    
    # Query Data
    # We fetch all users and their entry for this date (if any)
    
    report_data = []
    
    # Metrics
    metrics = {
        'total_employees': 0,
        'present': 0,
        'late': 0,
        'early_leaving': 0,
        'on_leave': 0,
        'week_off': 0,
        'absent': 0,
    }
    
    for user in active_users:
        # unexpected skip of superusers if they are not real employees? 
        # let's include everyone who has an EmployeeSettings
        if not hasattr(user, 'hr_settings'):
            continue
            
        metrics['total_employees'] += 1
        
        # Find entry
        entry = TimesheetDailyEntry.objects.filter(timesheet__employee=user, date=target_date).first()
        
        user_data = {
            'user': user,
            'status': 'ABSENT', # Default if no entry found
            'in_time': None,
            'out_time': None,
            'is_late': False,
            'is_early_left': False,
            'total_hours': 0,
            'notes': ''
        }
        
        if entry:
            user_data['status'] = entry.status
            user_data['in_time'] = entry.first_punch_in
            user_data['out_time'] = entry.last_punch_out
            user_data['total_hours'] = entry.total_hours
            user_data['notes'] = entry.notes
            
            # Logic
            if entry.status == 'PRESENT':
                metrics['present'] += 1
                
                # Late Check
                if entry.first_punch_in and entry.first_punch_in > SHIFT_START:
                    user_data['is_late'] = True
                    metrics['late'] += 1
                    
                # Early Leaving Check
                # Only if they have punched out, OR if the day is over?
                # If they haven't punched out yet, we can't say they left early unless it's past shift end and no out punch?
                # Usually 'Early Leaving' applies if last_punch_out < SHIFT_END
                if entry.last_punch_out and entry.last_punch_out < SHIFT_END:
                    user_data['is_early_left'] = True
                    metrics['early_leaving'] += 1
            
            elif entry.status in ['SICK_LEAVE', 'ANNUAL_LEAVE', 'HOLIDAY']:
                metrics['on_leave'] += 1
            elif entry.status == 'WEEK_OFF':
                metrics['week_off'] += 1
            elif entry.status == 'ABSENT':
                metrics['absent'] += 1
        else:
            # No entry usually means Absent or Not Generated
            metrics['absent'] += 1
            
        report_data.append(user_data)
        
    # --- Filtering Logic ---
    status_filter = request.GET.get('filter')
    filtered_data = report_data # Default: Show all
    
    if status_filter:
        if status_filter == 'present':
            filtered_data = [d for d in report_data if d['status'] == 'PRESENT']
        elif status_filter == 'late':
            filtered_data = [d for d in report_data if d['is_late']]
        elif status_filter == 'early_left':
            filtered_data = [d for d in report_data if d['is_early_left']]
        elif status_filter == 'absent':
            # 'absent' filter usually implies strict Absent, or maybe any non-present?
            # Let's stick to status == ABSENT
            filtered_data = [d for d in report_data if d['status'] == 'ABSENT']
        elif status_filter == 'on_leave':
             filtered_data = [d for d in report_data if d['status'] in ['SICK_LEAVE', 'ANNUAL_LEAVE', 'HOLIDAY']]
        elif status_filter == 'week_off':
             filtered_data = [d for d in report_data if d['status'] == 'WEEK_OFF']
             
    # Export Handling (Use FILTERED data)
    if request.GET.get('export') == 'excel':
        return export_attendance_report(target_date, filtered_data, metrics)
        
    context = {
        'target_date': target_date,
        'metrics': metrics,
        'report_data': filtered_data, # Show filtered list
        'current_filter': status_filter,
        'shift_start': SHIFT_START,
        'shift_end': SHIFT_END
    }
    return render(request, 'hr/attendance_report.html', context)

def export_attendance_report(date, data, metrics):
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from django.http import HttpResponse
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Attendance {date}"
    
    # Title
    ws.merge_cells('A1:H1')
    ws['A1'] = f"Attendance Report - {date.strftime('%A, %d %B %Y')}"
    ws['A1'].font = Font(size=14, bold=True)
    ws['A1'].alignment = Alignment(horizontal='center')
    
    # Metrics Row
    ws['A3'] = f"Total: {metrics['total_employees']}"
    ws['C3'] = f"Present: {metrics['present']}"
    ws['E3'] = f"Late: {metrics['late']}"
    ws['G3'] = f"Early Left: {metrics['early_leaving']}"
    
    ws['A4'] = f"Absent: {metrics['absent']}"
    ws['C4'] = f"On Leave: {metrics['on_leave']}"
    ws['E4'] = f"Week Off: {metrics['week_off']}"
    
    for row in ws['A3:H4']:
        for cell in row:
            cell.font = Font(bold=True)

    # Headers
    headers = ['Employee', 'Status', 'In Time', 'Out Time', 'Hours', 'Late?', 'Left Early?', 'Notes']
    header_row = 6
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=header_row, column=col_num)
        cell.value = header
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="3B82F6", fill_type="solid")
        cell.alignment = Alignment(horizontal="center")
        
    # Data
    row_num = 7
    for item in data:
        u = item['user']
        ws.cell(row=row_num, column=1, value=f"{u.first_name} {u.last_name}")
        ws.cell(row=row_num, column=2, value=item['status'])
        
        in_t = item['in_time'].strftime('%H:%M') if item['in_time'] else '--'
        # Highlight Late
        c_in = ws.cell(row=row_num, column=3, value=in_t)
        if item['is_late']:
            c_in.font = Font(color="DC2626", bold=True)
            
        out_t = item['out_time'].strftime('%H:%M') if item['out_time'] else '--'
        c_out = ws.cell(row=row_num, column=4, value=out_t)
        if item['is_early_left']:
            c_out.font = Font(color="DC2626", bold=True)
            
        ws.cell(row=row_num, column=5, value=item['total_hours'])
        ws.cell(row=row_num, column=6, value="YES" if item['is_late'] else "")
        ws.cell(row=row_num, column=7, value="YES" if item['is_early_left'] else "")
        ws.cell(row=row_num, column=8, value=item['notes'])
        
        row_num += 1
        
    # Auto-width
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try: 
                if len(str(cell.value)) > max_length: max_length = len(str(cell.value))
            except: pass
        ws.column_dimensions[column].width = max_length + 2

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Attendance_Report_{date}.xlsx"'
    wb.save(response)
    return response

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

    if waffle.flag_is_active(request, 'timesheet_strict_mode'):
        if not settings.allow_punch:
            return JsonResponse({'status': 'error', 'message': 'Punch access is strictly disabled for your account.'}, status=403)

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
    
    # Get User Settings for permissions
    settings_obj, _ = EmployeeSettings.objects.get_or_create(user=request.user)
    
    context = {
        'timesheet': timesheet,
        'entries': entries,
        'total_period_hours': total_period_hours,
        'today': timezone.now().date(),
        'settings': settings_obj
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

    # Master Edit Flag Check
    if not waffle.flag_is_active(request, 'enable_timesheet_editing'):
         return JsonResponse({'status': 'error', 'message': 'Timesheet editing is globally disabled.'}, status=403)

    # Strict Safety Mode Check
    if waffle.flag_is_active(request, 'timesheet_strict_mode'):
        settings, _ = EmployeeSettings.objects.get_or_create(user=request.user)
        if not settings.allow_edit:
            return JsonResponse({'status': 'error', 'message': 'Edit access is strictly disabled for your account.'}, status=403)
        
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

@login_required
def pull_timesheet(request):
    """
    Allow HR to 'Pull' (force submit) a user's timesheet.
    """
    if not (request.user.is_superuser or (hasattr(request.user, 'hr_settings') and request.user.hr_settings.is_hr_admin)):
        messages.error(request, "Permission denied.")
        return redirect('home')

    if not waffle.flag_is_active(request, 'hr_pull_attendance'):
         messages.error(request, "Feature disabled.")
         return redirect('hr_admin_dashboard')

    if request.method == 'POST':
        timesheet_id = request.POST.get('timesheet_id')
        timesheet = get_object_or_404(Timesheet, id=timesheet_id)
        
        if timesheet.status == 'PENDING':
            timesheet.status = 'SUBMITTED'
            timesheet.submitted_at = timezone.now()
            # Optional: Mark that it was forced by Admin? 
            # For now, just submitting it is enough to get it into the pipeline.
            timesheet.save()
            
            # Notify Employee
            try:
                SystemNotification.objects.create(
                    recipient=timesheet.employee,
                    title='Timesheet Pulled by HR',
                    message=f"Your timesheet for {timesheet.period_start.strftime('%B %Y')} was pulled for review by {request.user.first_name}.",
                    link=f"/hr/timesheet/view/{timesheet.id}/"
                )
            except Exception as e:
                print(f"Notification Error: {e}")
                
            messages.success(request, f"Successfully pulled timesheet for {timesheet.employee.username}.")
        else:
            messages.warning(request, "Timesheet is not in Pending state.")
            
    return redirect('hr_admin_dashboard')
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
            elif action == 'toggle_punch':
                settings.allow_punch = not settings.allow_punch
                settings.save()
                messages.success(request, f"Punch access for {target_user.username} is now {'ENABLED' if settings.allow_punch else 'DISABLED'}.")
            elif action == 'toggle_edit':
                settings.allow_edit = not settings.allow_edit
                settings.save()
                messages.success(request, f"Edit access for {target_user.username} is now {'ENABLED' if settings.allow_edit else 'DISABLED'}.")
                
        return redirect('hr_admin_dashboard')

    # Ensure all users have settings created so the template doesn't crash
    # ONLY fetch users for Superusers (Employee Access Management)
    # --- Mode handling ---
    mode = request.GET.get('mode', 'pending') # Options: 'pending', 'approvals', 'drafts', 'history', 'access'
    
    # Initialize variables to empty
    user_list = []
    submitted_timesheets = []
    approved_timesheets = []
    unsubmitted_timesheets = []
    
    # Search Params
    query = request.GET.get('q')
    search_pending = request.GET.get('search_pending')
    search_approved = request.GET.get('search_approved')
    date_approved = request.GET.get('date_approved')
    search_unsubmitted = request.GET.get('search_unsubmitted')

    # --- Mode: APPROVALS ---
    if mode == 'approvals':
        submitted_timesheets = Timesheet.objects.filter(status='SUBMITTED')
        if search_pending:
            submitted_timesheets = submitted_timesheets.filter(
                Q(employee__username__icontains=search_pending) |
                Q(employee__first_name__icontains=search_pending) |
                Q(employee__last_name__icontains=search_pending)
            )
        submitted_timesheets = submitted_timesheets.order_by('submitted_at')
        
    # --- Mode: DRAFTS ---
    elif mode == 'drafts':
        if waffle.flag_is_active(request, 'hr_pull_attendance'):
            unsubmitted_timesheets = Timesheet.objects.filter(status='PENDING')
            if search_unsubmitted:
                unsubmitted_timesheets = unsubmitted_timesheets.filter(
                    Q(employee__username__icontains=search_unsubmitted) |
                    Q(employee__first_name__icontains=search_unsubmitted) |
                    Q(employee__last_name__icontains=search_unsubmitted)
                )
            unsubmitted_timesheets = unsubmitted_timesheets.order_by('period_start')

    # --- Mode: HISTORY ---
    elif mode == 'history':
        approved_timesheets = Timesheet.objects.filter(status__in=['APPROVED', 'REJECTED']) # Maybe show rejected too in history? Original was just APPROVED filter but view name implies all finalized.
        # Original code was: approved_timesheets = Timesheet.objects.filter(status='APPROVED')
        # Let's stick to original behavior but maybe expand later.
        approved_timesheets = Timesheet.objects.filter(status='APPROVED')
        
        if search_approved:
            approved_timesheets = approved_timesheets.filter(
                Q(employee__username__icontains=search_approved) |
                Q(employee__first_name__icontains=search_approved) |
                Q(employee__last_name__icontains=search_approved)
            )
            
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

    # --- Mode: ACCESS (Settings) ---
    elif mode == 'access':
        if request.user.is_superuser:
            all_known_users = User.objects.filter(is_active=True).order_by('username') # Optimization: Only active?
            # Original: all()
            all_known_users = User.objects.all().order_by('username')
            
            if query:
                all_known_users = all_known_users.filter(
                    Q(username__icontains=query) | 
                    Q(first_name__icontains=query) | 
                    Q(last_name__icontains=query)
                )
            
            for u in all_known_users:
                s, _ = EmployeeSettings.objects.get_or_create(user=u)
                u.cached_settings = s 
                user_list.append(u)

    context = {
        'mode': mode,
        'users': user_list, 
        'search_query': query,
        'search_pending': search_pending,
        'search_approved': search_approved,
        'date_approved': date_approved,
        'submitted_timesheets': submitted_timesheets,
        'approved_timesheets': approved_timesheets,
        'unsubmitted_timesheets': unsubmitted_timesheets,
        'search_unsubmitted': search_unsubmitted,
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
 
@login_required
@require_POST
def enroll_face(request):
    """
    Saves the user's face descriptor (enrollment).
    """
    try:
        data = json.loads(request.body)
        descriptor = data.get('descriptor') # List of floats
        
        if not descriptor or len(descriptor) != 128:
             return JsonResponse({'status': 'error', 'message': 'Invalid face descriptor data.'}, status=400)
             
        # Save to DB
        face_data, created = EmployeeFaceData.objects.update_or_create(
            user=request.user,
            defaults={'face_descriptor': descriptor}
        )
        
        return JsonResponse({'status': 'success', 'message': 'Face enrolled successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def face_punch(request):
    """
    Verifies face and performs punch in/out.
    """
    if not waffle.flag_is_active(request, 'face_biometric_punch'):
         return JsonResponse({'status': 'error', 'message': 'Feature disabled.'}, status=403)
         
    try:
        data = json.loads(request.body)
        descriptor = data.get('descriptor')
        
        if not descriptor:
             return JsonResponse({'status': 'error', 'message': 'No face data provided.'}, status=400)
             
        # 1. Fetch Stored Data
        try:
            stored_data = request.user.face_data
            stored_descriptor = np.array(stored_data.face_descriptor)
        except EmployeeFaceData.DoesNotExist:
             return JsonResponse({'status': 'error', 'message': 'User not enrolled. Please enroll face first.'}, status=400)
             
        # 2. Verify (Euclidean Distance)
        received_descriptor = np.array(descriptor)
        distance = np.linalg.norm(stored_descriptor - received_descriptor)
        
        # Threshold: Adjusted to 0.55 based on user feedback (0.45 was too strict)
        if distance > 0.55:
             return JsonResponse({'status': 'error', 'message': f'Face mismatch. Match Score: {distance:.2f}'}, status=401)
             
        # 3. Perform Punch (Re-use existing logic logic is tricky because punch_in_out is a VIEW that expects request)
        # We can simulate the punch logic here or call a service. 
        # Since logic is small, I will duplicate/refactor the localized logic here to be safe and fast.
        
        # --- Copied/Adapted from punch_in_out ---
        settings_obj, _ = EmployeeSettings.objects.get_or_create(user=request.user)
        if not settings_obj.timesheet_enabled:
             return JsonResponse({'status': 'error', 'message': 'Timesheet access disabled.'}, status=403)
             
        # Strict Mode Check (Since we are seemingly bypassing the view)
        if waffle.flag_is_active(request, 'timesheet_strict_mode') and not settings_obj.allow_punch:
             return JsonResponse({'status': 'error', 'message': 'Punching permission revoked.'}, status=403)

        now = timezone.now()
        today = now.date()
        
        # Get/Create Timesheet
        ts = get_or_create_timesheet(request.user, today)
        daily_entry = TimesheetDailyEntry.objects.filter(timesheet=ts, date=today).first()
        
        # Determine strict punch type based on last state
        # Logic: If last was IN, next is OUT.
        last_log = PunchLog.objects.filter(user=request.user).order_by('-timestamp').first()
        
        punch_type = 'IN'
        if last_log and last_log.type == 'IN':
            punch_type = 'OUT'
            
        # Create Log
        PunchLog.objects.create(user=request.user, type=punch_type, timestamp=now, note="Face Biometric Punch")
        
        # Update Daily Entry
        if not daily_entry:
            # Should exist from get_or_create_timesheet but just in case
            pass 
        else:
            if punch_type == 'IN':
                if not daily_entry.first_punch_in:
                    daily_entry.first_punch_in = now.time()
                daily_entry.status = 'PRESENT'
            else:
                 daily_entry.last_punch_out = now.time()
                 
            daily_entry.save()
            
            # Recalc hours
            if daily_entry.first_punch_in and daily_entry.last_punch_out:
                # Simple recalc
                dummy = datetime.date(2000,1,1)
                t1 = datetime.datetime.combine(dummy, daily_entry.first_punch_in)
                t2 = datetime.datetime.combine(dummy, daily_entry.last_punch_out)
                diff = t2 - t1
                daily_entry.total_hours = Decimal(diff.total_seconds() / 3600)
                daily_entry.save()
        
        return JsonResponse({'status': 'success', 'punch_type': punch_type, 'distance': float(distance)})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def reset_face(request):
    """
    Deletes the enrolled face data.
    """
    if not waffle.flag_is_active(request, 'face_biometric_punch'):
         return JsonResponse({'status': 'error', 'message': 'Feature disabled.'}, status=403)
         
    try:
        if hasattr(request.user, 'face_data'):
            request.user.face_data.delete()
        return JsonResponse({'status': 'success', 'message': 'Face ID reset successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
