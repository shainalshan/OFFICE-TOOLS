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
    today = timezone.now().date()
    timesheet = get_or_create_timesheet(request.user, today)
    
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

    # Apply changes
    entry.status = new_status
    entry.is_manual_adjustment = True
    
    # Logic for hours based on status
    # If Leave/Holiday/Sick -> 0 hours usually (unless paid leave counts as hours? For now 0 "worked" hours)
    if new_status in ['ABSENT', 'HOLIDAY', 'SICK_LEAVE', 'ANNUAL_LEAVE', 'WEEK_OFF']:
        entry.total_hours = Decimal('0.00')
    # If WFH -> We trust the punches or keep existing hours. 
    # Or maybe user wants to manually set hours? For now, let's leaving hours alone if WFH, assuming punches exist.
    
    entry.save()
    
    return JsonResponse({'status': 'success', 'message': 'Entry updated'})

@login_required
def submit_timesheet(request):
    return redirect('hr_staff_portal')

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
    all_known_users = User.objects.all().order_by('username')
    
    # Search implementation
    query = request.GET.get('q')
    if query:
        all_known_users = all_known_users.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        )
    
    user_list = []
    for u in all_known_users:
        # get_or_create forces creation if missing, preventing RelatedObjectDoesNotExist
        s, _ = EmployeeSettings.objects.get_or_create(user=u)
        # Attach strictly for template usage (though u.hr_settings works now)
        u.cached_settings = s 
        user_list.append(u)
    
    return render(request, 'hr/admin_dashboard.html', {'users': user_list, 'search_query': query})

@login_required
def hr_settings(request):
    return render(request, 'hr/settings.html')

@login_required
def admin_timesheet_list(request):
    return render(request, 'hr/admin_timesheet_list.html')

@login_required
def admin_timesheet_detail(request, id):
    return render(request, 'hr/admin_timesheet_detail.html')
