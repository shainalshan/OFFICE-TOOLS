from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Count, Q
from django.http import HttpResponse
from .models import Ticket, DeletedTicketLog
from .forms import TicketForm
from core.decorators import check_tool_access
import csv
import openpyxl
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

@login_required
@check_tool_access('ticketing') # Assuming 'ticketing' slug for tool
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, f'Ticket {ticket.ticket_id} created successfully.')
            return redirect('my_tickets')
    else:
        form = TicketForm(user=request.user)
    return render(request, 'tickets/create_ticket.html', {'form': form})

@login_required
@check_tool_access('ticketing')
def my_tickets(request):
    # Hide completed tickets older than 24 hours
    cutoff_time = timezone.now() - timedelta(hours=24)
    
    tickets = Ticket.objects.filter(user=request.user)
    
    # Exclude old completed tickets
    visible_tickets = []
    for ticket in tickets:
        if ticket.status == 'COMPLETED':
            if ticket.completed_at and ticket.completed_at > cutoff_time:
                visible_tickets.append(ticket)
        else:
            visible_tickets.append(ticket)
            
    # Sort by created desc
    visible_tickets.sort(key=lambda x: x.created_at, reverse=True)

    # Fetch Assigned Tickets
    assigned_tickets_qs = Ticket.objects.filter(assigned_to=request.user)
    assigned_tickets = []
    for ticket in assigned_tickets_qs:
        if ticket.status == 'COMPLETED':
            if ticket.completed_at and ticket.completed_at > cutoff_time:
                assigned_tickets.append(ticket)
        else:
            assigned_tickets.append(ticket)
            
    assigned_tickets.sort(key=lambda x: x.created_at, reverse=True)

    # Check admin access
    is_admin = is_ticket_admin(request.user)
            
    return render(request, 'tickets/my_tickets.html', {
        'tickets': visible_tickets, 
        'assigned_tickets': assigned_tickets,
        'is_admin': is_admin
    })

def is_ticket_admin(user):
    return user.is_superuser or user.groups.filter(name='Ticket Admin').exists()

@user_passes_test(is_ticket_admin)
def admin_ticket_panel(request):

    # Ensure Group Exists
    Group.objects.get_or_create(name='Ticket Admin')

    # Filter handling
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    
    tickets = Ticket.objects.all().order_by('-created_at')
    
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    else:
        # Default: Exclude COMPLETED tickets so "All" acts as "Active"
        tickets = tickets.exclude(status='COMPLETED')
    priority_filter = request.GET.get('priority')
    if priority_filter == 'DEADLINE':
        tickets = tickets.filter(deadline__isnull=False).order_by('deadline')
    elif priority_filter:
        tickets = tickets.filter(priority=priority_filter)
        
    search_query = request.GET.get('ticket_search')
    if search_query:
        tickets = tickets.filter(
            Q(ticket_id__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query)
        )

    # Assignee Filter
    assignee_filter = request.GET.get('assignee')
    if assignee_filter == 'none':
        tickets = tickets.filter(assigned_to__isnull=True)
    elif assignee_filter == 'me':
        tickets = tickets.filter(assigned_to=request.user)
    elif assignee_filter and assignee_filter.isdigit():
        tickets = tickets.filter(assigned_to_id=assignee_filter)
        
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        new_status = request.POST.get('new_status')
        
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        # Update Status
        if new_status:
            ticket.status = new_status
            
        # Update Resolution
        resolution = request.POST.get('resolution')
        if resolution is not None:
             ticket.resolution = resolution

        # Update Assigned User
        assigned_to_id = request.POST.get('assigned_to')
        if assigned_to_id:
            if assigned_to_id == 'none':
                ticket.assigned_to = None
            else:
                try:
                    ticket.assigned_to = User.objects.get(id=assigned_to_id)
                except User.DoesNotExist:
                    pass
             
        ticket.save()
        messages.success(request, f'Ticket {ticket.ticket_id} updated successfully.')
        return redirect('admin_ticket_panel')

    # Get all users and check if they are in the group
    # Only show Ticket Admins in the assignment dropdowns
    # Get all users for the assignment dropdown
    # User requested to allow choosing any assignee (similar to what they expect)
    all_users = User.objects.all().order_by('username')
    
    # For the access table, we technically need ALL users to grant access TO them.
    # So let's fetch all users separately for the access management list
    all_users_for_access = User.objects.all().order_by('username')
    
    ticket_admin_group = Group.objects.get(name='Ticket Admin')
    # Use get_or_create for Support group to be safe
    ticket_support_group, _ = Group.objects.get_or_create(name='Ticket Support')
    
    users_with_access = []
    users_with_assignee_role = []

    for user in all_users_for_access:
        has_access = ticket_admin_group in user.groups.all()
        users_with_access.append({
            'user': user,
            'has_access': has_access
        })
        
        is_assignee = ticket_support_group in user.groups.all()
        users_with_assignee_role.append({
            'user': user,
            'is_assignee': is_assignee
        })

    # Update dropdown to show Admins OR Support staff
    # Query: Users in 'Ticket Admin' OR 'Ticket Support'
    all_users = User.objects.filter(
        Q(groups__name='Ticket Admin') | Q(groups__name='Ticket Support')
    ).distinct().order_by('username')


    return render(request, 'tickets/admin_panel_v6.html', {
        'tickets': tickets,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        
        # Pre-calculated booleans for template safety
        'is_filter_pending': status_filter == 'PENDING',
        'is_filter_in_progress': status_filter == 'IN_PROGRESS',
        'is_filter_completed': status_filter == 'COMPLETED',
        'is_filter_cancelled': status_filter == 'CANCELLED',
        'is_filter_deadline': priority_filter == 'DEADLINE',
        'is_filter_cancelled': status_filter == 'CANCELLED',
        'is_filter_deadline': priority_filter == 'DEADLINE',
        'is_filter_unassigned': assignee_filter == 'none',
        'is_filter_me': assignee_filter == 'me',
        'is_filter_active': not status_filter and not priority_filter and not assignee_filter,
        'assignee_filter': assignee_filter,

        'users': all_users, # For assignment dropdown
        'users_with_access': users_with_access, # For access management
        'users_with_assignee_role': users_with_assignee_role, # For assignee management
        'now': timezone.now()
    })

