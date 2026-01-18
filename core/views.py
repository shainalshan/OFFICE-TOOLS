from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from .models import Tool, UserToolAccess, User, UserProfile, NotificationEventSetting, AuditLog
from contacts.models import Contact
from assets.models import Asset
from .forms import RegistrationForm
from .decorators import check_tool_access
import waffle
from waffle.models import Flag
from .email_utils import send_dynamic_email
from .notifications import send_event_notification
from .models import Tool, UserToolAccess, User, UserProfile, NotificationEventSetting, AuditLog, EmailConfiguration, ThemeConfiguration

@login_required
def test_error(request):
    """
    Intentionally raises an error to test GlobalExceptionMiddleware.
    """
    if request.user.is_superuser:
        # Raise a random exception
        raise Exception("This is a test exception to verify the 500 error page.")
    return redirect('home')


def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get available tools for user
    if request.user.is_superuser:
        tools = Tool.objects.filter(is_active=True)
    else:
        try:
            tools = request.user.tool_access.tools.filter(is_active=True)
        except UserToolAccess.DoesNotExist:
            tools = []

    return render(request, 'core/home.html', {'tools': tools})

@login_required
def set_user_tools(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            tool_slugs = data.get('tool_slugs', [])
            
            user = get_object_or_404(User, id=user_id)
            access, _ = UserToolAccess.objects.get_or_create(user=user)
            
            # Filter valid tools
            tools_to_set = Tool.objects.filter(slug__in=tool_slugs)
            access.tools.set(tools_to_set)
                
            return JsonResponse({'status': 'success', 'message': f'Permissions updated for {user.username}.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
        
    show_forgot_password = waffle.flag_is_active(request, 'profile')
    return render(request, 'core/login.html', {
        'form': form,
        'show_forgot_password': show_forgot_password
    })

def user_logout(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created! Please wait for admin approval.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'core/register.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def check_pending_users(request):
    """API for polling pending users"""
    pending_users = User.objects.filter(is_active=False)
    return render(request, 'core/partials/pending_users_table.html', {'pending_users': pending_users})

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    pending_users = User.objects.filter(is_active=False)
    pending_users = User.objects.filter(is_active=False)
    managed_users = User.objects.filter(is_superuser=False).order_by('-date_joined')
    all_tools = Tool.objects.all()
    all_contacts = Contact.objects.all().order_by('name')
    audit_logs = AuditLog.objects.all()[:50] # Last 50 actions

    if request.method == 'POST':
        action = request.POST.get('action')

        # --- DYNAMIC EMAIL CONFIG (SAFETY MODE) ---
        if waffle.flag_is_active(request, 'dynamic_email_config'):
            if action == 'update_email_config':
                email_user = request.POST.get('email_user')
                app_password = request.POST.get('app_password')
                
                config, _ = EmailConfiguration.objects.get_or_create(id=1) # Singleton-ish
                config.email_host_user = email_user
                config.email_host_password = app_password
                config.save()
                messages.success(request, 'Email Configuration Updated.')
                return redirect('admin_dashboard')

                messages.success(request, 'Email Configuration Updated.')
                return redirect('admin_dashboard')

            elif action == 'test_email_config':
                try:
                    send_dynamic_email(
                        'Test Email - Office Portal',
                        f'This is a test email from {request.user.username}.',
                        [request.user.email]
                    )
                    messages.success(request, f'Test email sent to {request.user.email}.')
                except Exception as e:
                    messages.error(request, f'Test Failed: {str(e)}')
                return redirect('admin_dashboard')

        if action == 'create_flag':
            flag_name = request.POST.get('flag_name')
            if flag_name:
                Flag.objects.get_or_create(name=flag_name)
                messages.success(request, f'Flag "{flag_name}" created.')
            return redirect('admin_dashboard')

        elif action == 'delete_flag':
            flag_id = request.POST.get('flag_id')
            Flag.objects.filter(id=flag_id).delete()
            messages.warning(request, 'Flag deleted.')
            return redirect('admin_dashboard')

        elif action == 'update_flag_rule':
            flag_id = request.POST.get('flag_id')
            
            # Checkbox values
            is_global = request.POST.get('is_global') == 'on'
            is_admin = request.POST.get('is_admin') == 'on'
            is_specific = request.POST.get('is_specific') == 'on'
            user_ids = request.POST.getlist('user_ids') # For specific
            
            flag = get_object_or_404(Flag, id=flag_id)
            
            # Logic:
            # 1. If Global is ON -> everyone=True. (Superusers/Users irrelevant for logic, but we can keep/clear them)
            # 2. If Global OFF -> everyone=None. Then Superusers/Users apply.
            
            if is_global:
                flag.everyone = True
                flag.superusers = True # Optional, but keeps it clean
                flag.users.clear() # Clear specific to avoid confusion? Or keep them? Let's clear to match "Global" concept.
            else:
                flag.everyone = None # This enables "Fallthrough" logic
                flag.superusers = is_admin
                
                if is_specific:
                    users_to_add = User.objects.filter(id__in=user_ids)
                    flag.users.set(users_to_add)
                else:
                    flag.users.clear()
            
            flag.save()
            messages.success(request, f'Updated rules for flag "{flag.name}".')
            return redirect('admin_dashboard')

        elif action == 'create_user':
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password')
            
            if User.objects.filter(username__iexact=username).exists():
                messages.error(request, 'Username already exists.')
            else:
                from django.db import IntegrityError
                try:
                    user = User.objects.create_user(username=username, email=email, password=password)
                    
                    # Handle Name and Numbers
                    full_name = request.POST.get('full_name', '')
                    mobile_number = request.POST.get('mobile_number', '')
                    whatsapp_number = request.POST.get('whatsapp_number', '')
                    
                    user.first_name = full_name # Using first_name to store full name for simplicity
                    user.is_active = True 
                    user.save()
                    
                    # Create Profile
                    UserProfile.objects.create(
                        user=user,
                        mobile_number=mobile_number,
                        whatsapp_number=whatsapp_number
                    )
                    
                    # Auto-assign ticketing logic
                    access, _ = UserToolAccess.objects.get_or_create(user=user)
                    ticketing = Tool.objects.filter(slug='ticketing').first()
                    if ticketing:
                        access.tools.add(ticketing)
                    
                    messages.success(request, f'User {username} created successfully.')
                except IntegrityError:
                    messages.error(request, f'Error: Username "{username}" is already taken.')
            return redirect('admin_dashboard')

        elif action == 'update_user':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            
            full_name = request.POST.get('full_name', '')
            mobile_number = request.POST.get('mobile_number', '')
            whatsapp_number = request.POST.get('whatsapp_number', '')
            
            user.first_name = full_name
            user.save()
            
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.mobile_number = mobile_number
            profile.whatsapp_number = whatsapp_number
            profile.save()
            
            messages.success(request, f"User {user.username} updated.")
            return redirect('admin_dashboard')

        elif action == 'create_contact':
            name = request.POST.get('name')
            phone_number = request.POST.get('phone_number')
            email = request.POST.get('email')
            designation = request.POST.get('designation')
            
            Contact.objects.create(
                name=name,
                phone_number=phone_number,
                email=email,
                designation=designation
            )
            messages.success(request, f'Contact {name} added.')
            return redirect('/dashboard/?section=manage-contacts-section')

        elif action == 'update_contact':
            contact_id = request.POST.get('contact_id')
            contact = get_object_or_404(Contact, id=contact_id)
            
            contact.name = request.POST.get('name')
            contact.phone_number = request.POST.get('phone_number')
            contact.email = request.POST.get('email')
            contact.designation = request.POST.get('designation')
            contact.save()
            
            messages.success(request, f'Contact {contact.name} updated.')
            return redirect('/dashboard/?section=manage-contacts-section')

        elif action == 'delete_contact':
            contact_id = request.POST.get('contact_id')
            contact = get_object_or_404(Contact, id=contact_id)
            name = contact.name
            contact.delete()
            messages.warning(request, f'Contact {name} deleted.')
            return redirect('/dashboard/?section=manage-contacts-section') 

        # --- NOTIFICATION SETTINGS ACTIONS ---
        elif action == 'add_subscriber':
            event_type = request.POST.get('event_type')
            sub_user_id = request.POST.get('sub_user_id')
            is_ajax = request.POST.get('is_ajax') == 'true'
            
            setting, _ = NotificationEventSetting.objects.get_or_create(event_type=event_type)
            
            if not sub_user_id:
                if is_ajax: return JsonResponse({'status': 'error', 'message': 'Please select a user.'})
                messages.error(request, 'Please select a user to add.')
            else:
                user_to_add = User.objects.filter(id=sub_user_id).first()
                if user_to_add:
                    setting.subscribers.add(user_to_add)
                    msg = f'Added {user_to_add.username} to {setting.get_event_type_display()}.'
                    if is_ajax: 
                        return JsonResponse({
                            'status': 'success', 
                            'message': msg,
                            'user': {'id': user_to_add.id, 'username': user_to_add.username}
                        })
                    messages.success(request, msg)
                else:
                    if is_ajax: return JsonResponse({'status': 'error', 'message': 'User not found.'})
                    messages.error(request, 'User not found.')
            return redirect('admin_dashboard')

        elif action == 'remove_subscriber':
            event_type = request.POST.get('event_type')
            sub_user_id = request.POST.get('sub_user_id')
            is_ajax = request.POST.get('is_ajax') == 'true'
            
            setting = get_object_or_404(NotificationEventSetting, event_type=event_type)
            user_to_remove = User.objects.filter(id=sub_user_id).first()
            
            if user_to_remove:
                setting.subscribers.remove(user_to_remove)
                msg = f'Removed {user_to_remove.username} from {setting.get_event_type_display()}.'
                if is_ajax: return JsonResponse({'status': 'success', 'message': msg})
                messages.warning(request, msg)
            else:
                if is_ajax: return JsonResponse({'status': 'error', 'message': 'User not found.'})
                messages.error(request, 'User to remove not found.')
            return redirect('admin_dashboard')

        user_id = request.POST.get('user_id')
        if not user_id:
             # Fallback or pass (if action is not user-related but not caught above)
             pass
        else:
            user = get_object_or_404(User, id=user_id)
            
            if action == 'approve':
                user.is_active = True
                user.save()
                access, _ = UserToolAccess.objects.get_or_create(user=user)
                
                # Notification
                send_event_notification('USER_APPROVED', {'user': user}, functional_recipients=[user])
                
                messages.success(request, f'User {user.username} has been approved and activated.')

            elif action == 'reject':
                username = user.username
                email = user.email
                
                # Send Rejection Notification (Optional, keeping silent for now or system log)
                send_event_notification('USER_REJECTED', {'user': user, 'username': username, 'email': email})
                
                user.delete()
                messages.warning(request, f'User request for {username} rejected and deleted.')

            elif action == 'delete_user':
                username = user.username
                user.delete()
                messages.success(request, f'User {username} has been permanently deleted.')

            elif action == 'reset_password':
                new_password = request.POST.get('custom_password', 'temp1234')
                user.set_password(new_password)
                user.save()
                messages.success(request, f"Password for {user.username} reset successfully.")

            elif action == 'assign_tool':
                tool_slug = request.POST.get('tool_slug')
                tool = get_object_or_404(Tool, slug=tool_slug)
                
                access, _ = UserToolAccess.objects.get_or_create(user=user)
                if tool in access.tools.all():
                    access.tools.remove(tool)
                    messages.info(request, f'Removed {tool.name} from {user.username}.')
                else:
                    access.tools.add(tool)
                    messages.success(request, f'Assigned {tool.name} to {user.username}.')

        # --- WAFFLE FLAG MANAGEMENT ---


        return redirect('admin_dashboard')

    # Prepare Notification Settings for Template

    # Prepare Notification Settings for Template
    # Ensure all types exist
    for type_code, type_label in NotificationEventSetting.EVENT_TYPES:
        NotificationEventSetting.objects.get_or_create(event_type=type_code)
    
    all_settings = NotificationEventSetting.objects.all()
    
    # Split into two groups
    # Categorize Settings
    ticket_types = [
        'TICKET_CREATED', 'TICKET_ASSIGNED', 'TICKET_STATUS_CHANGED', 'TICKET_COMMENTED', 
        'TICKET_BREACHED', 'TICKET_BREACH_WARNING'
    ]
    hr_types = ['TIMESHEET_SUBMITTED', 'TIMESHEET_REJECTED', 'TIMESHEET_APPROVED']
    user_types = ['USER_ADDED', 'USER_APPROVED', 'USER_REJECTED', 'USER_TOOL_ACCESS']
    system_types = ['SYSTEM_HIGH_LOAD', 'SYSTEM_ERROR_SPIKE', 'SYSTEM_DOWNTIME', 'ASSET_UPDATE', 'SIG_CREATED']

    ticket_settings = all_settings.filter(event_type__in=ticket_types)
    hr_settings = all_settings.filter(event_type__in=hr_types)
    user_settings = all_settings.filter(event_type__in=user_types)
    system_settings = all_settings.filter(event_type__in=system_types)
    
    # Catch-all for anything else not categorized
    # categorized_types = ticket_types + hr_types + user_types + system_types
    # other_settings = all_settings.exclude(event_type__in=categorized_types)

    # Waffle Flags Access Logic
    # Superusers ALWAYS have access (Safety Net), or if the flag is enabled
    can_manage_flags = request.user.is_superuser or waffle.flag_is_active(request, 'admin_waffle_manager')
    
    waffle_flags = []
    if can_manage_flags:
        waffle_flags = Flag.objects.all().order_by('name')

    # Optimization: Get user's tool slugs for template checks
    user_tool_slugs = []
    if request.user.is_authenticated:
        try:
             user_tool_slugs = list(request.user.tool_access.tools.values_list('slug', flat=True))
        except UserToolAccess.DoesNotExist:
             pass

    email_config = None
    if waffle.flag_is_active(request, 'dynamic_email_config'):
        email_config = EmailConfiguration.objects.first()

    return render(request, 'core/admin_dashboard.html', {
        'pending_users': pending_users,
        'managed_users': managed_users,
        'all_tools': all_tools,
        'all_contacts': all_contacts,
        'ticket_settings': ticket_settings,
        'hr_settings': hr_settings,
        'user_settings': user_settings,
        'system_settings': system_settings,
        'audit_logs': audit_logs,
        'waffle_flags': waffle_flags,
        'email_config': email_config,
        'can_manage_flags': can_manage_flags,
        'system_notification_settings': all_settings,
        'user_tool_slugs': user_tool_slugs,
        'user_tool_slugs': user_tool_slugs,
    })

@login_required
def restore_item(request, log_id):
    if not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect('admin_dashboard')
        
    log = get_object_or_404(AuditLog, id=log_id)
    
    if log.action != 'DELETE':
        messages.warning(request, "Only deleted items can be restored currently.")
        return redirect('admin_dashboard')
        
    try:
        model_map = {
            'user': User,
            'contact': Contact,
            'asset': Asset
        }
        ModelClass = model_map.get(log.model_name)
        
        if not ModelClass:
            messages.error(request, f"Unknown model: {log.model_name}")
            return redirect('admin_dashboard')
            
        # Check if ID already exists (re-used)
        if ModelClass.objects.filter(id=log.object_id).exists():
            messages.error(request, f"Cannot restore: ID {log.object_id} is already taken by another item.")
            return redirect('admin_dashboard')
            
        # Re-create object
        data = log.data
        
        # Remove ID if present to let DB handle it? 
        # Actually user wants "restore", best to keep ID if possible to maintain relations
        # But SQLite might complain if auto-increment is messed up.
        # Let's try forcing the ID.
        
        if ModelClass == User:
            # User uses create_user to handle password hashing etc, but here we have raw data
            # The password in data is likely the hashed string, so we can just set it directly.
            obj = ModelClass()
            for key, value in data.items():
                if key != 'user_permissions' and key != 'groups': # M2M relations need separate handling
                    setattr(obj, key, value)
            obj.save()
            messages.success(request, f"Successfully restored User: {log.object_repr}")
            
        else:
            obj = ModelClass()
            for key, value in data.items():
                setattr(obj, key, value)
            obj.save()
            messages.success(request, f"Successfully restored {log.model_name}: {log.object_repr}")
            
    except Exception as e:
        messages.error(request, f"Restore failed: {str(e)}")
        
    return redirect('admin_dashboard')

@login_required
def search_users_notification(request):
    """API to search users for notification assignment"""
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(email__icontains=query)
        ).values('id', 'username', 'email')[:10]
        return JsonResponse({'users': list(users)})
    return JsonResponse({'users': []})

@login_required
def list_notifications(request):
    """API to list user notifications with pagination and cleanup"""
    from .models import SystemNotification
    from django.utils import timezone
    from datetime import timedelta
    
    # 5-Day Expiry logic for READ items (Filtering only, not deleting yet)
    five_days_ago = timezone.now() - timedelta(days=5)
    
    # Base Query: Belong to user AND (Unread OR Read within last 5 days)
    # This filters out "old read" notifications from the UI
    notifs_query = SystemNotification.objects.filter(
        recipient=request.user
    ).filter(
        Q(is_read=False) | Q(created_at__gte=five_days_ago) 
    ).order_by('-created_at')
    
    # Pagination
    page = int(request.GET.get('page', 1))
    limit = 5 # Small limit as requested to avoid "too big" dialog
    start = (page - 1) * limit
    end = start + limit
    
    total_count = notifs_query.count()
    notifs = notifs_query[start:end]
    
    data = []
    for n in notifs:
        data.append({
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'link': n.link,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%Y-%m-%d %H:%M')
        })
        
    return JsonResponse({
        'notifications': data,
        'has_next': end < total_count,
        'next_page': page + 1 if end < total_count else None
    })

@login_required
def mark_notification_read(request, notification_id):
    """API to mark a single notification as read"""
    from .models import SystemNotification
    try:
        notif = SystemNotification.objects.get(id=notification_id, recipient=request.user)
        notif.is_read = True
        notif.save()
        return JsonResponse({'status': 'success'})
    except SystemNotification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)

@login_required
def mark_notification_unread(request, notification_id):
    """API to mark a single notification as unread"""
    from .models import SystemNotification
    try:
        notif = SystemNotification.objects.get(id=notification_id, recipient=request.user)
        notif.is_read = False
        notif.save()
        return JsonResponse({'status': 'success'})
    except SystemNotification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)

@login_required
def mark_all_read(request):
    """API to mark all notifications as read"""
    from .models import SystemNotification
    SystemNotification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})

