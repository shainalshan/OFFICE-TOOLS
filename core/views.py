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
    return render(request, 'core/login.html', {'form': form})

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

        if action == 'create_user':
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
            
            setting, _ = NotificationEventSetting.objects.get_or_create(event_type=event_type)
            
            if not sub_user_id:
                messages.error(request, 'Please select a user to add.')
            else:
                user_to_add = User.objects.filter(id=sub_user_id).first()
                if user_to_add:
                    setting.subscribers.add(user_to_add)
                    messages.success(request, f'Added {user_to_add.username} to {setting.get_event_type_display()}.')
                else:
                    messages.error(request, 'User not found.')
            return redirect('admin_dashboard')

        elif action == 'remove_subscriber':
            event_type = request.POST.get('event_type')
            sub_user_id = request.POST.get('sub_user_id')
            
            setting = get_object_or_404(NotificationEventSetting, event_type=event_type)
            user_to_remove = User.objects.filter(id=sub_user_id).first()
            
            if user_to_remove:
                setting.subscribers.remove(user_to_remove)
                messages.warning(request, f'Removed {user_to_remove.username} from {setting.get_event_type_display()}.')
            else:
                messages.error(request, 'User to remove not found.')
            return redirect('admin_dashboard')

        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        
        if action == 'approve':
            user.is_active = True
            user.save()
            access, _ = UserToolAccess.objects.get_or_create(user=user)
            
            # Auto-assign ticketing
            ticketing = Tool.objects.filter(slug='ticketing').first()
            if ticketing:
                access.tools.add(ticketing)
                
            messages.success(request, f'User {user.username} approved.')
            
            # Send Email Notification
            try:
                send_mail(
                    'Account Approved - Office Portal',
                    f'Hello {user.username},\n\nYour account has been approved by the administrator. You can now login using your credentials.\n\nBest regards,\nOffice Admin',
                    'admin@officeportal.local',
                    [user.email],
                    fail_silently=True,
                )
            except Exception:
                pass # Fail silently for local dev if config issues
        
        elif action == 'reject':
            username = user.username
            user.delete()
            messages.warning(request, f'User request for {username} was rejected and deleted.')

        elif action == 'suspend':
            user.is_active = False
            user.save()
            messages.warning(request, f'User {user.username} has been suspended (access disabled).')

        elif action == 'reactivate':
            user.is_active = True
            user.save()
            messages.success(request, f'User {user.username} has been reactivated.')

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

        return redirect('admin_dashboard')

    # Prepare Notification Settings for Template

    # Prepare Notification Settings for Template
    # Ensure all types exist
    for type_code, type_label in NotificationEventSetting.EVENT_TYPES:
        NotificationEventSetting.objects.get_or_create(event_type=type_code)
    
    notification_settings = NotificationEventSetting.objects.all()

    return render(request, 'core/admin_dashboard.html', {
        'pending_users': pending_users,
        'managed_users': managed_users,
        'all_tools': all_tools,
        'all_contacts': all_contacts,
        'notification_settings': notification_settings,
        'audit_logs': audit_logs
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
