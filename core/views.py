from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from .models import Tool, UserToolAccess, User
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
    active_users = User.objects.filter(is_active=True, is_superuser=False)
    all_tools = Tool.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create_user':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.is_active = True # Auto-activate since admin created it
                user.save()
                
                # Auto-assign ticketing logic
                access, _ = UserToolAccess.objects.get_or_create(user=user)
                ticketing = Tool.objects.filter(slug='ticketing').first()
                if ticketing:
                    access.tools.add(ticketing)
                
                messages.success(request, f'User {username} created successfully.')
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
            messages.warning(request, f'User {user.username} has been suspended.')

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

    return render(request, 'core/admin_dashboard.html', {
        'pending_users': pending_users,
        'active_users': active_users,
        'all_tools': all_tools
    })

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