@login_required
def mark_all_unread(request):
    """API to mark all notifications as unread"""
    from .models import SystemNotification
    # Only mark those that are currently read as unread
    SystemNotification.objects.filter(recipient=request.user, is_read=True).update(is_read=False)
    return JsonResponse({'status': 'success'})

@login_required
def delete_notification(request, notification_id):
    """API to delete a single notification"""
    from .models import SystemNotification
    try:
        notif = SystemNotification.objects.get(id=notification_id, recipient=request.user)
        notif.delete()
        return JsonResponse({'status': 'success'})
    except SystemNotification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)

@login_required
def clear_all_notifications(request):
    """API to delete all notifications for the user"""
    from .models import SystemNotification
    SystemNotification.objects.filter(recipient=request.user).delete()
    return JsonResponse({'status': 'success'})

@login_required
def check_notifications(request):
    """API to check unread count"""
    from .models import SystemNotification
    count = SystemNotification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})

@login_required
@check_tool_access('news')
def office_news(request):
    return render(request, 'core/tool_placeholder.html', {'tool_name': 'Office News'})

@login_required
@check_tool_access('chat')
def group_chat(request):
    return render(request, 'core/tool_placeholder.html', {'tool_name': 'Group Chat'})

@login_required
@check_tool_access('pdf-to-word')
def pdf_to_word(request):
    return render(request, 'core/tool_placeholder.html', {'tool_name': 'PDF to Word Converter'})

