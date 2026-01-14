from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Count, Q
from django.db import connection
from django.http import HttpResponse
from .models import Ticket, DeletedTicketLog, TicketAttachment
from .forms import TicketForm
from core.decorators import check_tool_access
import waffle
import csv
import openpyxl
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from core.notifications import send_event_notification

def is_ticket_admin(user):
    return user.is_superuser or user.groups.filter(name='Ticket Admin').exists()

@login_required
@check_tool_access('ticketing')
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            
            # --- Safety Mode: Approval Workflow ---
            if waffle.flag_is_active(request, 'ticket_approval_workflow'):
                approver = form.cleaned_data.get('approver')
                if approver:
                    ticket.approver = approver
                    ticket.approval_status = 'PENDING'
                else:
                    ticket.approval_status = 'APPROVED'
            else:
                ticket.approval_status = 'APPROVED'
            # --------------------------------------

            ticket.save()

            # --- Safety Mode: Ticket Attachments ---
            if waffle.flag_is_active(request, 'ticket_attachments'):
                file = request.FILES.get('attachment')
                if file:
                    if file.size > 10 * 1024 * 1024:
                        messages.warning(request, f'File {file.name} is too large (Max 10MB). Ticket created without attachment.')
                    else:
                        TicketAttachment.objects.create(
                            ticket=ticket,
                            file=file,
                            uploaded_by=request.user
                        )
            # ---------------------------------------

            # Notification
            send_event_notification('TICKET_CREATED', {'ticket': ticket}, functional_recipients=[ticket.user])

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
    
    visible_tickets = []
    for ticket in tickets:
        if ticket.status == 'COMPLETED':
            if ticket.completed_at and ticket.completed_at > cutoff_time:
                visible_tickets.append(ticket)
        else:
            visible_tickets.append(ticket)
            
    visible_tickets.sort(key=lambda x: x.created_at, reverse=True)

    assigned_tickets_qs = Ticket.objects.filter(assigned_to=request.user)
    assigned_tickets = []
    for ticket in assigned_tickets_qs:
        if ticket.status == 'COMPLETED':
            if ticket.completed_at and ticket.completed_at > cutoff_time:
                assigned_tickets.append(ticket)
        else:
            assigned_tickets.append(ticket)
            
    assigned_tickets.sort(key=lambda x: x.created_at, reverse=True)

    is_admin = is_ticket_admin(request.user)
            
    return render(request, 'tickets/my_tickets.html', {
        'tickets': visible_tickets, 
        'assigned_tickets': assigned_tickets,
        'is_admin': is_admin
    })