@login_required
def delete_ticket(request, ticket_id):
    # Only superusers or Ticket Admins can delete
    if not request.user.is_superuser:
        if not request.user.groups.filter(name='Ticket Admin').exists():
            messages.error(request, "Permission denied. Only admins can delete tickets.")
            return redirect('admin_ticket_panel')

    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
        # Log for recycling
        DeletedTicketLog.objects.create(ticket_id=ticket.ticket_id)
        
        ticket_id_str = ticket.ticket_id
        ticket.delete()
        messages.success(request, f"Ticket {ticket_id_str} deleted. ID queued for recycling.")
    
    return redirect('admin_ticket_panel')

@login_required
@check_tool_access('ticketing')
def ticket_history(request):
    # Filter for Completed/Cancelled tickets related to the user
    # 1. Created by user
    # 2. Assigned to user
    tickets = Ticket.objects.filter(
        Q(status__in=['COMPLETED', 'CANCELLED']) &
        (Q(user=request.user) | Q(assigned_to=request.user))
    ).order_by('-updated_at')
    
    return render(request, 'tickets/ticket_history.html', {'tickets': tickets})

@user_passes_test(lambda u: u.is_superuser)
def manage_ticket_access(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action') # 'grant' or 'revoke'
        
        try:
            user = User.objects.get(id=user_id)
            group, created = Group.objects.get_or_create(name='Ticket Admin')
            
            if action == 'grant':
                user.groups.add(group)
                messages.success(request, f'Access granted to {user.username}')
            elif action == 'revoke':
                user.groups.remove(group)
                messages.success(request, f'Access revoked from {user.username}')
                
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            
    return redirect('admin_ticket_panel')

@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Ticket Admin').exists())
def manage_ticket_assignees(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action') # 'grant' or 'revoke'
        
        try:
            user = User.objects.get(id=user_id)
            group, created = Group.objects.get_or_create(name='Ticket Support')
            
            if action == 'grant':
                user.groups.add(group)
                messages.success(request, f'Assignee role granted to {user.username}')
            elif action == 'revoke':
                user.groups.remove(group)
                messages.success(request, f'Assignee role revoked from {user.username}')
                
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            
    return redirect('admin_ticket_panel')

@user_passes_test(is_ticket_admin)
def ticket_reports(request):
    # Date Filtering
    date_range = request.GET.get('date_range', 'all')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    tickets = Ticket.objects.all()
    
    if date_range == 'last_month':
        today = timezone.now().date()
        first = today.replace(day=1)
        last_month_end = first - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        tickets = tickets.filter(created_at__date__gte=last_month_start, created_at__date__lte=last_month_end)
    elif start_date and end_date:
        tickets = tickets.filter(created_at__date__range=[start_date, end_date])
        
    # Stats Calculation
    total_tickets = tickets.count()
    status_counts = tickets.values('status').annotate(count=Count('status'))
    priority_counts = tickets.values('priority').annotate(count=Count('priority'))

    # Helper to dict
    status_dict = {item['status']: item['count'] for item in status_counts}
    priority_dict = {item['priority']: item['count'] for item in priority_counts}
    
    # Export Logic
    export_type = request.GET.get('export')
    if export_type == 'excel':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=ticket_report_{timezone.now().date()}.xlsx'
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Tickets"
        
        # Headers
        headers = ['Ticket ID', 'User', 'Status', 'Priority', 'Created At', 'Issue', 'Resolution']
        ws.append(headers)
        
        for t in tickets:
            res = t.resolution if t.resolution else ""
            ws.append([t.ticket_id, t.user.username, t.status, t.priority, t.created_at.replace(tzinfo=None), t.issue, res])
            
        wb.save(response)
        return response
        
    elif export_type == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=ticket_report_{timezone.now().date()}.pdf'
        
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        elements.append(Paragraph("Ticket Analytic Report", styles['Title']))
        elements.append(Paragraph(f"Date: {timezone.now().date()}", styles['Normal']))
        elements.append(Paragraph(f"Total Tickets: {total_tickets}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Stats Table
        stat_data = [['Status', 'Count']]
        for s in status_dict:
            stat_data.append([s, status_dict[s]])
            
        t_stats = Table(stat_data, colWidths=[150, 50])
        t_stats.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(t_stats)
        elements.append(Spacer(1, 20))
        
        # Ticket List Table
        elements.append(Paragraph("Ticket Details:", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        # Columns: ID, User, Status, Resolution
        # We limit columns to fit on page
        ticket_data = [['ID', 'User', 'Status', 'Resolution']]
        for t in tickets:
            res = t.resolution if t.resolution else ""
            # Wrap text if needed? standard Table handles some, but long text might overflow.
            # Paragraphs inside cells handle wrapping.
            res_para = Paragraph(res, styles['BodyText'])
            ticket_data.append([t.ticket_id, t.user.username, t.status, res_para])
            
        # Table with auto-wrapping for resolution
        t_tickets = Table(ticket_data, colWidths=[80, 80, 80, 300])
        t_tickets.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'), # Align top for multi-line
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(t_tickets)
        
        doc.build(elements)
        return response


    
    context = {
        'total': total_tickets,
        'status_counts': status_dict,
        'priority_counts': priority_dict,
        'start_date': start_date,
        'end_date': end_date,
        'date_range': date_range
    }
    return render(request, 'tickets/reports.html', context)

@login_required
@check_tool_access('ticketing')
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    
    # Permission Check: Owner, Assignee, or Admin
    is_owner = ticket.user == request.user
    is_assignee = ticket.assigned_to == request.user
    is_admin = is_ticket_admin(request.user)
    
    if not (is_owner or is_assignee or is_admin):
        messages.error(request, "You do not have permission to view this ticket.")
        return redirect('my_tickets')
        
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Add Comment
        if action == 'comment':
            text = request.POST.get('text')
            if text:
                from .models import TicketComment
                TicketComment.objects.create(ticket=ticket, user=request.user, text=text)
                messages.success(request, "Comment added.")
        
        # Update Status (Assignee or Admin only)
        elif action == 'status':
            if is_assignee or is_admin:
                new_status = request.POST.get('new_status')
                if new_status in dict(Ticket.STATUS_CHOICES):
                    ticket.status = new_status
                    ticket.save()
                    messages.success(request, f"Status updated to {ticket.get_status_display()}.")
            else:
                 messages.error(request, "Permission denied to update status.")

        # Cancel Ticket (Owner, Assignee, or Admin)
        elif action == 'cancel':
            # Check if ticket is not already completed or cancelled
            if ticket.status not in ['COMPLETED', 'CANCELLED']:
                ticket.status = 'CANCELLED'
                ticket.save()
                messages.success(request, "Ticket cancelled.")
            else:
                 messages.warning(request, "Ticket is already closed.")
                 
        return redirect('ticket_detail', ticket_id=ticket.ticket_id)

    comments = ticket.comments.all().order_by('created_at')
    
    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'comments': comments,
        'is_owner': is_owner,
        'is_assignee': is_assignee, 
        'is_admin': is_admin
    })