@login_required
def profile_view(request):
    if not waffle.flag_is_active(request, 'profile'):
        messages.error(request, "Profile feature is currently disabled.")
        return redirect('home')

    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    # Check if EmployeeFaceData exists (soft dependency on HR app)
    is_face_enrolled = False
    try:
        from hr.models import EmployeeFaceData
        if EmployeeFaceData.objects.filter(user=user).exists():
            is_face_enrolled = True
    except ImportError:
        pass

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_personal':
            first_name = request.POST.get('full_name')
            mobile = request.POST.get('mobile_number')
            whatsapp = request.POST.get('whatsapp_number')
            dob = request.POST.get('birth_date')
            
            user.first_name = first_name
            user.save()
            
            profile.mobile_number = mobile
            profile.whatsapp_number = whatsapp
            if dob:
                profile.birth_date = dob
            profile.save()
            
            messages.success(request, "Personal details updated.")
            return redirect('/profile/#personal')
            
        elif action == 'reset_password_email':
            # Generate Temp Password
            import random
            import string
            temp_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
            user.set_password(temp_pass)
            user.save()
            
            # Keep user logged in
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            
            # Send Email
            try:
                send_dynamic_email(
                    subject="Password Reset - Office Portal",
                    message=f"Hello {user.username},\n\nYour temporary password is: {temp_pass}\n\nPlease use this as your 'Current Password' to set a new one.",
                    recipient_list=[user.email]
                )
                messages.success(request, "Temporary password sent to your email.")
            except Exception as e:
                messages.error(request, f"Failed to send email: {e}")
            
            return redirect('/profile/#security')

        elif action == 'change_password':
            old_pass = request.POST.get('old_password')
            new_pass = request.POST.get('new_password')
            confirm_pass = request.POST.get('confirm_password')
            
            if not user.check_password(old_pass):
                messages.error(request, "Incorrect current password.")
                return redirect('/profile/#security')
                
            if new_pass != confirm_pass:
                messages.error(request, "New passwords do not match.")
                return redirect('/profile/#security')
                
            if len(new_pass) < 6:
                messages.error(request, "Password must be at least 6 characters.")
                return redirect('/profile/#security')
                
            user.set_password(new_pass)
            user.save()
            
            # Keep user logged in
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            
            messages.success(request, "Password changed successfully.")
            return redirect('/profile/#security')

        elif action == 'update_face':
            if 'face_image' not in request.FILES:
                messages.error(request, "No image uploaded.")
                return redirect('/profile/#face-bio')
                
            image_file = request.FILES['face_image']
            
            try:
                import face_recognition
                
                # Load image
                image = face_recognition.load_image_file(image_file)
                encodings = face_recognition.face_encodings(image)
                
                if len(encodings) == 0:
                    messages.error(request, "No face detected in the photo. Please try again.")
                    return redirect('/profile/#face-bio')
                    
                if len(encodings) > 1:
                    messages.error(request, "Multiple faces detected. Please upload a photo with only you.")
                    return redirect('/profile/#face-bio')
                    
                # Store encoding
                descriptor = encodings[0].tolist() # Convert numpy array to list
                
                from hr.models import EmployeeFaceData
                face_data, _ = EmployeeFaceData.objects.get_or_create(user=user)
                face_data.face_descriptor = descriptor
                face_data.save()
                
                messages.success(request, "Face data updated successfully.")
                
            except ImportError:
                messages.error(request, "Face recognition system is not installed on this server.")
            except Exception as e:
                messages.error(request, f"Error processing image: {str(e)}")
                
            return redirect('/profile/#face-bio')

    return render(request, 'core/profile.html', {
        'profile': profile,
        'is_face_enrolled': is_face_enrolled
    })