@login_required
@check_tool_access('ticketing')
def ticket_detail(request, ticket_id):
    try:
        ticket = Ticket.objects.get(ticket_id=ticket_id)
    except Ticket.DoesNotExist:
        messages.error(request, "Ticket not found.")
        return redirect('my_tickets')
    
    is_owner = ticket.user == request.user
    is_assignee = ticket.assigned_to == request.user
    is_admin = is_ticket_admin(request.user)
    
    # --- Safety Mode: Approval Workflow ---
    is_approver = False
    requires_approval = False
    approval_pending = False
    
    if waffle.flag_is_active(request, 'ticket_approval_workflow'):
        is_approver = ticket.approver == request.user
        approval_pending = ticket.approval_status == 'PENDING'
        
    if not (is_owner or is_assignee or is_admin or is_approver):
        messages.error(request, "You do not have permission to view this ticket.")
        return redirect('my_tickets')
        
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # --- Safety Mode: Approval Actions ---
        if waffle.flag_is_active(request, 'ticket_approval_workflow'):
            if action == 'approve':
                if is_approver or is_admin:
                    ticket.approval_status = 'APPROVED'
                    ticket.save()
                    messages.success(request, "Ticket Approved. Assignee can now proceed.")
                    send_event_notification('TICKET_APPROVED', {'ticket': ticket}, functional_recipients=[ticket.user, ticket.assigned_to])
                else:
                    messages.error(request, "Permission denied.")
                return redirect('ticket_detail', ticket_id=ticket.ticket_id)
                
            elif action == 'reject':
                if is_approver or is_admin:
                    ticket.approval_status = 'REJECTED'
                    ticket.status = 'CANCELLED'
                    ticket.resolution = "Rejected by Approver"
                    ticket.save()
                    messages.warning(request, "Ticket Rejected and Cancelled.")
                    send_event_notification('TICKET_REJECTED', {'ticket': ticket}, functional_recipients=[ticket.user])
                else:
                    messages.error(request, "Permission denied.")
                return redirect('ticket_detail', ticket_id=ticket.ticket_id)
        # --------------------------------------
        
        if action == 'comment':
            text = request.POST.get('text')
            if text:
                from .models import TicketComment
                comment = TicketComment.objects.create(ticket=ticket, user=request.user, text=text)
                messages.success(request, "Comment added.")

                if waffle.flag_is_active(request, 'ticket_attachments'):
                    file = request.FILES.get('attachment')
                    if file:
                        if file.size > 10 * 1024 * 1024:
                            messages.warning(request, f'File {file.name} is too large (Max 10MB). Comment added without attachment.')
                        else:
                            TicketAttachment.objects.create(
                                ticket=ticket,
                                comment=comment,
                                file=file,
                                uploaded_by=request.user
                            )

                recipients = []
                if ticket.user != request.user: recipients.append(ticket.user)
                if ticket.assigned_to and ticket.assigned_to != request.user: recipients.append(ticket.assigned_to)
                send_event_notification('TICKET_COMMENTED', {'ticket': ticket, 'actor': request.user}, functional_recipients=recipients)
        
        elif action == 'status':
            if is_assignee or is_admin:
                new_status = request.POST.get('new_status')
                if new_status in dict(Ticket.STATUS_CHOICES):
                    if ticket.status != new_status:
                        ticket.status = new_status
                        ticket.save()
                        messages.success(request, f"Status updated to {ticket.get_status_display()}.")
                        
                        recipients = [u for u in [ticket.user, ticket.assigned_to] if u and u != request.user]
                        send_event_notification('TICKET_STATUS_CHANGED', {'ticket': ticket}, functional_recipients=recipients)
            else:
                 messages.error(request, "Permission denied to update status.")

        elif action == 'cancel':
            if ticket.status not in ['COMPLETED', 'CANCELLED']:
                ticket.status = 'CANCELLED'
                ticket.save()
                messages.success(request, "Ticket cancelled.")
                
                recipients = [u for u in [ticket.user, ticket.assigned_to] if u and u != request.user]
                send_event_notification('TICKET_STATUS_CHANGED', {'ticket': ticket}, functional_recipients=recipients)
            else:
                 messages.warning(request, "Ticket is already closed.")
                 
        return redirect('ticket_detail', ticket_id=ticket.ticket_id)

    comments = ticket.comments.all().order_by('created_at')
    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'comments': comments,
        'is_owner': is_owner,
        'is_assignee': is_assignee, 
        'is_admin': is_admin,
        'is_approver': is_approver,
        'approval_pending': approval_pending,
    })

@user_passes_test(is_ticket_admin)
def admin_ticket_panel(request):
    Group.objects.get_or_create(name='Ticket Admin')

    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    
    tickets = Ticket.objects.all().order_by('-created_at')
    
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    else:
        tickets = tickets.exclude(status='COMPLETED')
        
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
        
        try:
             ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
             messages.error(request, "Ticket not found or already deleted.")
             return redirect('admin_ticket_panel')
        
        status_changed = False
        if new_status and new_status != ticket.status:
            ticket.status = new_status
            status_changed = True
            
        resolution = request.POST.get('resolution')
        if resolution is not None:
             ticket.resolution = resolution

        assigned_to_id = request.POST.get('assigned_to')
        assignee_changed = False
        if assigned_to_id:
            if assigned_to_id == 'none':
                if ticket.assigned_to:
                    ticket.assigned_to = None
                    assignee_changed = True
            else:
                try:
                    new_assignee = User.objects.get(id=assigned_to_id)
                    if ticket.assigned_to != new_assignee:
                        ticket.assigned_to = new_assignee
                        assignee_changed = True
                except User.DoesNotExist:
                    pass
             
        ticket.save()
        
        if status_changed:
            recipients = [u for u in [ticket.user, ticket.assigned_to] if u and u != request.user]
            send_event_notification('TICKET_STATUS_CHANGED', {'ticket': ticket}, functional_recipients=recipients)
            
        if assignee_changed and ticket.assigned_to:
            recipients = [u for u in [ticket.user, ticket.assigned_to] if u and u != request.user]
            send_event_notification('TICKET_ASSIGNED', {'ticket': ticket}, functional_recipients=recipients)

        messages.success(request, f'Ticket {ticket.ticket_id} updated successfully.')
        return redirect('admin_ticket_panel')

    all_users = User.objects.all().order_by('username')
    all_users_for_access = User.objects.all().order_by('username')
    ticket_admin_group = Group.objects.get(name='Ticket Admin')
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

    all_users = User.objects.filter(
        Q(groups__name='Ticket Admin') | Q(groups__name='Ticket Support')
    ).distinct().order_by('username')

    return render(request, 'tickets/admin_panel_v6.html', {
        'tickets': tickets,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'is_filter_pending': status_filter == 'PENDING',
        'is_filter_in_progress': status_filter == 'IN_PROGRESS',
        'is_filter_completed': status_filter == 'COMPLETED',
        'is_filter_cancelled': status_filter == 'CANCELLED',
        'is_filter_deadline': priority_filter == 'DEADLINE',
        'is_filter_unassigned': assignee_filter == 'none',
        'is_filter_me': assignee_filter == 'me',
        'is_filter_active': not status_filter and not priority_filter and not assignee_filter,
        'assignee_filter': assignee_filter,
        'users': all_users,
        'users_with_access': users_with_access,
        'users_with_assignee_role': users_with_assignee_role,
        'now': timezone.now()
    })