def forgot_password(request):
    if not waffle.flag_is_active(request, 'profile'):
        messages.error(request, "Feature disabled.")
        return redirect('login')
        
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        
        # Security: Always show the same success message to prevent user enumeration
        success_msg = "If an account exists with those details, a temporary password has been sent to the registered email."
        
        user = User.objects.filter(Q(username__iexact=identifier) | Q(email__iexact=identifier)).first()
        
        if user:
            # Generate Temp Password
            import random
            import string
            temp_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
            user.set_password(temp_pass)
            user.save()
            
            # Send Email
            try:
                send_dynamic_email(
                    subject="Password Reset - Office Portal",
                    message=f"Hello {user.username},\n\nYour temporary password is: {temp_pass}\n\nPlease login and change your password immediately in My Profile -> Security.",
                    recipient_list=[user.email]
                )
            except Exception as e:
                # Log error but don't show user? Or show error if email fails?
                # For this tool, better to show error if email fails so they know.
                print(f"Email failed: {e}")
                
        messages.success(request, success_msg)
        return redirect('login')
        
    return render(request, 'core/forgot_password.html')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def theme_changer_view(request):
    users = User.objects.all().order_by('username')
    config, _ = ThemeConfiguration.objects.get_or_create(id=1)
    
    return render(request, 'core/theme_changer.html', {
        'users': users,
        'global_theme': config.global_theme
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def apply_theme(request):
    if request.method == 'POST':
        theme_name = request.POST.get('theme_name')
        scope = request.POST.get('scope') # 'global', 'admin', 'specific'
        user_id = request.POST.get('user_id')
        
        if not theme_name:
            messages.error(request, "Please select a theme.")
            return redirect('theme_changer')

        if scope == 'global':
            config, _ = ThemeConfiguration.objects.get_or_create(id=1)
            config.global_theme = theme_name
            config.save()
            messages.success(request, f"Global theme updated to {theme_name}.")
            
        elif scope == 'admin':
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            profile.theme_preference = theme_name
            profile.save()
            messages.success(request, f"Theme applied to you ({request.user.username}).")
            
        elif scope == 'specific':
            if not user_id:
                messages.error(request, "Please select a user for specific application.")
                return redirect('theme_changer')
                
            target_user = get_object_or_404(User, id=user_id)
            profile, _ = UserProfile.objects.get_or_create(user=target_user)
            profile.theme_preference = theme_name
            profile.save()
            messages.success(request, f"Theme applied to {target_user.username}.")
            
    return redirect('theme_changer')