@login_required
def delete_ticket(request, ticket_id):
    if not request.user.is_superuser:
        if not request.user.groups.filter(name='Ticket Admin').exists():
            messages.error(request, "Permission denied. Only admins can delete tickets.")
            return redirect('admin_ticket_panel')

    if request.method == 'POST':
        try:
            ticket = Ticket.objects.get(ticket_id=ticket_id)
        except Ticket.DoesNotExist:
            messages.error(request, "Ticket not found or already deleted.")
            return redirect('admin_ticket_panel')
            
        DeletedTicketLog.objects.create(ticket_id=ticket.ticket_id)
        
        ticket_id_str = ticket.ticket_id
        ticket.delete()
        messages.success(request, f"Ticket {ticket_id_str} deleted. ID queued for recycling.")
    
    return redirect('admin_ticket_panel')

@login_required
@check_tool_access('ticketing')
def ticket_history(request):
    tickets = Ticket.objects.filter(
        Q(status__in=['COMPLETED', 'CANCELLED']) &
        (Q(user=request.user) | Q(assigned_to=request.user))
    ).order_by('-updated_at')
    
    return render(request, 'tickets/ticket_history.html', {'tickets': tickets})

@user_passes_test(lambda u: u.is_superuser)
def manage_ticket_access(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        
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
        action = request.POST.get('action') 
        
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
        
    total_tickets = tickets.count()
    status_counts = tickets.values('status').annotate(count=Count('status'))
    priority_counts = tickets.values('priority').annotate(count=Count('priority'))

    status_dict = {item['status']: item['count'] for item in status_counts}
    priority_dict = {item['priority']: item['count'] for item in priority_counts}
    
    export_type = request.GET.get('export')
    if export_type == 'excel':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=ticket_report_{timezone.now().date()}.xlsx'
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Tickets"
        
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
        
        elements.append(Paragraph("Ticket Analytic Report", styles['Title']))
        elements.append(Paragraph(f"Date: {timezone.now().date()}", styles['Normal']))
        elements.append(Paragraph(f"Total Tickets: {total_tickets}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
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
        
        elements.append(Paragraph("Ticket Details:", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        ticket_data = [['ID', 'User', 'Status', 'Resolution']]
        for t in tickets:
            res = t.resolution if t.resolution else ""
            res_para = Paragraph(res, styles['BodyText'])
            ticket_data.append([t.ticket_id, t.user.username, t.status, res_para])
            
        t_tickets = Table(ticket_data, colWidths=[80, 80, 80, 300])
        t_tickets.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'), 
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

@user_passes_test(lambda u: u.is_superuser)
def reset_ticket_sequence(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        if not request.user.check_password(password):
            messages.error(request, "Incorrect password. Security check failed.")
            return redirect('admin_ticket_panel')
        
        try:
            Ticket.objects.all().delete()
            DeletedTicketLog.objects.all().delete()
            
            with connection.cursor() as cursor:
                try:
                    if connection.vendor == 'postgresql':
                        cursor.execute("ALTER SEQUENCE tickets_ticket_id_seq RESTART WITH 1;")
                    elif connection.vendor == 'sqlite':
                        cursor.execute("DELETE FROM sqlite_sequence WHERE name='tickets_ticket';")
                    elif 'postgres' in settings.DATABASES['default']['ENGINE']:
                         cursor.execute("ALTER SEQUENCE tickets_ticket_id_seq RESTART WITH 1;")
                except Exception as db_e:
                    # logger.error(f"Failed to reset sequence: {db_e}")
                    pass
            
            messages.success(request, "⚠️ SYSTEM RESET: All tickets wiped. Counter reset to PIXL00001.")
            
        except Exception as e:
            messages.error(request, f"Error during reset: {str(e)}")
            
    return redirect('admin_ticket_panel')
